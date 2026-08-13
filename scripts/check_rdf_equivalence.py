"""Prove that generated and split RDF preserve the golden ATNS graph."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "tests" / "golden-baseline.yaml"
AGREEMENT_RECORD = URIRef(
    "https://linked.data.gov.au/def/atns/model/AgreementRecord"
)
ATNS_DATASET = URIRef(
    "https://data.idnau.org/pid/resource/"
    "d23405b4-fc04-47e2-9e7a-9c5735ae3780"
)
SCHEMA_IS_PART_OF = URIRef("https://schema.org/isPartOf")


def load_graph(paths: list[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


def blank_node_triple_count(graph: Graph) -> int:
    return sum(
        1
        for subject, _, object_ in graph
        if isinstance(subject, BNode) or isinstance(object_, BNode)
    )


def canonical_hash(graph: Graph) -> str:
    if blank_node_triple_count(graph):
        raise ValueError(
            "The current simple canonicalization requires a graph without blank nodes"
        )
    lines = sorted(
        f"{subject.n3()} {predicate.n3()} {object_.n3()} ."
        for subject, predicate, object_ in graph
    )
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def assert_equal(label: str, expected: Graph, actual: Graph) -> None:
    missing = expected - actual
    extra = actual - expected
    if not missing and not extra:
        print(f"{label}: graph-identical ({len(actual)} triples)")
        return

    print(
        f"{label}: FAILED ({len(missing)} missing, {len(extra)} extra triples)"
    )
    for difference_label, graph in (("missing", missing), ("extra", extra)):
        for triple in sorted(graph, key=lambda value: tuple(map(str, value)))[:20]:
            print(
                f"  {difference_label}: "
                + " ".join(term.n3() for term in triple)
                + " ."
            )
    raise SystemExit(1)


def assert_agreement_dataset_membership(graph: Graph) -> None:
    agreements = set(graph.subjects(RDF.type, AGREEMENT_RECORD))
    missing = sorted(
        agreement
        for agreement in agreements
        if (agreement, SCHEMA_IS_PART_OF, ATNS_DATASET) not in graph
    )
    if missing:
        joined = "\n  ".join(str(value) for value in missing)
        raise SystemExit(
            "Agreement records missing ATNS dataset membership:\n  " + joined
        )
    print(f"ATNS dataset membership: {len(agreements)} agreement records")


def main() -> None:
    baseline = yaml.safe_load(BASELINE_PATH.read_text(encoding="utf-8"))
    aggregate_path = ROOT / baseline["aggregate"]
    aggregate = load_graph([aggregate_path])
    assert_agreement_dataset_membership(aggregate)

    if len(aggregate) != baseline["triple_count"]:
        raise SystemExit(
            f"Golden triple count changed: {len(aggregate)} "
            f"!= {baseline['triple_count']}"
        )
    actual_blank_nodes = blank_node_triple_count(aggregate)
    if actual_blank_nodes != baseline["blank_node_triple_count"]:
        raise SystemExit(
            f"Golden blank-node count changed: {actual_blank_nodes} "
            f"!= {baseline['blank_node_triple_count']}"
        )
    actual_hash = canonical_hash(aggregate)
    if actual_hash != baseline["canonical_ntriples_sha256"]:
        raise SystemExit(
            f"Golden graph hash changed: {actual_hash} "
            f"!= {baseline['canonical_ntriples_sha256']}"
        )
    print(
        f"golden baseline: {len(aggregate)} triples, SHA-256 {actual_hash}"
    )

    generated_paths = sorted(ROOT.glob(baseline["generated_glob"]))
    if len(generated_paths) != baseline["generated_file_count"]:
        raise SystemExit(
            f"Generated file count changed: {len(generated_paths)} "
            f"!= {baseline['generated_file_count']}"
        )
    generated = load_graph(generated_paths)
    assert_equal("generated RDF", aggregate, generated)

    split_item_paths = sorted(ROOT.glob(baseline["split_items_glob"]))
    if len(split_item_paths) != baseline["split_item_file_count"]:
        raise SystemExit(
            f"Published item file count changed: {len(split_item_paths)} "
            f"!= {baseline['split_item_file_count']}"
        )
    split = load_graph(
        [ROOT / baseline["split_catalogue"], *split_item_paths]
    )
    assert_equal("published split RDF", aggregate, split)


if __name__ == "__main__":
    main()
