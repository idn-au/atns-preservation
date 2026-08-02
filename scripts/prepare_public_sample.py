"""Select declared public sample rows from normalized ATNS CSV tables."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "build" / "csv"
OUTPUT_DIR = ROOT / "build" / "sample"
REPORT_DIR = ROOT / "build" / "reports"
SELECTION = ROOT / "specs" / "public-sample-resources.csv"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_selected(
    table: str,
    predicate,
) -> int:
    headers, rows = read_rows(SOURCE_DIR / f"{table}.csv")
    selected = [row for row in rows if predicate(row)]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / f"{table}.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(selected)
    return len(selected)


def validate_selection(selection_rows: list[dict[str, str]]) -> None:
    identities: set[tuple[str, str]] = set()
    iris: set[str] = set()
    for row in selection_rows:
        identity = (row["kind"].strip(), row["source_id"].strip())
        iri = row["resource_iri"].strip()
        if identity in identities:
            raise ValueError(f"Duplicate public sample source identity: {identity}")
        if iri in iris:
            raise ValueError(f"Duplicate public sample resource IRI: {iri}")
        if identity[0] not in {"entity", "reference", "relationship"}:
            raise ValueError(f"Unrecognized public sample resource kind: {identity[0]}")
        if row["profile"] not in {"full", "supporting"}:
            raise ValueError(
                f"Unrecognized profile for {identity}: {row['profile']}"
            )
        if not iri.startswith(("http://", "https://")):
            raise ValueError(f"Published resource IRI is not HTTP(S): {iri}")
        identities.add(identity)
        iris.add(iri)


def indexed_source(table: str, key: str) -> dict[str, dict[str, str]]:
    _, rows = read_rows(SOURCE_DIR / f"{table}.csv")
    return {row[key]: row for row in rows}


def removal_candidates(
    selection_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    tables = {
        "entity": (indexed_source("Entities", "EntityID"), "Deleted", "Public"),
        "reference": (indexed_source("Refs", "RefID"), "Deleted", "Public"),
        "relationship": (
            indexed_source("Entity_Entity", "Entity_EntityID"),
            None,
            None,
        ),
    }
    candidates: list[dict[str, str]] = []
    reasons: dict[tuple[str, str], str] = {}
    selection = {
        (row["kind"], row["source_id"]): row for row in selection_rows
    }

    for identity, selected in selection.items():
        kind, source_id = identity
        source_rows, deleted_field, public_field = tables[kind]
        source = source_rows.get(source_id)
        reason = ""
        if source is None:
            reason = "missing-from-source"
        elif deleted_field and source[deleted_field].strip() != "0":
            reason = "source-deleted"
        elif public_field and source[public_field].strip() != "1":
            reason = "no-longer-public"
        if reason:
            reasons[identity] = reason
            candidates.append(
                {
                    "action": "remove",
                    "kind": kind,
                    "source_id": source_id,
                    "resource_iri": selected["resource_iri"],
                    "reason": reason,
                }
            )

    removed_entity_ids = {
        source_id
        for (kind, source_id), _ in reasons.items()
        if kind == "entity"
    }
    relationship_rows = tables["relationship"][0]
    selected_entity_ids = {
        source_id for kind, source_id in selection if kind == "entity"
    }
    for identity, selected in selection.items():
        kind, source_id = identity
        if kind != "relationship" or identity in reasons:
            continue
        relationship = relationship_rows[source_id]
        endpoints = {
            relationship["EntityID"], relationship["RelatedEntityID"]
        }
        unpublished_endpoints = endpoints - selected_entity_ids
        if unpublished_endpoints:
            raise ValueError(
                f"Published relationship {source_id} has unpublished entity endpoints: "
                + ", ".join(sorted(unpublished_endpoints))
            )
        if endpoints & removed_entity_ids:
            candidates.append(
                {
                    "action": "remove",
                    "kind": kind,
                    "source_id": source_id,
                    "resource_iri": selected["resource_iri"],
                    "reason": "references-removal-candidate",
                }
            )

    return sorted(
        candidates,
        key=lambda row: (row["kind"], int(row["source_id"])),
    )


def write_removal_report(candidates: list[dict[str, str]]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / "removal-candidates.csv"
    headers = ["action", "kind", "source_id", "resource_iri", "reason"]
    with report.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(candidates)
    return report


def main() -> None:
    _, selection_rows = read_rows(SELECTION)
    validate_selection(selection_rows)
    candidates = removal_candidates(selection_rows)
    report = write_removal_report(candidates)
    if candidates:
        raise SystemExit(
            f"Found {len(candidates)} published resources requiring removal review. "
            f"See {report.relative_to(ROOT)}; no RDF was generated."
        )
    print(f"Removal review: 0 candidates -> {report.relative_to(ROOT)}")

    rdf_output = ROOT / "build" / "rdf"
    rdf_output.mkdir(parents=True, exist_ok=True)
    for old_output in rdf_output.glob("*.ttl"):
        old_output.unlink()
    ids = {
        kind: {
            row["source_id"] for row in selection_rows if row["kind"] == kind
        }
        for kind in ("entity", "reference", "relationship")
    }

    predicates = {
        "Entities": lambda row: row["EntityID"] in ids["entity"],
        "Refs": lambda row: row["RefID"] in ids["reference"],
        "Entity_Entity": lambda row: row["Entity_EntityID"]
        in ids["relationship"],
        "Entity_Refs": lambda row: row["EntityID"] in ids["entity"]
        and row["RefID"] in ids["reference"],
        "Entity_SubCategory": lambda row: row["EntityID"] in ids["entity"],
        "Entity_SubjectMatter": lambda row: row["EntityID"] in ids["entity"],
    }
    for table, predicate in predicates.items():
        count = write_selected(table, predicate)
        print(f"{table}: selected {count:,} rows")


if __name__ == "__main__":
    main()
