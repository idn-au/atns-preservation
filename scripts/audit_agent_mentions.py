#!/usr/bin/env python3
"""Find known IDN agents mentioned in ATNS Agreement summaries and bodies.

Matches are review evidence only. They do not assign ODRL party roles and do
not establish whether a mentioned agent is an assigner, assignee or other party.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parents[1]
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
DEFAULT_AGENTS_DIR = ROOT.parent / "agentsdb-data/data/raw"

ATNS = Namespace("https://linked.data.gov.au/def/atns/model/")
SCHEMA = Namespace("https://schema.org/")
AGREEMENT_TYPE = URIRef("https://data.idnau.org/pid/vocab/cat-obj-types/Agreement")
AGENT_TYPES = {SCHEMA.Organization, SCHEMA.Person}
ANCHOR_STOPWORDS = {
    "aboriginal", "and", "australia", "australian", "corporation", "council",
    "department", "government", "group", "indigenous", "limited", "of", "people",
    "pty", "the", "trust",
}


@dataclass(frozen=True)
class LabelEntry:
    agent: URIRef
    label: str
    normalized: str
    label_kind: str
    agent_type: str
    source_files: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-dir", type=Path, default=DEFAULT_AGENTS_DIR)
    return parser.parse_args()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("&", " and ")
    value = re.sub(r"[’‘`´]", "'", value)
    value = re.sub(r"[^\w']+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def first_literal(graph: Graph, subject: URIRef, predicate: URIRef) -> str:
    for value in graph.objects(subject, predicate):
        if isinstance(value, Literal):
            return str(value)
    return ""


def load_agents(directory: Path) -> tuple[list[LabelEntry], dict[str, set[URIRef]]]:
    graph = Graph()
    sources: dict[URIRef, set[str]] = defaultdict(set)
    for path in sorted(directory.glob("*.ttl")):
        source = Graph().parse(path, format="turtle")
        graph += source
        for subject in source.subjects(RDF.type, None):
            if any((subject, RDF.type, agent_type) in source for agent_type in AGENT_TYPES):
                sources[subject].add(path.name)

    labels_by_normalized: dict[str, set[URIRef]] = defaultdict(set)
    pending: list[tuple[URIRef, str, str, str]] = []
    for agent in sources:
        agent_type = "Person" if (agent, RDF.type, SCHEMA.Person) in graph else "Organization"
        for predicate, kind in ((SCHEMA.name, "canonical"), (SCHEMA.alternateName, "alternate")):
            for value in graph.objects(agent, predicate):
                if not isinstance(value, Literal):
                    continue
                label = str(value).strip()
                normalized = normalize(label)
                if len(normalized) < 3:
                    continue
                pending.append((agent, label, normalized, kind, agent_type))
                labels_by_normalized[normalized].add(agent)

    entries = [
        LabelEntry(agent, label, normalized, kind, agent_type, ";".join(sorted(sources[agent])))
        for agent, label, normalized, kind, agent_type in pending
    ]
    return entries, labels_by_normalized


def anchor(normalized_label: str) -> str:
    tokens = normalized_label.split()
    useful = [token for token in tokens if token not in ANCHOR_STOPWORDS and len(token) >= 3]
    return max(useful or tokens, key=len)


def mentioned(normalized_label: str, normalized_text: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(normalized_label)}(?!\w)", normalized_text))


def snippet(label: str, summary: str, body: str) -> str:
    for field_name, text in (("summary", summary), ("body", body)):
        match = re.search(re.escape(label), text, flags=re.IGNORECASE)
        if match:
            start = max(0, match.start() - 90)
            end = min(len(text), match.end() + 90)
            context = re.sub(r"\s+", " ", text[start:end]).strip()
            return f"{field_name}: {context}"
    return "normalised label match; inspect source text"


def confidence(entry: LabelEntry, ambiguity: int, related: bool, fields: str) -> str:
    token_count = len(entry.normalized.split())
    if ambiguity > 1 or entry.label_kind == "alternate" or token_count == 1:
        return "low"
    if related or token_count >= 3 or fields == "summary-and-body":
        return "high"
    return "medium"


def main() -> None:
    agents_dir = parse_args().agents_dir.resolve()
    if not agents_dir.exists():
        raise FileNotFoundError(f"Agent source directory not found: {agents_dir}")

    graph = Graph()
    for path in sorted(RDF_DIR.glob("*.ttl")):
        graph.parse(path, format="turtle")
    entries, labels_by_normalized = load_agents(agents_dir)

    by_anchor: dict[str, list[LabelEntry]] = defaultdict(list)
    for entry in entries:
        by_anchor[anchor(entry.normalized)].append(entry)

    related_names: dict[URIRef, set[str]] = defaultdict(set)
    for relationship in graph.subjects(RDF.type, ATNS.EntityRelationship):
        subjects = list(graph.objects(relationship, ATNS.subjectEntity))
        objects = list(graph.objects(relationship, ATNS.objectEntity))
        for agreement, others in ((entity, objects) for entity in subjects):
            for other in others:
                name = first_literal(graph, other, SCHEMA.name)
                if name:
                    related_names[agreement].add(normalize(name))
        for agreement, others in ((entity, subjects) for entity in objects):
            for other in others:
                name = first_literal(graph, other, SCHEMA.name)
                if name:
                    related_names[agreement].add(normalize(name))

    agreements = sorted(
        subject
        for subject in graph.subjects(SCHEMA.additionalType, AGREEMENT_TYPE)
        if (subject, RDF.type, ATNS.Entity) in graph
        and (subject, RDF.type, SCHEMA.CreativeWork) in graph
    )
    rows: list[dict[str, str | int | bool]] = []
    matched_agreements: set[URIRef] = set()
    for agreement in agreements:
        summary = first_literal(graph, agreement, SCHEMA.description)
        body = first_literal(graph, agreement, SCHEMA.text)
        normalized_summary = normalize(summary)
        normalized_body = normalize(body)
        tokens = set((normalized_summary + " " + normalized_body).split())
        candidates = {
            entry
            for token in tokens
            for entry in by_anchor.get(token, [])
            if mentioned(entry.normalized, normalized_summary)
            or mentioned(entry.normalized, normalized_body)
        }
        seen: set[tuple[URIRef, str]] = set()
        for entry in candidates:
            key = (entry.agent, entry.normalized)
            if key in seen:
                continue
            seen.add(key)
            in_summary = mentioned(entry.normalized, normalized_summary)
            in_body = mentioned(entry.normalized, normalized_body)
            fields = (
                "summary-and-body" if in_summary and in_body else "summary" if in_summary else "body"
            )
            ambiguity = len(labels_by_normalized[entry.normalized])
            related = entry.normalized in related_names.get(agreement, set())
            rows.append(
                {
                    "agreement": str(agreement),
                    "agreement_name": first_literal(graph, agreement, SCHEMA.name),
                    "source_entity_id": first_literal(graph, agreement, ATNS.sourceEntityId),
                    "atns_eid": first_literal(graph, agreement, ATNS.eid),
                    "agent": str(entry.agent),
                    "agent_label": entry.label,
                    "agent_type": entry.agent_type,
                    "label_kind": entry.label_kind,
                    "mentioned_in": fields,
                    "mention_count": len(
                        re.findall(
                            rf"(?<!\w){re.escape(entry.normalized)}(?!\w)",
                            normalized_summary + " " + normalized_body,
                        )
                    ),
                    "label_ambiguity_count": ambiguity,
                    "matches_related_atns_entity": related,
                    "confidence": confidence(entry, ambiguity, related, fields),
                    "agent_source_files": entry.source_files,
                    "evidence": snippet(entry.label, summary, body),
                }
            )
            matched_agreements.add(agreement)

    confidence_order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(
        key=lambda row: (
            confidence_order[str(row["confidence"])],
            str(row["agreement_name"]).casefold(),
            str(row["agent_label"]).casefold(),
        )
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "odrl-agent-mention-candidates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    confidence_counts = {
        level: sum(row["confidence"] == level for row in rows)
        for level in confidence_order
    }
    summary_path = REPORT_DIR / "odrl-agent-mention-summary.md"
    with summary_path.open("w", encoding="utf-8") as output:
        output.write("# ATNS ODRL agent-mention candidate audit\n\n")
        output.write(f"- Agreement-classified CreativeWorks: {len(agreements):,}\n")
        output.write(f"- Agent resources searched: {len({entry.agent for entry in entries}):,}\n")
        output.write(f"- Agent labels searched: {len(entries):,}\n")
        output.write(f"- Agreements with at least one agent mention: {len(matched_agreements):,}\n")
        output.write(f"- Candidate mention rows: {len(rows):,}\n")
        output.write(f"- High-confidence rows: {confidence_counts['high']:,}\n")
        output.write(f"- Medium-confidence rows: {confidence_counts['medium']:,}\n")
        output.write(f"- Low-confidence rows: {confidence_counts['low']:,}\n")
        output.write(f"- Agreements without an agent mention: {len(agreements) - len(matched_agreements):,}\n\n")
        output.write(
            "Matches use complete canonical or alternate agent labels with token boundaries. "
            "Confidence reflects label distinctiveness, ambiguity, repeated mention, and whether "
            "the same name occurs on an ATNS entity related to the Agreement. A mention does not "
            "establish an ODRL role; no assigner, assignee or other party assertion is created.\n"
        )

    print(
        f"Audited {len(agreements):,} agreements against {len({entry.agent for entry in entries}):,} "
        f"agents; {len(matched_agreements):,} agreements have at least one mention."
    )
    print(f"Wrote {csv_path.relative_to(ROOT)} and {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
