"""Add legacy Agreement Summary and Body text to converted entity RDF."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parent.parent
ATNS_ENTITY = URIRef("https://linked.data.gov.au/def/atns/model/Entity")
SCHEMA_CREATIVE_WORK = URIRef("https://schema.org/CreativeWork")
SCHEMA_ADDITIONAL_TYPE = URIRef("https://schema.org/additionalType")
SCHEMA_DESCRIPTION = URIRef("https://schema.org/description")
SCHEMA_TEXT = URIRef("https://schema.org/text")
AGREEMENT = URIRef("https://data.idnau.org/pid/vocab/cat-obj-types/Agreement")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def rich_text(value: str) -> str:
    """Restore line breaks encoded by the legacy rich-text export."""
    return value.replace("\\n", "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("sample", "sandbox"), required=True)
    return parser.parse_args()


def main() -> None:
    profile = parse_args().profile
    build_dir = ROOT / "build" / profile
    csv_dir = build_dir if profile == "sample" else build_dir / "csv"
    registry_path = (
        ROOT / "specs" / "public-sample-resources.csv"
        if profile == "sample"
        else build_dir / "resources.csv"
    )
    graph_path = build_dir / "rdf" / "Entities-1.ttl"

    entity_iris = {
        row["source_id"]: URIRef(row["resource_iri"])
        for row in read_csv(registry_path)
        if row["kind"] == "entity"
    }
    graph = Graph().parse(graph_path)
    descriptions = 0
    texts = 0
    for row in read_csv(csv_dir / "Entities.csv"):
        subject = entity_iris.get(row["EntityID"])
        if subject is None or (subject, SCHEMA_ADDITIONAL_TYPE, AGREEMENT) not in graph:
            continue
        if (subject, RDF.type, ATNS_ENTITY) not in graph:
            continue
        if (subject, RDF.type, SCHEMA_CREATIVE_WORK) not in graph:
            continue
        if row["Summary"]:
            graph.add(
                (subject, SCHEMA_DESCRIPTION, Literal(rich_text(row["Summary"]), lang="en"))
            )
            descriptions += 1
        if row["Body"]:
            graph.add((subject, SCHEMA_TEXT, Literal(rich_text(row["Body"]), lang="en")))
            texts += 1

    graph.serialize(graph_path, format="turtle")
    print(
        f"{profile}: added {descriptions:,} Agreement descriptions and "
        f"{texts:,} Agreement text bodies -> {graph_path.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
