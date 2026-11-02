"""Merge reviewed spatial, agent and ODRL enrichments into generated entity RDF."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, URIRef


ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "build" / "sandbox" / "rdf" / "Entities-1.ttl"
SPATIAL_PATH = ROOT / "enrichments" / "spatial-coverage.ttl"
AGENTS_PATH = ROOT / "enrichments" / "agent-attributions.ttl"
YAMATJI_ODRL_PATH = ROOT / "enrichments" / "yamatji-nation-odrl.ttl"
SCHEMA_SPATIAL_COVERAGE = URIRef("https://schema.org/spatialCoverage")
PROV_QUALIFIED_ATTRIBUTION = URIRef("http://www.w3.org/ns/prov#qualifiedAttribution")
RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
ODRL_AGREEMENT = URIRef("http://www.w3.org/ns/odrl/2/Agreement")
ODRL_OBLIGATION = URIRef("http://www.w3.org/ns/odrl/2/obligation")


def require_entity_subjects(
    entities: Graph, enrichment: Graph, predicate: URIRef, label: str
) -> set[tuple]:
    assertions = set(enrichment.triples((None, predicate, None)))
    missing_subjects = sorted(
        str(subject)
        for subject, _, _ in assertions
        if not any(entities.triples((subject, None, None)))
    )
    if missing_subjects:
        preview = "\n".join(f"- {iri}" for iri in missing_subjects[:10])
        raise SystemExit(
            f"Refusing to merge {label}: {len(missing_subjects)} Agreement subjects "
            f"are absent from {ENTITIES_PATH.relative_to(ROOT)}:\n{preview}"
        )
    return assertions


def main() -> None:
    entities = Graph().parse(ENTITIES_PATH)
    spatial = Graph().parse(SPATIAL_PATH)
    agents = Graph().parse(AGENTS_PATH)
    yamatji_odrl = Graph().parse(YAMATJI_ODRL_PATH)

    spatial_links = require_entity_subjects(
        entities, spatial, SCHEMA_SPATIAL_COVERAGE, "spatial coverage"
    )
    attributions = require_entity_subjects(
        entities, agents, PROV_QUALIFIED_ATTRIBUTION, "agent attributions"
    )
    agreement_subjects = set(yamatji_odrl.subjects(RDF_TYPE, ODRL_AGREEMENT))
    if not agreement_subjects:
        raise SystemExit(
            f"Refusing to merge {YAMATJI_ODRL_PATH.relative_to(ROOT)}: "
            "no odrl:Agreement subject was found"
        )
    missing_agreements = sorted(
        str(subject)
        for subject in agreement_subjects
        if not any(entities.triples((subject, None, None)))
    )
    if missing_agreements:
        preview = "\n".join(f"- {iri}" for iri in missing_agreements[:10])
        raise SystemExit(
            "Refusing to merge ODRL Agreement enrichment: "
            f"{len(missing_agreements)} Agreement subjects are absent from "
            f"{ENTITIES_PATH.relative_to(ROOT)}:\n{preview}"
        )
    obligations = set(yamatji_odrl.triples((None, ODRL_OBLIGATION, None)))

    entities += spatial
    entities += agents
    entities += yamatji_odrl
    entities.bind("schema", "https://schema.org/")
    entities.bind("prov", "http://www.w3.org/ns/prov#")
    entities.bind("odrl", "http://www.w3.org/ns/odrl/2/")
    entities.serialize(ENTITIES_PATH, format="turtle")
    print(
        f"Merged {len(spatial_links):,} reviewed spatialCoverage assertions and "
        f"{len(attributions):,} reviewed qualifiedAttributions, and "
        f"{len(agreement_subjects):,} ODRL Agreement with "
        f"{len(obligations):,} obligations into "
        f"{ENTITIES_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
