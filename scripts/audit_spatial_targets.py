#!/usr/bin/env python3
"""Audit spatial features that may be ODRL targets for ATNS Agreements.

The report records candidate evidence only. It does not create odrl:target
statements or assert that a spatial feature is the legal asset of a rule.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parents[1]
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
DEFAULT_FEATURES_DIR = (
    ROOT.parent / "indigenous-data-catalogue/resources/reference/datasets/features"
)

ATNS = Namespace("https://linked.data.gov.au/def/atns/model/")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
SCHEMA = Namespace("https://schema.org/")
AGREEMENT_TYPE = URIRef("https://data.idnau.org/pid/vocab/cat-obj-types/Agreement")
NNTT_FEATURE_BASE = "https://data.idnau.org/pid/nntt/"

NNTT_FILE_NUMBER = re.compile(
    r"NNTT_Fileno=([A-Z]{1,2}[0-9]{4})[/%-]([0-9]{3})", re.IGNORECASE
)
GEOGRAPHIC_TARGET_CUE = re.compile(
    r"\b(agreement area|determination area|land|waters?|country|site|reserve|"
    r"property|lease|licen[cs]e area|claim area|park|mine|infrastructure)\b",
    re.IGNORECASE,
)
TRAILING_QUALIFIER = re.compile(
    r"\s*\((?:ILUA|[^)]*\b(?:18|19|20)\d{2}\b[^)]*)\)\s*$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features-dir", type=Path, default=DEFAULT_FEATURES_DIR)
    return parser.parse_args()


def first_literal(graph: Graph, subject: URIRef, predicate: URIRef) -> str:
    for value in graph.objects(subject, predicate):
        if isinstance(value, Literal):
            return str(value)
    return ""


def normalized_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    previous = None
    while value != previous:
        previous = value
        value = TRAILING_QUALIFIER.sub("", value)
    value = re.sub(r"[‐‑‒–—]", "-", value)
    return re.sub(r"\s+", " ", value).strip()


def nntt_features(features_dir: Path) -> dict[str, tuple[URIRef, str]]:
    features: dict[str, tuple[URIRef, str]] = {}
    subject_pattern = re.compile(
        rf"<{re.escape(NNTT_FEATURE_BASE)}([A-Z]{{1,2}}[0-9]{{4}}-[0-9]{{3}})>"
        r".*?schema:name\s+\"((?:[^\"\\]|\\.)*)\"\s*;?",
        re.DOTALL,
    )
    for path in sorted(features_dir.glob("nntt-ilua-*.trig")):
        source = path.read_text(encoding="utf-8")
        for match in subject_pattern.finditer(source):
            identifier, name = match.groups()
            features.setdefault(
                identifier,
                (URIRef(f"{NNTT_FEATURE_BASE}{identifier}"), name.replace('\\"', '"')),
            )
    return features


def main() -> None:
    features_dir = parse_args().features_dir.resolve()
    atns_path = features_dir / "atns-entity-areas.trig"
    if not atns_path.exists():
        raise FileNotFoundError(f"ATNS feature data not found: {atns_path}")

    graph = Graph()
    for path in sorted(RDF_DIR.glob("*.ttl")):
        graph.parse(path, format="turtle")

    feature_data = Dataset(default_union=True)
    feature_data.parse(atns_path, format="trig")
    exact_names: dict[str, list[tuple[URIRef, str]]] = defaultdict(list)
    normalized_names: dict[str, list[tuple[URIRef, str]]] = defaultdict(list)
    for feature in feature_data.subjects(RDF.type, GEO.Feature):
        name = first_literal(feature_data, feature, SCHEMA.name)
        if not name:
            continue
        exact_names[name.casefold().strip()].append((feature, name))
        normalized_names[normalized_name(name)].append((feature, name))

    nntt = nntt_features(features_dir)
    agreements = sorted(
        subject
        for subject in graph.subjects(SCHEMA.additionalType, AGREEMENT_TYPE)
        if (subject, RDF.type, ATNS.Entity) in graph
        and (subject, RDF.type, SCHEMA.CreativeWork) in graph
    )

    rows: list[dict[str, str | int | bool]] = []
    matched_agreements: set[URIRef] = set()
    nntt_matched: set[URIRef] = set()
    atns_matched: set[URIRef] = set()
    for agreement in agreements:
        name = first_literal(graph, agreement, SCHEMA.name)
        summary = first_literal(graph, agreement, SCHEMA.description)
        body = first_literal(graph, agreement, SCHEMA.text)
        location = first_literal(graph, agreement, SCHEMA.location)
        evidence_text = "\n".join(value for value in (summary, body) if value)
        common = {
            "agreement": str(agreement),
            "agreement_name": name,
            "source_entity_id": first_literal(graph, agreement, ATNS.sourceEntityId),
            "atns_eid": first_literal(graph, agreement, ATNS.eid),
            "agreement_location": location,
            "has_summary": bool(summary),
            "has_body": bool(body),
            "has_geographic_text_cue": bool(GEOGRAPHIC_TARGET_CUE.search(evidence_text)),
        }

        for url in graph.objects(agreement, SCHEMA.url):
            match = NNTT_FILE_NUMBER.search(str(url))
            if not match:
                continue
            identifier = f"{match.group(1).upper()}-{match.group(2)}"
            candidate = nntt.get(identifier)
            if candidate is None:
                continue
            feature, feature_name = candidate
            rows.append(
                {
                    **common,
                    "candidate_feature": str(feature),
                    "feature_name": feature_name,
                    "source_dataset": "nntt-ilua",
                    "match_method": "nntt-file-number",
                    "confidence": "high",
                    "ambiguity_count": 1,
                    "candidate_name_in_text": normalized_name(feature_name)
                    in normalized_name(evidence_text),
                    "evidence": f"schema:url contains NNTT file number {identifier}",
                }
            )
            matched_agreements.add(agreement)
            nntt_matched.add(agreement)

        exact_key = name.casefold().strip()
        candidates = exact_names.get(exact_key, [])
        method = "exact-name"
        if not candidates:
            candidates = normalized_names.get(normalized_name(name), [])
            method = "normalized-name"
        for feature, feature_name in candidates:
            ambiguity = len(candidates)
            rows.append(
                {
                    **common,
                    "candidate_feature": str(feature),
                    "feature_name": feature_name,
                    "source_dataset": "atns-entity-areas",
                    "match_method": method,
                    "confidence": "medium" if ambiguity == 1 else "low",
                    "ambiguity_count": ambiguity,
                    "candidate_name_in_text": normalized_name(feature_name)
                    in normalized_name(evidence_text),
                    "evidence": (
                        "Agreement and feature names match"
                        if method == "exact-name"
                        else "Agreement and feature names match after removing a trailing date/ILUA qualifier"
                    ),
                }
            )
            matched_agreements.add(agreement)
            atns_matched.add(agreement)

    confidence_order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(
        key=lambda row: (
            confidence_order[str(row["confidence"])],
            str(row["agreement_name"]).casefold(),
            str(row["candidate_feature"]),
        )
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "odrl-spatial-target-candidates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    confidence_counts = {
        confidence: sum(row["confidence"] == confidence for row in rows)
        for confidence in confidence_order
    }
    summary_path = REPORT_DIR / "odrl-spatial-target-summary.md"
    with summary_path.open("w", encoding="utf-8") as output:
        output.write("# ATNS ODRL spatial-target candidate audit\n\n")
        output.write(f"- Agreement-classified CreativeWorks: {len(agreements):,}\n")
        output.write(f"- Agreements with at least one candidate: {len(matched_agreements):,}\n")
        output.write(f"- Agreements with a direct NNTT identifier match: {len(nntt_matched):,}\n")
        output.write(f"- Agreements with an ATNS feature-name match: {len(atns_matched):,}\n")
        output.write(f"- Agreements matched through both sources: {len(nntt_matched & atns_matched):,}\n")
        output.write(f"- Candidate rows rated high confidence: {confidence_counts['high']:,}\n")
        output.write(f"- Candidate rows rated medium confidence: {confidence_counts['medium']:,}\n")
        output.write(f"- Candidate rows rated low confidence: {confidence_counts['low']:,}\n")
        output.write(f"- Agreements without a candidate: {len(agreements) - len(matched_agreements):,}\n\n")
        output.write(
            "High confidence means a source `schema:url` contains an NNTT file number "
            "that resolves to an existing NNTT ILUA feature. Medium confidence means a "
            "unique ATNS feature-name match. Low confidence means that name matching is "
            "ambiguous. These are review candidates only: no `odrl:target` statement is "
            "created, and bounding-box features are not treated as legal boundaries.\n"
        )

    print(
        f"Audited {len(agreements):,} agreements; {len(matched_agreements):,} have "
        f"at least one spatial-target candidate."
    )
    print(f"Wrote {csv_path.relative_to(ROOT)} and {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
