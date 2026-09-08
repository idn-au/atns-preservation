#!/usr/bin/env python3
"""Generate a human-review batch of new ATNS organisation candidates.

Candidates come from ATNS Organization entities related to Agreement-classified
CreativeWorks. Exact IDC agents-database matches are excluded. Close name matches
are quarantined for identity review rather than minted as new organisations.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parents[1]
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
DEFAULT_AGENTS_DIR = ROOT.parent / "agentsdb-data/data/raw"

ATNS = Namespace("https://linked.data.gov.au/def/atns/model/")
SDO = Namespace("https://schema.org/")
AGREEMENT_TYPE = URIRef("https://data.idnau.org/pid/vocab/cat-obj-types/Agreement")
ORGANIZATION_BASE = "https://data.idnau.org/pid/organization/"
FUZZY_THRESHOLD = 0.92


@dataclass(frozen=True)
class Candidate:
    source: URIRef
    name: str
    normalized: str
    url: str
    agreements: tuple[URIRef, ...]
    mentioned_agreements: tuple[URIRef, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-dir", type=Path, default=DEFAULT_AGENTS_DIR)
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Distinct organisations in the review batch; 0 writes all candidates",
    )
    parser.add_argument(
        "--include-all-attributions",
        action="store_true",
        help="Emit every related Agreement attribution instead of one representative per organisation",
    )
    return parser.parse_args()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("&", " and ")
    value = re.sub(r"[’‘`´]", "'", value)
    value = re.sub(r"[^\w']+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    # Catalogue identity matching ignores initial English articles while the
    # source label itself remains unchanged for display and RDF generation.
    return re.sub(r"^(?:a|an|the)\s+", "", value)


def first_literal(graph: Graph, subject: URIRef, predicate: URIRef) -> str:
    for value in graph.objects(subject, predicate):
        if isinstance(value, Literal) and str(value).strip():
            return str(value).strip()
    return ""


def valid_http_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def turtle_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"@en'


def load_graph(directory: Path) -> Graph:
    graph = Graph()
    for path in sorted(directory.glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def load_agent_labels(directory: Path) -> dict[str, set[URIRef]]:
    labels: dict[str, set[URIRef]] = defaultdict(set)
    for path in sorted(directory.glob("*.ttl")):
        graph = Graph().parse(path, format="turtle")
        for agent in set(graph.subjects(RDF.type, SDO.Organization)) | set(
            graph.subjects(RDF.type, SDO.Person)
        ):
            for predicate in (SDO.name, SDO.alternateName):
                for value in graph.objects(agent, predicate):
                    if isinstance(value, Literal) and normalize(str(value)):
                        labels[normalize(str(value))].add(agent)
    return labels


def closest_existing(name: str, labels: dict[str, set[URIRef]]) -> tuple[str, float]:
    best_name = ""
    best_score = 0.0
    for existing_name in labels:
        # Only similarly shaped labels can meet the duplicate-review threshold.
        # This avoids millions of expensive comparisons against unrelated names.
        if existing_name[:1] != name[:1] or abs(len(existing_name) - len(name)) > max(
            4, int(len(name) * 0.2)
        ):
            continue
        score = SequenceMatcher(None, name, existing_name).ratio()
        if score > best_score:
            best_name, best_score = existing_name, score
    return best_name, best_score


def minted_iri(source: URIRef) -> URIRef:
    identifier = uuid.uuid5(uuid.NAMESPACE_URL, f"atns-organization:{source}")
    return URIRef(f"{ORGANIZATION_BASE}{identifier}")


def build_candidates(graph: Graph) -> list[Candidate]:
    agreements = {
        subject
        for subject in graph.subjects(SDO.additionalType, AGREEMENT_TYPE)
        if (subject, RDF.type, ATNS.Entity) in graph
        and (subject, RDF.type, SDO.CreativeWork) in graph
    }
    organizations = set(graph.subjects(RDF.type, SDO.Organization))
    related: dict[URIRef, set[URIRef]] = defaultdict(set)
    for relationship in graph.subjects(RDF.type, ATNS.EntityRelationship):
        subjects = set(graph.objects(relationship, ATNS.subjectEntity))
        objects = set(graph.objects(relationship, ATNS.objectEntity))
        for agreement in subjects & agreements:
            related.update({org: related[org] | {agreement} for org in objects & organizations})
        for agreement in objects & agreements:
            related.update({org: related[org] | {agreement} for org in subjects & organizations})

    candidates: list[Candidate] = []
    for organization, linked_agreements in related.items():
        name = first_literal(graph, organization, SDO.name)
        if not name:
            continue
        url = first_literal(graph, organization, SDO.url)
        if not valid_http_url(url):
            url = ""
        mentioned: list[URIRef] = []
        normalized_name = normalize(name)
        pattern = re.compile(rf"(?<!\w){re.escape(normalized_name)}(?!\w)")
        for agreement in linked_agreements:
            text = " ".join(
                first_literal(graph, agreement, predicate)
                for predicate in (SDO.description, SDO.text)
            )
            if pattern.search(normalize(text)):
                mentioned.append(agreement)
        candidates.append(
            Candidate(
                organization,
                name,
                normalized_name,
                url,
                tuple(sorted(linked_agreements, key=str)),
                tuple(sorted(mentioned, key=str)),
            )
        )
    return candidates


def selected_agreements(candidate: Candidate, include_all: bool) -> tuple[URIRef, ...]:
    if include_all:
        return candidate.agreements
    if candidate.mentioned_agreements:
        return candidate.mentioned_agreements[:1]
    return candidate.agreements[:1]


def write_turtle(
    path: Path, candidates: list[Candidate], graph: Graph, include_all: bool
) -> int:
    lines = [
        "@prefix droles: <https://linked.data.gov.au/def/data-roles/> .",
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix sdo: <https://schema.org/> .",
        "",
        "# DRAFT REVIEW DATA: candidate organisations and subject-agent associations.",
        "# Delete or edit rejected blocks before promoting reviewed data.",
        "",
    ]
    attribution_count = 0
    for candidate in candidates:
        organization = minted_iri(candidate.source)
        lines.extend(
            [
                "############################################################",
                f"# Candidate: {candidate.name}",
                f"# Source ATNS entity: {candidate.source}",
                "############################################################",
                "",
            ]
        )
        for agreement in selected_agreements(candidate, include_all):
            agreement_name = first_literal(graph, agreement, SDO.name)
            lines.extend(
                [
                    f"# Agreement: {agreement_name}",
                    f"<{agreement}>",
                    "    prov:qualifiedAttribution [",
                    "        a prov:Attribution ;",
                    f"        sdo:agent <{organization}> ;",
                    "        sdo:roleName droles:subjectAgent",
                    "    ] .",
                    "",
                ]
            )
            attribution_count += 1
        lines.extend(
            [
                f"<{organization}>",
                "    a sdo:Organization ;",
                f"    sdo:name {turtle_string(candidate.name)}" + (" ;" if candidate.url else " ."),
            ]
        )
        if candidate.url:
            lines.append(f"    sdo:url <{candidate.url}> .")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return attribution_count


def main() -> None:
    args = parse_args()
    agents_dir = args.agents_dir.resolve()
    if not agents_dir.exists():
        raise FileNotFoundError(f"Agent source directory not found: {agents_dir}")

    graph = load_graph(RDF_DIR)
    labels = load_agent_labels(agents_dir)
    all_candidates = build_candidates(graph)
    novel: list[Candidate] = []
    possible_existing: list[tuple[Candidate, str, float, str]] = []
    exact_count = 0
    for candidate in all_candidates:
        if candidate.normalized in labels:
            exact_count += 1
            continue
        closest_name, similarity = closest_existing(candidate.normalized, labels)
        if similarity >= FUZZY_THRESHOLD:
            existing_iris = ";".join(sorted(map(str, labels[closest_name])))
            possible_existing.append((candidate, closest_name, similarity, existing_iris))
        else:
            novel.append(candidate)

    novel.sort(
        key=lambda candidate: (
            -bool(candidate.mentioned_agreements),
            -bool(candidate.url),
            len(candidate.agreements),
            candidate.name.casefold(),
        )
    )
    selected = novel if args.limit == 0 else novel[: args.limit]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ttl_path = REPORT_DIR / "agent-enrichment-candidates.ttl"
    csv_path = REPORT_DIR / "agent-enrichment-candidates.csv"
    fuzzy_path = REPORT_DIR / "agent-enrichment-possible-existing.csv"
    attribution_count = write_turtle(
        ttl_path, selected, graph, args.include_all_attributions
    )

    fields = [
        "candidate_organization",
        "candidate_name",
        "candidate_url",
        "source_atns_entity",
        "agreement",
        "agreement_name",
        "name_mentioned_in_agreement_text",
        "review_decision",
        "reviewed_name",
        "reviewed_url",
        "review_notes",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for candidate in selected:
            for agreement in selected_agreements(
                candidate, args.include_all_attributions
            ):
                writer.writerow(
                    {
                        "candidate_organization": str(minted_iri(candidate.source)),
                        "candidate_name": candidate.name,
                        "candidate_url": candidate.url,
                        "source_atns_entity": str(candidate.source),
                        "agreement": str(agreement),
                        "agreement_name": first_literal(graph, agreement, SDO.name),
                        "name_mentioned_in_agreement_text": agreement
                        in candidate.mentioned_agreements,
                        "review_decision": "",
                        "reviewed_name": "",
                        "reviewed_url": "",
                        "review_notes": "",
                    }
                )

    fuzzy_fields = [
        "source_atns_entity",
        "candidate_name",
        "candidate_url",
        "possible_existing_normalized_name",
        "similarity",
        "possible_existing_agents",
    ]
    with fuzzy_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fuzzy_fields)
        writer.writeheader()
        for candidate, name, similarity, iris in sorted(
            possible_existing, key=lambda row: (-row[2], row[0].name.casefold())
        ):
            writer.writerow(
                {
                    "source_atns_entity": str(candidate.source),
                    "candidate_name": candidate.name,
                    "candidate_url": candidate.url,
                    "possible_existing_normalized_name": name,
                    "similarity": f"{similarity:.3f}",
                    "possible_existing_agents": iris,
                }
            )

    Graph().parse(ttl_path, format="turtle")
    print(f"Related ATNS organisation entities: {len(all_candidates):,}")
    print(f"Excluded exact IDC agent matches: {exact_count:,}")
    print(f"Quarantined possible existing agents: {len(possible_existing):,}")
    print(f"Novel organisation candidates: {len(novel):,}")
    print(
        f"Wrote {len(selected):,} organisations and {attribution_count:,} attributions "
        f"to {ttl_path.relative_to(ROOT)}"
    )
    print(f"Wrote {csv_path.relative_to(ROOT)} and {fuzzy_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
