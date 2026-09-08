"""Small lookup and literal helpers used by the declarative rdfcon specs."""

from __future__ import annotations

import csv
import os
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS


ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
CONVERSION_PROFILE = os.environ.get("ATNS_CONVERSION_PROFILE", "sample")
if CONVERSION_PROFILE not in {"sample", "sandbox"}:
    raise ValueError(
        "ATNS_CONVERSION_PROFILE must be either 'sample' or 'sandbox'"
    )

SOURCE_ROWS = ROOT / "build" / (
    "sample" if CONVERSION_PROFILE == "sample" else "sandbox/csv"
)
RESOURCE_REGISTRY = (
    SPECS / "public-sample-resources.csv"
    if CONVERSION_PROFILE == "sample"
    else ROOT / "build" / "sandbox" / "resources.csv"
)

VOCAB_FILES = {
    "category": ROOT / "vocabs" / "atns-cat.ttl",
    "country": ROOT / "vocabs" / "atns-country.ttl",
    "reference_type": ROOT / "vocabs" / "atns-ref.ttl",
    "relationship_type": ROOT / "vocabs" / "atns-rel.ttl",
    "subcategory": ROOT / "vocabs" / "atns-subcat.ttl",
    "subject": ROOT / "vocabs" / "atns-sub.ttl",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


@lru_cache(maxsize=1)
def _sample_resources() -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["kind"], row["source_id"]): row
        for row in _read_csv(RESOURCE_REGISTRY)
    }


def sample_resource(kind: str, source_id: str) -> dict[str, str] | None:
    return _sample_resources().get((kind, source_id.strip()))


def resource_iri(kind: str, source_id: str) -> str:
    resource = sample_resource(kind, source_id)
    return resource["resource_iri"] if resource else ""


@lru_cache(maxsize=None)
def _concepts(vocabulary: str) -> dict[str, str]:
    graph = Graph().parse(VOCAB_FILES[vocabulary])
    return {
        str(notation): str(concept)
        for concept, notation in graph.subject_objects(SKOS.notation)
    }


def concept_iri(vocabulary: str, notation: str) -> str:
    notation = notation.strip()
    if not notation:
        return ""
    try:
        return _concepts(vocabulary)[notation]
    except KeyError as error:
        raise KeyError(
            f"No {vocabulary} concept has source notation {notation!r}"
        ) from error


def concept_iri_if_known(vocabulary: str, notation: str) -> str:
    """Return a concept IRI, or an empty value for a blank source list entry."""
    notation = notation.strip()
    if not notation:
        return ""
    return _concepts(vocabulary).get(notation, "")


@lru_cache(maxsize=1)
def _classification_rules() -> dict:
    return yaml.safe_load(
        (SPECS / "classification-rules.yaml").read_text(encoding="utf-8")
    )


def entity_types(category_id: str) -> list[str]:
    return _classification_rules()["entity_category_types"].get(
        category_id.strip(), []
    )


def entity_additional_types(category_id: str) -> list[str]:
    return _classification_rules()["entity_category_additional_types"].get(
        category_id.strip(), []
    )


def is_agreement(category_id: str) -> bool:
    return (
        "https://data.idnau.org/pid/vocab/cat-obj-types/Agreement"
        in entity_additional_types(category_id)
    )


def legacy_atns_page_iri(source_id: str) -> str:
    """Return the deterministic legacy public ATNS page for a source entity."""
    return (
        "https://database.atns.net.au/agreement.asp?EntityID="
        + source_id.strip()
    )


@lru_cache(maxsize=1)
def _editorial_overrides() -> dict:
    return yaml.safe_load(
        (SPECS / "editorial-overrides.yaml").read_text(encoding="utf-8")
    )


def entity_description(source_id: str) -> str:
    return (
        _editorial_overrides()
        .get("entities", {})
        .get(source_id.strip(), {})
        .get("description", "")
    )


@lru_cache(maxsize=None)
def _rows(table: str) -> list[dict[str, str]]:
    return _read_csv(SOURCE_ROWS / f"{table}.csv")


@lru_cache(maxsize=1)
def _references_by_entity() -> dict[str, list[str]]:
    values: dict[str, list[str]] = defaultdict(list)
    for row in _rows("Entity_Refs"):
        iri = resource_iri("reference", row["RefID"])
        if iri:
            values[row["EntityID"]].append(iri)
    return values


def references_for_entity(entity_id: str) -> list[str]:
    return _references_by_entity().get(entity_id.strip(), [])


@lru_cache(maxsize=1)
def _subcategories_by_entity() -> dict[str, list[str]]:
    values: dict[str, list[str]] = defaultdict(list)
    for row in _rows("Entity_SubCategory"):
        iri = concept_iri_if_known("subcategory", row["SubCategoryID"])
        if iri:
            values[row["EntityID"]].append(iri)
    return values


def subcategories_for_entity(entity_id: str) -> list[str]:
    return _subcategories_by_entity().get(entity_id.strip(), [])


@lru_cache(maxsize=1)
def _subjects_by_entity() -> dict[str, list[str]]:
    values: dict[str, list[str]] = defaultdict(list)
    for row in _rows("Entity_SubjectMatter"):
        values[row["EntityID"]].append(
            concept_iri("subject", row["SubjectMatterID"])
        )
    return values


def subjects_for_entity(entity_id: str) -> list[str]:
    return _subjects_by_entity().get(entity_id.strip(), [])


def _boolean_lexical(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"0", "false", "no"}:
        return "false"
    if normalized in {"1", "true", "yes"}:
        return "true"
    raise ValueError(f"Unrecognized source boolean: {value!r}")


def source_boolean(value: str) -> str:
    return f'"{_boolean_lexical(value)}"^^xsd:boolean'


def access_iri(public: str) -> str:
    return (
        "https://linked.data.gov.au/def/data-access-rights/open"
        if _boolean_lexical(public) == "true"
        else ""
    )


def http_url(value: str) -> str:
    """Return a complete HTTP(S) URL, or empty for source notes/relative text."""
    value = value.strip()
    return value if re.fullmatch(r"https?://\S+", value) else ""


def iso_date(value: str) -> str:
    return value.strip().split("T", 1)[0]


def literal(
    value: str,
    lang: str | None = None,
    datatype: str | None = None,
) -> str:
    return Literal(
        value,
        lang=lang,
        datatype=URIRef(datatype) if datatype else None,
    ).n3()
