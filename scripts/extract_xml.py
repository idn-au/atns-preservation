"""Extract selected ATNS XML tables to normalized, ignored CSV files.

This stage deliberately knows nothing about RDF. It verifies the private source
files against the tracked manifest, preserves every source column, and creates
tabular inputs for the declarative rdfcon specifications.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import yaml
from lxml import etree


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "specs" / "source-manifest.yaml"
SOURCE_DIR = ROOT / "raw" / "xml" / "ATNS_XML_05Apr22"
OUTPUT_DIR = ROOT / "build" / "csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def columns_sha256(headers: list[str]) -> str:
    return hashlib.sha256(("\n".join(headers) + "\n").encode("utf-8")).hexdigest()


def extract_table(
    table: str,
    details: dict,
    update_manifest: bool,
) -> tuple[int, str, str, Path]:
    source = SOURCE_DIR / f"{table}.xml"
    if not source.exists():
        raise FileNotFoundError(
            f"Private source table is missing: {source.relative_to(ROOT)}"
        )

    actual_sha256 = sha256(source)
    if not update_manifest and actual_sha256 != details["sha256"]:
        raise ValueError(
            f"Checksum mismatch for {source.relative_to(ROOT)}: "
            f"expected {details['sha256']}, got {actual_sha256}. "
            "Review the replacement export, then run 'task accept-source'."
        )

    rows: list[dict[str, str]] = []
    headers: list[str] = []
    known_headers: set[str] = set()
    parser = etree.iterparse(
        str(source),
        events=("end",),
        tag=table,
        recover=True,
        huge_tree=True,
        encoding="utf-8",
    )
    for _, element in parser:
        parent = element.getparent()
        if parent is None or local_name(parent.tag) != "dataroot":
            continue
        row: dict[str, str] = {}
        for child in element:
            field = local_name(child.tag)
            if field not in known_headers:
                known_headers.add(field)
                headers.append(field)
            row[field] = (child.text or "").strip()
        rows.append(row)
        element.clear()
        while element.getprevious() is not None:
            del parent[0]

    primary_key = details["primary_key"]
    if primary_key not in headers:
        raise ValueError(f"{table} does not contain primary key {primary_key}")
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(primary_key, "").strip()
        if not value:
            raise ValueError(f"{table} contains a blank {primary_key}")
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        examples = ", ".join(sorted(duplicates)[:10])
        raise ValueError(
            f"{table} contains {len(duplicates)} duplicate {primary_key} values: "
            f"{examples}"
        )

    actual_columns_sha256 = columns_sha256(headers)
    expected_columns_sha256 = details.get("columns_sha256")
    if expected_columns_sha256 and actual_columns_sha256 != expected_columns_sha256:
        raise ValueError(
            f"Column structure changed for {table}: expected "
            f"{expected_columns_sha256}, got {actual_columns_sha256}. "
            "A schema change requires a deliberate mapping review."
        )
    if not update_manifest and len(rows) != details["row_count"]:
        raise ValueError(
            f"Row count changed for {table}: expected {details['row_count']}, "
            f"got {len(rows)}. Review the replacement export, then run "
            "'task accept-source'."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{table}.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), actual_sha256, actual_columns_sha256, output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="accept a reviewed row-only source update by recording its checksums and counts",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    for table, details in manifest["tables"].items():
        count, actual_sha256, actual_columns_sha256, output = extract_table(
            table, details, args.update_manifest
        )
        if args.update_manifest:
            details["sha256"] = actual_sha256
            details["row_count"] = count
            details["columns_sha256"] = actual_columns_sha256
        print(f"{table}: {count:,} rows -> {output.relative_to(ROOT)}")
    if args.update_manifest:
        MANIFEST_PATH.write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )
        print(f"Updated {MANIFEST_PATH.relative_to(ROOT)} for review")


if __name__ == "__main__":
    main()
