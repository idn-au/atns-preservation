"""Authoritative public-IRI rules for ATNS source records.

The UUID component is derived from the preserved source identity and does not
change when an organisation moves from the generic resource namespace to the
agent-specific organisation namespace. Reviewed external identities override
the generated IDN IRI.
"""

from __future__ import annotations

import csv
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESOURCE_BASE = "https://data.idnau.org/pid/resource/"
ORGANIZATION_BASE = "https://data.idnau.org/pid/org/"
ORGANIZATION_CATEGORY = "3"
IDENTITY_MAPPINGS = ROOT / "specs" / "entity-identity-mappings.csv"
LEGACY_ENTITY_IRIS = ROOT / "specs" / "legacy-entity-iris.csv"
PUBLIC_SAMPLE_RESOURCES = ROOT / "specs" / "public-sample-resources.csv"
UUID_NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://data.idnau.org/pid/resource/atns-preservation/source-identity",
)


def generated_uuid(kind: str, source_id: str) -> uuid.UUID:
    return uuid.uuid5(UUID_NAMESPACE, f"{kind}:{source_id.strip()}")


def generated_resource_iri(kind: str, source_id: str) -> str:
    return f"{RESOURCE_BASE}{generated_uuid(kind, source_id)}"


def load_entity_identity_mappings(
    path: Path = IDENTITY_MAPPINGS,
) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    mappings = {row["source_id"].strip(): row["canonical_iri"].strip() for row in rows}
    if "" in mappings or any(not iri.startswith(("http://", "https://")) for iri in mappings.values()):
        raise ValueError(f"Invalid canonical identity mapping in {path}")
    return mappings


def load_established_entity_iris(
    path: Path = PUBLIC_SAMPLE_RESOURCES,
) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            row["source_id"].strip(): row["resource_iri"].strip()
            for row in csv.DictReader(stream)
            if row["kind"].strip() == "entity"
        }


def entity_iri(
    source_id: str,
    category_id: str,
    mappings: dict[str, str] | None = None,
    established_iris: dict[str, str] | None = None,
) -> str:
    source_id = source_id.strip()
    mappings = load_entity_identity_mappings() if mappings is None else mappings
    if source_id in mappings:
        return mappings[source_id]
    established_iris = (
        load_established_entity_iris()
        if established_iris is None
        else established_iris
    )
    if category_id.strip() != ORGANIZATION_CATEGORY and source_id in established_iris:
        return established_iris[source_id]
    base = ORGANIZATION_BASE if category_id.strip() == ORGANIZATION_CATEGORY else RESOURCE_BASE
    return f"{base}{generated_uuid('entity', source_id)}"


def load_legacy_entity_iris(
    path: Path = LEGACY_ENTITY_IRIS,
) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            row["source_id"].strip(): row["legacy_iri"].strip()
            for row in csv.DictReader(stream)
        }


def legacy_entity_iri(
    source_id: str,
    overrides: dict[str, str] | None = None,
) -> str:
    """Return the generic ATNS IRI used before category-aware agent IRIs."""
    source_id = source_id.strip()
    overrides = load_legacy_entity_iris() if overrides is None else overrides
    if source_id in overrides:
        return overrides[source_id]
    return generated_resource_iri("entity", source_id)
