"""Export the reviewed Yamatji Nation ILUA demo as a compact publication graph."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF


ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "build" / "sandbox" / "rdf" / "Entities-1.ttl"
REFERENCES_PATH = ROOT / "build" / "sandbox" / "rdf" / "Refs-1.ttl"
AGREEMENT = URIRef(
    "https://data.idnau.org/pid/resource/e450e34e-9806-5ed5-ba85-37a01c121064"
)
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
PROV = Namespace("http://www.w3.org/ns/prov#")
SCHEMA = Namespace("https://schema.org/")

# Follow only the relations needed to render the Agreement page. This keeps the
# demo self-contained without accidentally exporting the full legacy graph.
FOLLOW_PREDICATES = {
    DCTERMS.references,
    ODRL.permission,
    ODRL.prohibition,
    ODRL.obligation,
    ODRL.duty,
    ODRL.action,
    ODRL.assigner,
    ODRL.assignee,
    ODRL.target,
    PROV.wasDerivedFrom,
    SCHEMA.citation,
    SCHEMA.hasPart,
    SCHEMA.spatialCoverage,
}


def export(output_path: Path) -> None:
    source = Graph().parse(ENTITIES_PATH)
    source.parse(REFERENCES_PATH)
    output = Graph()
    queue = deque([AGREEMENT])
    visited: set[URIRef] = set()

    while queue:
        subject = queue.popleft()
        if subject in visited:
            continue
        visited.add(subject)
        for triple in source.triples((subject, None, None)):
            output.add(triple)
            _, predicate, obj = triple
            if predicate in FOLLOW_PREDICATES and isinstance(obj, URIRef):
                queue.append(obj)

    if (AGREEMENT, RDF.type, ODRL.Agreement) not in output:
        raise SystemExit("The generated source does not contain the enriched ODRL Agreement")
    obligation_count = len(set(output.objects(AGREEMENT, ODRL.obligation)))
    if obligation_count != 4:
        raise SystemExit(f"Expected four reviewed obligations; found {obligation_count}")

    for prefix, namespace in source.namespaces():
        output.bind(prefix, namespace)
    output.bind("odrl", ODRL)
    output.bind("schema", SCHEMA)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.serialize(output_path, format="turtle")
    print(
        f"Exported {len(output):,} triples across {len(visited):,} traversed resources "
        f"to {output_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination Turtle file")
    args = parser.parse_args()
    export(args.output.resolve())


if __name__ == "__main__":
    main()
