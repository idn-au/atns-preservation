"""Audit schema:url targets in generated ATNS entities and references."""

from __future__ import annotations

import csv
import socket
import ssl
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

from rdflib import Graph, URIRef


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
SCHEMA_URL = URIRef("https://schema.org/url")
SCHEMA_NAME = URIRef("https://schema.org/name")
USER_AGENT = "atns-preservation-link-audit/1.0"
TIMEOUT_SECONDS = 6
WORKERS = 64
PER_DOMAIN = 12
DOMAIN_LOCKS: defaultdict[str, threading.BoundedSemaphore] = defaultdict(
    lambda: threading.BoundedSemaphore(PER_DOMAIN)
)


@dataclass(frozen=True)
class Target:
    resource_iri: str
    resource_name: str
    original_url: str


def normalised_host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host.removeprefix("www.")


def unverified_candidate(original_url: str) -> tuple[str, str]:
    """Return a deterministic replacement candidate that still needs browser validation."""
    parsed = urlparse(original_url)
    if normalised_host(original_url) == "nntt.gov.au":
        path = parsed.path.lower()
        if path.endswith("/ilua_details.aspx"):
            register = "indigenous-land-use-agreements"
        elif path.endswith(("/nntr_details.aspx", "/determination_details.aspx")):
            register = "native-title-register"
        else:
            return "", ""
        file_numbers = parse_qs(parsed.query).get("NNTT_Fileno", [])
        if len(file_numbers) == 1 and file_numbers[0]:
            encoded = quote(file_numbers[0], safe="")
            return (
                f"https://www.nntt.gov.au/search-the-registers/{register}#/{encoded}",
                "candidate_unverified",
            )
    return "", ""


def classify_status(status: int, content_length: str) -> tuple[str, str]:
    if status == 204 or content_length == "0":
        return "no_content", "confirmed_broken"
    if 200 <= status < 300:
        return "ok", "working"
    if status in {404, 410}:
        return "not_found", "confirmed_broken"
    if status in {401, 403, 429}:
        return "access_restricted", "review_required"
    if 400 <= status < 500:
        return "client_error", "likely_broken"
    if 500 <= status < 600:
        return "server_error", "review_required"
    return "unexpected_status", "review_required"


def refine_redirect(classification: str, assessment: str, original_url: str, final_url: str) -> tuple[str, str]:
    if assessment != "working" or final_url == original_url:
        return classification, assessment
    original_path = urlparse(original_url).path.rstrip("/")
    final_path = urlparse(final_url).path.rstrip("/")
    final_lower = final_path.lower()
    if any(marker in final_lower for marker in ("/404", "404-not-found", "/errors/404", "/not-found")):
        return "soft_404", "confirmed_broken"
    generic_source = original_path.lower() in {"", "/index.htm", "/index.html", "/default.htm", "/default.html"}
    if original_path and not generic_source and not final_path:
        return "redirect_to_home", "review_required"
    return classification, assessment


