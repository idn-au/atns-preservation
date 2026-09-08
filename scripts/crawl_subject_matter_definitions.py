"""Recover ATNS subject-matter definitions from pinned Wayback captures."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports" / "subject-matter.tsv"
OUTPUT = ROOT / "specs" / "subject-matter-definitions.tsv"
CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
REPLAY_ROOT = "https://web.archive.org/web"
TARGET_TIMESTAMP = "20110216000000"
USER_AGENT = "atns-preservation/1.0 (archival vocabulary recovery)"
MIN_REQUEST_INTERVAL = 0.75
REQUEST_LOCK = threading.Lock()
LAST_REQUEST_AT = 0.0

ID_PATTERN = re.compile(r"[?&]subjectmatterid=(\d+)", re.IGNORECASE)
PAGE_PATTERN = re.compile(
    r"class\s*=\s*[\"']?heading[\"']?[^>]*>(.*?)</td>.*?"
    r"<b[^>]*>(.*?)</b>",
    re.IGNORECASE | re.DOTALL,
)
TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class Subject:
    iri: str
    label: str
    notation: str


@dataclass(frozen=True)
class Capture:
    timestamp: str
    original: str
    digest: str

    @property
    def raw_url(self) -> str:
        return f"{REPLAY_ROOT}/{self.timestamp}id_/{self.original}"

    @property
    def source_url(self) -> str:
        return f"{REPLAY_ROOT}/{self.timestamp}/{self.original}"


def fetch(url: str, *, attempts: int = 4) -> bytes:
    global LAST_REQUEST_AT
    for attempt in range(attempts):
        try:
            with REQUEST_LOCK:
                delay = MIN_REQUEST_INTERVAL - (time.monotonic() - LAST_REQUEST_AT)
                if delay > 0:
                    time.sleep(delay)
                request = Request(url, headers={"User-Agent": USER_AGENT})
                with urlopen(request, timeout=45) as response:
                    content = response.read()
                LAST_REQUEST_AT = time.monotonic()
            return content
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def load_subjects(path: Path) -> list[Subject]:
    subjects: list[Subject] = []
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.reader(source, delimiter="\t"):
            if len(row) != 3:
                raise SystemExit(f"Unexpected subject-matter row: {row!r}")
            compact_iri, label, notation = row
            subjects.append(
                Subject(
                    iri=compact_iri.replace(
                        "atns-sub:", "https://data.idnau.org/pid/vocab/atns-sub/", 1
                    ),
                    label=label,
                    notation=notation,
                )
            )
    return subjects


def load_captures() -> dict[str, list[Capture]]:
    query = urlencode(
        {
            "url": "atns.net.au/subjectmatter.asp?SubjectmatterID=*",
            "output": "json",
            "filter": ["statuscode:200", "mimetype:text/html"],
            "fl": "timestamp,original,statuscode,digest",
            "collapse": "digest",
        },
        doseq=True,
    )
    payload = json.loads(fetch(f"{CDX_ENDPOINT}?{query}"))
    if not payload or payload[0] != ["timestamp", "original", "statuscode", "digest"]:
        raise SystemExit("Unexpected Wayback CDX response")

    captures: dict[str, list[Capture]] = {}
    for timestamp, original, _status, digest in payload[1:]:
        match = ID_PATTERN.search(original)
        if match:
            captures.setdefault(match.group(1), []).append(
                Capture(timestamp=timestamp, original=original, digest=digest)
            )
    for values in captures.values():
        values.sort(key=lambda capture: capture.timestamp)
    return captures


def clean_fragment(fragment: str) -> str:
    return " ".join(html.unescape(TAG_PATTERN.sub(" ", fragment)).split())


def extract_page(capture: Capture) -> tuple[str, str]:
    content = fetch(capture.raw_url).decode("windows-1252", errors="replace")
    match = PAGE_PATTERN.search(content)
    if not match:
        raise ValueError("heading and definition pattern not found")
    return clean_fragment(match.group(1)), clean_fragment(match.group(2))


def capture_distance(capture: Capture) -> float:
    target = datetime.strptime(TARGET_TIMESTAMP, "%Y%m%d%H%M%S")
    captured = datetime.strptime(capture.timestamp, "%Y%m%d%H%M%S")
    return abs((captured - target).total_seconds())


def sample_captures(captures: list[Capture]) -> list[Capture]:
    if not captures:
        return []
    selected = [captures[0], min(captures, key=capture_distance), captures[-1]]
    return list({capture.timestamp + capture.original: capture for capture in selected}.values())


def recover_subject(
    subject: Subject, captures: list[Capture]
) -> dict[str, str | int]:
    sampled = sample_captures(captures)
    recovered: list[tuple[Capture, str, str]] = []
    errors: list[str] = []
    for capture in sampled:
        try:
            heading, definition = extract_page(capture)
            recovered.append((capture, heading, definition))
        except Exception as error:
            errors.append(f"{capture.timestamp}: {type(error).__name__}: {error}")

    matching = [item for item in recovered if item[1].casefold() == subject.label.casefold()]
    chosen_pool = matching or recovered
    chosen = max(chosen_pool, key=lambda item: item[0].timestamp) if chosen_pool else None
    definitions = {definition for _capture, _heading, definition in recovered}
    headings = {heading for _capture, heading, _definition in recovered}

    if not captures:
        status = "missing-capture"
    elif not recovered:
        status = "extraction-failed"
    elif not matching:
        status = "heading-mismatch"
    elif chosen and not chosen[2]:
        status = "empty-definition"
    elif len(definitions) > 1:
        status = "definition-changed"
    elif len(recovered) == 1:
        status = "single-sample"
    else:
        status = "stable"

    capture, heading, definition = chosen if chosen else (None, "", "")
    review_note = ""
    if status != "stable":
        review_note = " || ".join(
            f"{item_capture.timestamp}: {item_heading} — {item_definition or '[empty]'}"
            for item_capture, item_heading, item_definition in sorted(
                recovered, key=lambda item: item[0].timestamp
            )
        )
    return {
        "concept_iri": subject.iri,
        "notation": subject.notation,
        "pref_label": subject.label,
        "definition": definition,
        "capture_timestamp": capture.timestamp if capture else "",
        "source_url": capture.source_url if capture else "",
        "capture_count": len(captures),
        "sampled_capture_count": len(recovered),
        "distinct_sampled_definitions": len(definitions),
        "review_status": status,
        "review_note": review_note,
        "sampled_headings": " | ".join(sorted(headings)),
        "errors": " | ".join(errors),
    }


def write_rows(path: Path, rows: list[dict[str, str | int]]) -> None:
    fieldnames = [
        "concept_iri",
        "notation",
        "pref_label",
        "definition",
        "capture_timestamp",
        "source_url",
        "capture_count",
        "sampled_capture_count",
        "distinct_sampled_definitions",
        "review_status",
        "review_note",
        "sampled_headings",
        "errors",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(
            destination,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)


def load_existing_rows(path: Path) -> dict[str, dict[str, str | int]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as source:
        return {
            row["notation"]: dict(row)
            for row in csv.DictReader(source, delimiter="\t")
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--retry-unresolved",
        action="store_true",
        help="Retry every non-stable row in the existing output",
    )
    args = parser.parse_args()

    subjects = load_subjects(args.manifest)
    captures = load_captures()
    rows_by_notation = load_existing_rows(args.output) if args.retry_unresolved else {}
    if args.retry_unresolved:
        retry_statuses = {
            "definition-changed",
            "empty-definition",
            "extraction-failed",
            "heading-mismatch",
            "missing-capture",
            "single-sample",
        }
        subjects_to_crawl = [
            subject
            for subject in subjects
            if subject.notation not in rows_by_notation
            or str(rows_by_notation[subject.notation].get("review_status", ""))
            in retry_statuses
        ]
    else:
        subjects_to_crawl = subjects
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(recover_subject, subject, captures.get(subject.notation, [])): subject
            for subject in subjects_to_crawl
        }
        for future in as_completed(futures):
            subject = futures[future]
            rows_by_notation[subject.notation] = future.result()
            print(
                f"{subject.notation}: "
                f"{rows_by_notation[subject.notation]['review_status']}",
                flush=True,
            )

    rows = [rows_by_notation[subject.notation] for subject in subjects]
    write_rows(args.output, rows)
    statuses: dict[str, int] = {}
    for row in rows:
        status = str(row["review_status"])
        statuses[status] = statuses.get(status, 0) + 1
    print(f"Wrote {len(rows)} definitions to {args.output.relative_to(ROOT)}")
    print("Review statuses: " + ", ".join(f"{key}={value}" for key, value in sorted(statuses.items())))


if __name__ == "__main__":
    main()
