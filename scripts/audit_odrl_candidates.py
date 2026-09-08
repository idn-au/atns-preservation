#!/usr/bin/env python3
"""Audit ATNS agreement records for evidence useful in reviewed ODRL enrichment.

This report deliberately does not infer ODRL rules. A signatory relationship is
party evidence only; it does not establish an assigner, assignee, action or asset.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS


ROOT = Path(__file__).resolve().parents[1]
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
VOCAB_DIR = ROOT / "vocabs"
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"

ATNS = Namespace("https://linked.data.gov.au/def/atns/model/")
SCHEMA = Namespace("https://schema.org/")
AGREEMENT_TYPE = URIRef("https://data.idnau.org/pid/vocab/cat-obj-types/Agreement")

LEXICAL_CUES = {
    "party": re.compile(
        r"\b(part(?:y|ies)|signator(?:y|ies)|between|applicant|respondent)\b",
        re.IGNORECASE,
    ),
    "duty": re.compile(
        r"\b(must|shall|required|obligation|undertak(?:e|es|en|ing)|commitment|agree(?:d|s)? to)\b",
        re.IGNORECASE,
    ),
    "permission_action": re.compile(
        r"\b(permission|permit(?:s|ted)?|consent|right to|access|use|occupy|develop|explor(?:e|ation)|min(?:e|ing))\b",
        re.IGNORECASE,
    ),
    "target_asset": re.compile(
        r"\b(agreement area|determination area|land|waters?|site|property|resource|infrastructure)\b",
        re.IGNORECASE,
    ),
    "constraint": re.compile(
        r"\b(condition|subject to|only|unless|restriction|commenc(?:e|ement)|terminat(?:e|es|ion)|expir(?:e|y))\b",
        re.IGNORECASE,
    ),
}


def load_turtle(directory: Path) -> Graph:
    graph = Graph()
    for path in sorted(directory.glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def first_text(graph: Graph, subject: URIRef, predicates: tuple[URIRef, ...]) -> str:
    for predicate in predicates:
        for value in graph.objects(subject, predicate):
            if isinstance(value, Literal):
                return str(value)
    return ""


def main() -> None:
    graph = load_turtle(RDF_DIR)
    vocab = load_turtle(VOCAB_DIR)
    graph += vocab

    agreements = sorted(
        subject
        for subject in graph.subjects(SCHEMA.additionalType, AGREEMENT_TYPE)
        if (subject, RDF.type, ATNS.Entity) in graph
        and (subject, RDF.type, SCHEMA.CreativeWork) in graph
    )

    relationships: dict[URIRef, list[URIRef]] = defaultdict(list)
    for relationship in graph.subjects(RDF.type, ATNS.EntityRelationship):
        for entity in graph.objects(relationship, ATNS.subjectEntity):
            relationships[entity].append(relationship)
        for entity in graph.objects(relationship, ATNS.objectEntity):
            relationships[entity].append(relationship)

    rows: list[dict[str, str | int | bool]] = []
    for agreement in agreements:
        rels = set(relationships[agreement])
        signatory_count = 0
        for relationship in rels:
            for relationship_type in graph.objects(relationship, ATNS.relationshipType):
                label = first_text(
                    graph,
                    relationship_type,
                    (SKOS.prefLabel, SCHEMA.name, RDFS.label),
                )
                if "signator" in label.casefold():
                    signatory_count += 1

        summary = first_text(graph, agreement, (SCHEMA.description,))
        body = first_text(graph, agreement, (SCHEMA.text,))
        evidence_text = "\n".join(value for value in (summary, body) if value)
        cue_flags = {
            f"has_{name}_cue": bool(pattern.search(evidence_text))
            for name, pattern in LEXICAL_CUES.items()
        }
        cue_count = sum(cue_flags.values())
        if signatory_count and evidence_text:
            assessment = "structured-party-and-text-evidence"
        elif evidence_text:
            assessment = "text-evidence-only"
        elif signatory_count:
            assessment = "party-evidence-only"
        else:
            assessment = "linked-shell-only"

        row = {
            "agreement": str(agreement),
            "name": first_text(graph, agreement, (SCHEMA.name, RDFS.label)),
            "relationship_count": len(rels),
            "signatory_relationship_count": signatory_count,
            "reference_count": len(set(graph.objects(agreement, DCTERMS.references))),
            "has_url": any(True for _ in graph.objects(agreement, SCHEMA.url)),
            "has_summary": bool(summary),
            "has_body": bool(body),
            "evidence_text_characters": len(evidence_text),
            **cue_flags,
            "lexical_cue_count": cue_count,
            "assessment": assessment,
        }
        rows.append(row)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "odrl-enrichment-candidates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    structured_and_text = sum(
        row["assessment"] == "structured-party-and-text-evidence" for row in rows
    )
    text_only = sum(row["assessment"] == "text-evidence-only" for row in rows)
    party_only = sum(row["assessment"] == "party-evidence-only" for row in rows)
    shells = sum(row["assessment"] == "linked-shell-only" for row in rows)
    with (REPORT_DIR / "odrl-enrichment-summary.md").open("w", encoding="utf-8") as output:
        output.write("# ATNS ODRL enrichment evidence audit\n\n")
        output.write(f"- Agreement-classified CreativeWorks: {len(rows):,}\n")
        output.write(
            f"- Records with structured party and text evidence: {structured_and_text:,}\n"
        )
        output.write(f"- Records with text evidence only: {text_only:,}\n")
        output.write(f"- Records with structured party evidence only: {party_only:,}\n")
        output.write(f"- Linked-shell-only records: {shells:,}\n")
        for name in LEXICAL_CUES:
            count = sum(bool(row[f"has_{name}_cue"]) for row in rows)
            output.write(f"- Records with a {name.replace('_', ' ')} lexical cue: {count:,}\n")
        output.write("\n")
        output.write(
            "Signatory relationships identify possible party evidence only. Lexical cues "
            "rank records for human review; they do not establish ODRL assigner/assignee "
            "roles, actions, targets, duties or constraints. No ODRL Permission is "
            "generated by this audit.\n"
        )

    print(
        f"Audited {len(rows):,} agreements; {structured_and_text:,} have structured "
        f"party plus text evidence and {text_only:,} have text evidence only."
    )
    print(f"Wrote {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