def audit(target: Target) -> dict[str, str]:
    parsed = urlparse(target.original_url)
    candidate_url, candidate_status = unverified_candidate(target.original_url)
    base = {
        "resource_iri": target.resource_iri,
        "resource_name": target.resource_name,
        "original_url": target.original_url,
        "original_domain": normalised_host(target.original_url),
        "last_url_reached": "",
        "last_domain_reached": "",
        "possible_updated_url": "",
        "candidate_url": candidate_url,
        "candidate_status": candidate_status,
        "http_status": "",
        "classification": "",
        "assessment": "confirmed_broken",
        "broken": "true",
        "same_domain_redirect": "false",
        "path_changed": "false",
        "content_type": "",
        "content_length": "",
        "error": "",
    }
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return {**base, "classification": "invalid_url", "error": "Expected an HTTP(S) URL"}

    request = Request(
        target.original_url,
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
        method="GET",
    )
    try:
        with DOMAIN_LOCKS[parsed.hostname.lower()]:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                response.read(1)
                status = response.status
                final_url = response.geturl()
                content_length = response.headers.get("Content-Length", "")
                classification, assessment = classify_status(status, content_length)
                classification, assessment = refine_redirect(classification, assessment, target.original_url, final_url)
                final_parsed = urlparse(final_url)
                return {
                    **base,
                    "last_url_reached": final_url,
                    "last_domain_reached": normalised_host(final_url),
                    "possible_updated_url": (
                        final_url
                        if assessment == "working"
                        and final_url != target.original_url
                        and normalised_host(final_url) == normalised_host(target.original_url)
                        and final_parsed.path != parsed.path
                        else ""
                    ),
                    "http_status": str(status),
                    "classification": classification,
                    "assessment": assessment,
                    "broken": str(assessment in {"confirmed_broken", "likely_broken"}).lower(),
                    "same_domain_redirect": str(
                        final_url != target.original_url
                        and normalised_host(final_url) == normalised_host(target.original_url)
                    ).lower(),
                    "path_changed": str(
                        final_url != target.original_url
                        and final_parsed.path != parsed.path
                    ).lower(),
                    "content_type": response.headers.get("Content-Type", ""),
                    "content_length": content_length,
                }
    except HTTPError as error:
        final_url = error.geturl()
        classification, assessment = classify_status(error.code, error.headers.get("Content-Length", ""))
        return {
            **base,
            "last_url_reached": final_url,
            "last_domain_reached": normalised_host(final_url),
            "http_status": str(error.code),
            "classification": classification,
            "assessment": assessment,
            "broken": str(assessment in {"confirmed_broken", "likely_broken"}).lower(),
            "content_type": error.headers.get("Content-Type", ""),
            "content_length": error.headers.get("Content-Length", ""),
            "error": str(error.reason),
        }
    except (TimeoutError, socket.timeout) as error:
        return {**base, "classification": "timeout", "assessment": "review_required", "broken": "false", "error": str(error)}
    except ssl.SSLError as error:
        return {**base, "classification": "tls_error", "assessment": "likely_broken", "error": str(error)}
    except URLError as error:
        reason = error.reason
        if isinstance(reason, socket.gaierror):
            classification = "dns_error"
        elif isinstance(reason, ssl.SSLError):
            classification = "tls_error"
        elif isinstance(reason, (TimeoutError, socket.timeout)):
            classification = "timeout"
        else:
            classification = "connection_error"
        assessment = "likely_broken" if classification in {"dns_error", "tls_error"} else "review_required"
        return {**base, "classification": classification, "assessment": assessment, "broken": str(assessment == "likely_broken").lower(), "error": str(reason)}
    except Exception as error:
        return {**base, "classification": "request_error", "assessment": "review_required", "broken": "false", "error": repr(error)}


def targets(path: Path) -> list[Target]:
    graph = Graph().parse(path)
    values: list[Target] = []
    for subject, url in graph.subject_objects(SCHEMA_URL):
        name = next((str(value) for value in graph.objects(subject, SCHEMA_NAME)), "")
        values.append(Target(str(subject), name, str(url)))
    return sorted(values, key=lambda item: (item.original_url, item.resource_iri))


