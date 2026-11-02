"""Prepare all usable public ATNS rows for the ignored local Prez sandbox."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

from publication_filters import confidential_entity_ids, is_public
from resource_identity import (
    entity_iri,
    generated_resource_iri,
    legacy_entity_iri,
    load_entity_identity_mappings,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "build" / "csv"
SANDBOX_DIR = ROOT / "build" / "sandbox"
CSV_DIR = SANDBOX_DIR / "csv"
RDF_DIR = SANDBOX_DIR / "rdf"
REPORT_DIR = SANDBOX_DIR / "reports"
SAMPLE_REGISTRY = ROOT / "specs" / "public-sample-resources.csv"


def read_rows(table: str) -> tuple[list[str], list[dict[str, str]]]:
    with (SOURCE_DIR / f"{table}.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_rows(
    table: str, headers: list[str], rows: list[dict[str, str]]
) -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    with (CSV_DIR / f"{table}.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def existing_iris() -> dict[tuple[str, str], str]:
    with SAMPLE_REGISTRY.open(newline="", encoding="utf-8") as stream:
        return {
            (row["kind"], row["source_id"]): row["resource_iri"]
            for row in csv.DictReader(stream)
        }


def non_entity_iri(
    kind: str,
    source_id: str,
    overrides: dict[tuple[str, str], str],
) -> str:
    return overrides.get(
        (kind, source_id),
        generated_resource_iri(kind, source_id),
    )


def write_registry(
    entities: list[dict[str, str]],
    reference_ids: set[str],
    relationship_ids: set[str],
) -> None:
    overrides = existing_iris()
    mappings = load_entity_identity_mappings()
    rows = [
        {
            "kind": "entity",
            "source_id": row["EntityID"],
            "resource_iri": entity_iri(row["EntityID"], row["CategoryID"], mappings),
            "profile": "full",
        }
        for row in sorted(entities, key=lambda value: int(value["EntityID"]))
    ]
    rows.extend(
        {
            "kind": kind,
            "source_id": source_id,
            "resource_iri": non_entity_iri(kind, source_id, overrides),
            "profile": "full",
        }
        for kind, ids in (("reference", reference_ids), ("relationship", relationship_ids))
        for source_id in sorted(ids, key=int)
    )
    iris = [row["resource_iri"] for row in rows]
    if len(iris) != len(set(iris)):
        raise ValueError("Generated sandbox resource IRIs are not unique")
    with (SANDBOX_DIR / "resources.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["kind", "source_id", "resource_iri", "profile"],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_identity_reports(entities: list[dict[str, str]]) -> None:
    mappings = load_entity_identity_mappings()
    fields = [
        "source_id", "name", "category_id", "legacy_iri", "canonical_iri", "strategy"
    ]
    rows = []
    people = []
    for row in sorted(entities, key=lambda value: int(value["EntityID"])):
        source_id = row["EntityID"]
        canonical = entity_iri(source_id, row["CategoryID"], mappings)
        strategy = (
            "reviewed-external-identity"
            if source_id in mappings
            else "idn-organisation"
            if row["CategoryID"] == "3"
            else "generic-atns-resource"
        )
        report_row = {
            "source_id": source_id,
            "name": row["Name"],
            "category_id": row["CategoryID"],
            "legacy_iri": legacy_entity_iri(source_id),
            "canonical_iri": canonical,
            "strategy": strategy,
        }
        rows.append(report_row)
        if row["CategoryID"] == "6":
            people.append(report_row)
    for filename, values in (
        ("entity-identity-migration.csv", rows),
        ("people-identity-review.csv", people),
    ):
        with (REPORT_DIR / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(values)


def write_reports(
    counts: dict[str, int], omissions: list[dict[str, str]]
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with (REPORT_DIR / "publication-summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=["measure", "count"])
        writer.writeheader()
        for measure, count in counts.items():
            writer.writerow({"measure": measure, "count": count})
    with (REPORT_DIR / "omissions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["table", "source_id", "field", "value", "reason"],
        )
        writer.writeheader()
        writer.writerows(omissions)


def main() -> None:
    entity_headers, all_entities = read_rows("Entities")
    reference_headers, all_references = read_rows("Refs")
    relationship_headers, all_relationships = read_rows("Entity_Entity")
    _, all_additional = read_rows("Additional")

    confidential_ids = confidential_entity_ids(all_additional)
    confidential_public_entities = [
        row
        for row in all_entities
        if is_public(row) and row["EntityID"] in confidential_ids
    ]

    public_entities = [
        row
        for row in all_entities
        if is_public(row) and row["EntityID"] not in confidential_ids
    ]
    entities = [row for row in public_entities if row["Name"].strip()]
    entity_ids = {row["EntityID"] for row in entities}

    public_references = [row for row in all_references if is_public(row)]
    references = [row for row in public_references if row["Title"].strip()]
    reference_ids = {row["RefID"] for row in references}

    relationships = [
        row
        for row in all_relationships
        if row["EntityID"] in entity_ids
        and row["RelatedEntityID"] in entity_ids
    ]
    relationship_ids = {row["Entity_EntityID"] for row in relationships}

    table_filters = {
        "Entities": (entity_headers, entities),
        "Refs": (reference_headers, references),
        "Entity_Entity": (relationship_headers, relationships),
    }
    for table, predicate in {
        "Entity_Refs": lambda row: row["EntityID"] in entity_ids
        and row["RefID"] in reference_ids,
        "Entity_SubCategory": lambda row: row["EntityID"] in entity_ids,
        "Entity_SubjectMatter": lambda row: row["EntityID"] in entity_ids,
    }.items():
        headers, rows = read_rows(table)
        table_filters[table] = (headers, [row for row in rows if predicate(row)])

    for table, (headers, rows) in table_filters.items():
        write_rows(table, headers, rows)

    write_registry(entities, reference_ids, relationship_ids)
    write_identity_reports(entities)

    omissions = [
        *(
            {
                "table": "Entities",
                "source_id": row["EntityID"],
                "field": "Additional.Confidential",
                "value": "1",
                "reason": "parent entity withheld pending source-owner clarification",
            }
            for row in confidential_public_entities
        ),
        *(
            {
                "table": "Entities",
                "source_id": row["EntityID"],
                "field": "Name",
                "value": "",
                "reason": "public row has no displayable name",
            }
            for row in public_entities
            if not row["Name"].strip()
        ),
        *(
            {
                "table": "Refs",
                "source_id": row["RefID"],
                "field": "Title",
                "value": "",
                "reason": "public row has no displayable title",
            }
            for row in public_references
            if not row["Title"].strip()
        ),
    ]
    for table, id_field, field, missing_value in (
        ("Refs", "RefID", "TypeID", "182"),
        ("Entity_Entity", "Entity_EntityID", "RelationshipTypeID", "0"),
        ("Entity_SubCategory", "Entity_SubCategoryID", "SubCategoryID", "326"),
    ):
        rows = table_filters[table][1]
        omissions.extend(
            {
                "table": table,
                "source_id": row[id_field],
                "field": field,
                "value": missing_value,
                "reason": "source lookup entry has no label; classification omitted",
            }
            for row in rows
            if row[field].strip() == missing_value
        )

    for table, id_field in (("Entities", "EntityID"), ("Refs", "RefID")):
        rows = table_filters[table][1]
        omissions.extend(
            {
                "table": table,
                "source_id": row[id_field],
                "field": "URL",
                "value": row["URL"],
                "reason": "not a complete HTTP(S) URI; schema:url omitted",
            }
            for row in rows
            if row["URL"].strip()
            and not re.fullmatch(r"https?://\S+", row["URL"].strip())
        )

    counts = {
        "source entities": len(all_entities),
        "confidential-linked public entities withheld": len(
            confidential_public_entities
        ),
        "public non-deleted entities": len(public_entities),
        "published named entities": len(entities),
        "source references": len(all_references),
        "public non-deleted references": len(public_references),
        "published titled references": len(references),
        "published relationships": len(relationships),
        "published entity-reference links": len(table_filters["Entity_Refs"][1]),
        "reported omissions": len(omissions),
    }
    write_reports(counts, omissions)

    RDF_DIR.mkdir(parents=True, exist_ok=True)
    for old_output in RDF_DIR.glob("*.ttl"):
        old_output.unlink()
    print("Prepared the public ATNS sandbox:")
    for measure, count in counts.items():
        print(f"  {measure}: {count:,}")
    print(f"  reports: {REPORT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