FIELDS = [
    "resource_iri", "resource_name", "original_url", "last_url_reached",
    "possible_updated_url", "candidate_url", "candidate_status", "http_status", "classification", "assessment", "broken", "same_domain_redirect",
    "path_changed", "content_type", "content_length", "error",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |" for row in rows)
    return "\n".join(lines)


def write_summary(groups: list[tuple[str, list[dict[str, str]], str]]) -> None:
    checked = datetime.now(UTC).isoformat(timespec="seconds")
    sections = [
        "# ATNS `schema:url` link audit",
        "",
        f"Checked: `{checked}`",
        "",
        "`last_url_reached` records where redirect handling ended; it is diagnostic evidence, not a recommended replacement. `possible_updated_url` is populated only when a same-domain changed path returned usable content. `candidate_url` records a predictable mapping that has not been validated inside the destination browser application; these rows have `candidate_status` `candidate_unverified`. `assessment` describes the original URL check and is independent of candidate status. Access restrictions, timeouts and server errors are not automatically called broken. HTTP 204, explicit zero-length responses, 404/410, invalid URLs and detected soft-404 pages are confirmed broken.",
    ]
    for title, rows, csv_name in groups:
        counts = Counter(row["classification"] for row in rows)
        assessment_counts = Counter(row["assessment"] for row in rows)
        broken = [row for row in rows if row["broken"] == "true"]
        sections.extend([
            "", f"## {title}", "",
            f"Full table: `{csv_name}` ({len(rows):,} URL assertions; {len(broken):,} confirmed or likely broken).", "",
            markdown_table(
                ["Assessment", "Count"],
                [[key, f"{value:,}"] for key, value in sorted(assessment_counts.items(), key=lambda item: (-item[1], item[0]))],
            ),
            "",
            markdown_table(
                ["Classification", "Count"],
                [[key, f"{value:,}"] for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))],
            ),
        ])
        domain_counts = Counter(row["original_domain"] for row in broken)
        sections.extend([
            "", "### Most common broken domains", "",
            markdown_table(
                ["Domain", "Broken URLs"],
                [[domain or "(invalid)", f"{count:,}"] for domain, count in domain_counts.most_common(15)],
            ),
        ])
        repairable = [
            row for row in rows
            if row["broken"] == "false" and row["same_domain_redirect"] == "true" and row["path_changed"] == "true"
        ]
        pattern_counts = Counter((row["original_domain"], urlparse(row["original_url"]).path, urlparse(row["last_url_reached"]).path) for row in repairable)
        sections.extend([
            "", "### Observed same-domain path migrations", "",
            markdown_table(
                ["Domain", "Original path", "Final path", "Examples"],
                [[domain, old or "/", new or "/", str(count)] for (domain, old, new), count in pattern_counts.most_common(15)],
            ) if pattern_counts else "No successful same-domain path migrations were observed.",
        ])
        candidates = [row for row in rows if row.get("candidate_status") == "candidate_unverified"]
        sections.extend([
            "", "### Unverified candidate URLs", "",
            f"{len(candidates):,} deterministic candidate mappings were generated. They require browser-level validation before the source RDF is changed.", "",
            markdown_table(
                ["Resource", "Name", "Original URL", "Candidate URL", "Status"],
                [[row["resource_iri"], row["resource_name"], row["original_url"], row["candidate_url"], row["candidate_status"]] for row in candidates],
            ) if candidates else "No deterministic candidate mappings were generated.",
        ])
    (REPORT_DIR / "broken-link-report.md").write_text("\n".join(sections) + "\n", encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    inputs = [
        ("Entity URLs", ROOT / "build" / "sandbox" / "rdf" / "Entities-1.ttl", "entity-url-audit.csv"),
        ("Reference URLs", ROOT / "build" / "sandbox" / "rdf" / "Refs-1.ttl", "reference-url-audit.csv"),
    ]
    groups: list[tuple[str, list[dict[str, str]], str]] = []
    for title, source, csv_name in inputs:
        source_targets = targets(source)
        print(f"Checking {len(source_targets):,} {title.lower()}...", flush=True)
        rows: list[dict[str, str]] = []
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = [executor.submit(audit, target) for target in source_targets]
            for index, future in enumerate(as_completed(futures), start=1):
                rows.append(future.result())
                if index % 250 == 0 or index == len(futures):
                    print(f"  {index:,}/{len(futures):,}", flush=True)
        rows.sort(key=lambda row: (row["broken"] != "true", row["classification"], row["original_domain"], row["original_url"], row["resource_iri"]))
        write_csv(REPORT_DIR / csv_name, rows)
        groups.append((title, rows, csv_name))
    write_summary(groups)
    print(f"Wrote link audit reports to {REPORT_DIR.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
