#!/usr/bin/env python3
"""Audit sentence-level evidence for ODRL assigner and assignee roles.

This is deliberately conservative. Party lists and "agreement between" wording
are not directional. Candidate roles are emitted only where a sentence contains
grant, consent, permission, authorisation or entitlement grammar.
"""

from __future__ import annotations

import csv
import html
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef

from audit_agent_mentions import normalize


ROOT = Path(__file__).resolve().parents[1]
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
AGENT_REPORT = REPORT_DIR / "odrl-agent-mention-candidates.csv"
SPATIAL_REPORT = REPORT_DIR / "odrl-spatial-target-candidates.csv"

ATNS = Namespace("https://linked.data.gov.au/def/atns/model/")
SCHEMA = Namespace("https://schema.org/")

DIRECTIONAL_CUE = re.compile(
    r"\b(grant(?:s|ed|ing)?|giv(?:e|es|en|ing)|provid(?:e|es|ed|ing)|consent(?:s|ed|ing)?|"
    r"permission|permit(?:s|ted|ting)?|authoris(?:e|es|ed|ing|ation)|allow(?:s|ed|ing)?|"
    r"entitl(?:e|es|ed|ement)|right to)\b",
    re.IGNORECASE,
)
ACTION_CUE = re.compile(
    r"\b(access|use|occupy|enter|develop|construct|explor(?:e|ation)|min(?:e|ing)|"
    r"perform|undertake|do(?:ing)?|future acts?)\b",
    re.IGNORECASE,
)
ACTIVE_VERB = re.compile(
    r"\b(grant(?:s|ed|ing)?|giv(?:e|es|en|ing)|provid(?:e|es|ed|ing)|consent(?:s|ed|ing)?|"
    r"authoris(?:e|es|ed|ing)|allow(?:s|ed|ing)|permit(?:s|ted|ting)?)\b",
    re.IGNORECASE,
)
RIGHTS_OBJECT = re.compile(
    r"\b(permission|consent|right|access|lease|licen[cs]e|authority|entitlement)\b",
    re.IGNORECASE,
)
CLEAR_PERMISSION_VERB = re.compile(
    r"\b(consent(?:s|ed)?|authoris(?:e|es|ed)|allow(?:s|ed)|permit(?:s|ted)?)\b",
    re.IGNORECASE,
)
PASSIVE_VERB = re.compile(
    r"\b(?:is|are|was|were|be|been)\s+(granted|given|provided|authorised|allowed|permitted)\b",
    re.IGNORECASE,
)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"br", "div", "li", "p", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"div", "li", "p", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def visible_text(value: str) -> str:
    parser = VisibleText()
    parser.feed(html.unescape(value))
    return "".join(parser.parts)


def sentences(value: str) -> list[str]:
    text = visible_text(value)
    return [
        re.sub(r"\s+", " ", part).strip()
        for part in re.split(r"(?<=[.!?])\s+|[\r\n]+", text)
        if re.sub(r"\s+", " ", part).strip()
    ]


def first_literal(graph: Graph, subject: URIRef, predicate: URIRef) -> str:
    for value in graph.objects(subject, predicate):
        if isinstance(value, Literal):
            return str(value)
    return ""


def between(value: str, start: int, end: int) -> str:
    return value[min(start, end) : max(start, end)]


def main() -> None:
    graph = Graph()
    for path in sorted(RDF_DIR.glob("*.ttl")):
        graph.parse(path, format="turtle")

    agents_by_agreement: dict[str, list[dict[str, str]]] = defaultdict(list)
    with AGENT_REPORT.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            agents_by_agreement[row["agreement"]].append(row)

    high_targets: dict[str, str] = {}
    if SPATIAL_REPORT.exists():
        with SPATIAL_REPORT.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                if row["confidence"] == "high":
                    high_targets.setdefault(row["agreement"], row["candidate_feature"])

    rows: list[dict[str, str | int | bool]] = []
    directional_agreements: set[str] = set()
    complete_pair_agreements: set[str] = set()
    for agreement_iri, agent_rows in agents_by_agreement.items():
        agreement = URIRef(agreement_iri)
        field_sentences = [
            ("summary", sentence)
            for sentence in sentences(first_literal(graph, agreement, SCHEMA.description))
        ] + [
            ("body", sentence)
            for sentence in sentences(first_literal(graph, agreement, SCHEMA.text))
        ]
        unique_agents = {
            (row["agent"], row["agent_label"]): row for row in agent_rows
        }
        for sentence_number, (field, sentence) in enumerate(field_sentences, start=1):
            normalized_sentence = normalize(sentence)
            cue = DIRECTIONAL_CUE.search(normalized_sentence)
            if cue is None:
                continue
            mentions: list[tuple[dict[str, str], int, int]] = []
            for row in unique_agents.values():
                label = normalize(row["agent_label"])
                match = re.search(rf"(?<!\w){re.escape(label)}(?!\w)", normalized_sentence)
                if match:
                    mentions.append((row, match.start(), match.end()))
            if not mentions:
                continue

            directional_agreements.add(agreement_iri)
            assigner = ""
            assignee = ""
            pattern = "directional-cue-with-agent"
            confidence = "low"
            rationale = "Directional vocabulary and a known agent occur together, but grammar does not resolve both roles."

            # Active voice: Agent A + grant verb + Agent B.
            for left in mentions:
                for right in mentions:
                    if left == right or left[1] >= right[1]:
                        continue
                    middle = between(normalized_sentence, left[2], right[1])
                    verb = ACTIVE_VERB.search(middle)
                    recipient_markers = list(re.finditer(r"\b(?:to|for)\b", middle))
                    words_after_marker = (
                        len(middle[recipient_markers[-1].end() :].split())
                        if recipient_markers
                        else 999
                    )
                    words_after_verb = len(middle[verb.end() :].split()) if verb else 999
                    following_recipient = normalized_sentence[right[2] : right[2] + 100]
                    marker_grammar = bool(recipient_markers) and words_after_marker <= 12
                    direct_grammar = words_after_verb <= 4
                    recipient_grammar = marker_grammar or direct_grammar
                    if verb and recipient_grammar:
                        assigner = left[0]["agent"]
                        assignee = right[0]["agent"]
                        if (
                            CLEAR_PERMISSION_VERB.search(middle)
                            or RIGHTS_OBJECT.search(middle)
                            or (direct_grammar and RIGHTS_OBJECT.search(following_recipient))
                        ):
                            pattern = "active-agent-grants-right-to-agent"
                            confidence = "high"
                            rationale = "One known agent grants a rights-bearing object to another known agent."
                        else:
                            pattern = "active-agent-transfers-object-to-agent"
                            confidence = "medium"
                            rationale = "The sentence is directional, but the transferred object is not clearly a permission or right."
                        break
                if assigner and assignee:
                    break

            # Passive voice: Agent B is permitted ... by Agent A.
            if not (assigner and assignee):
                for recipient in mentions:
                    passive = PASSIVE_VERB.search(normalized_sentence, recipient[2])
                    if not passive:
                        continue
                    by_match = re.search(r"\bby\b", normalized_sentence[passive.end() :])
                    if not by_match:
                        continue
                    by_position = passive.end() + by_match.end()
                    grantors = [item for item in mentions if item[1] >= by_position]
                    if grantors:
                        assigner = grantors[0][0]["agent"]
                        assignee = recipient[0]["agent"]
                        pattern = "passive-agent-permitted-by-agent"
                        confidence = "high"
                        rationale = "A known recipient is passively permitted/authorised by another known agent."
                        break

            # One-sided evidence is useful, but cannot produce an Agreement role pair.
            if not (assigner and assignee):
                for row, start, end in mentions:
                    before = normalized_sentence[max(0, start - 90) : start]
                    after = normalized_sentence[end : end + 90]
                    if re.search(r"\b(consent|permission)\s+(?:of|from)\s*$", before) or re.search(
                        r"^\s*(?:consent(?:s|ed)?|grant(?:s|ed)?|authoris(?:e|es|ed)?)\b",
                        after,
                    ):
                        assigner = row["agent"]
                        pattern = "candidate-assigner-only"
                        confidence = "medium"
                        rationale = "Grammar suggests this agent gives consent, but no known recipient is resolved."
                        break
                    if re.search(r"\b(?:to|for)\s*$", before) and re.search(
                        r"\b(consent|permission|grant|allow|authoris|permit)", before
                    ):
                        assignee = row["agent"]
                        pattern = "candidate-assignee-only"
                        confidence = "medium"
                        rationale = "Grammar suggests this agent receives a grant, but no known grantor is resolved."
                        break

            if assigner and assignee:
                complete_pair_agreements.add(agreement_iri)
            action_match = ACTION_CUE.search(normalized_sentence)
            rows.append(
                {
                    "agreement": agreement_iri,
                    "agreement_name": first_literal(graph, agreement, SCHEMA.name),
                    "source_entity_id": first_literal(graph, agreement, ATNS.sourceEntityId),
                    "text_field": field,
                    "sentence_number": sentence_number,
                    "sentence": sentence,
                    "mentioned_agents": "; ".join(
                        f"{item[0]['agent_label']} <{item[0]['agent']}>" for item in mentions
                    ),
                    "directional_pattern": pattern,
                    "candidate_assigner": assigner,
                    "candidate_assignee": assignee,
                    "candidate_action_lexeme": action_match.group(0) if action_match else "",
                    "high_confidence_spatial_target": high_targets.get(agreement_iri, ""),
                    "confidence": confidence,
                    "rationale": rationale,
                }
            )

    order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(
        key=lambda row: (
            order[str(row["confidence"])],
            str(row["agreement_name"]).casefold(),
            int(row["sentence_number"]),
        )
    )
    csv_path = REPORT_DIR / "odrl-directional-role-candidates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    counts = {level: sum(row["confidence"] == level for row in rows) for level in order}
    complete_with_target = {
        str(row["agreement"])
        for row in rows
        if row["candidate_assigner"]
        and row["candidate_assignee"]
        and row["candidate_action_lexeme"]
        and row["high_confidence_spatial_target"]
    }
    high_complete = {
        str(row["agreement"])
        for row in rows
        if row["confidence"] == "high"
        and row["candidate_assigner"]
        and row["candidate_assignee"]
    }
    summary_path = REPORT_DIR / "odrl-directional-role-summary.md"
    with summary_path.open("w", encoding="utf-8") as output:
        output.write("# ATNS ODRL directional-role audit\n\n")
        output.write(f"- Agreements with known-agent mentions: {len(agents_by_agreement):,}\n")
        output.write(f"- Agreements with directional sentences: {len(directional_agreements):,}\n")
        output.write(f"- Directional sentence candidates: {len(rows):,}\n")
        output.write(f"- High-confidence sentence rows: {counts['high']:,}\n")
        output.write(f"- Medium-confidence sentence rows: {counts['medium']:,}\n")
        output.write(f"- Low-confidence sentence rows: {counts['low']:,}\n")
        output.write(f"- Agreements with a complete candidate role pair: {len(complete_pair_agreements):,}\n")
        output.write(f"- Agreements with a high-confidence complete role pair: {len(high_complete):,}\n")
        output.write(
            "- Agreements with a complete role pair, action lexeme and high-confidence spatial target: "
            f"{len(complete_with_target):,}\n\n"
        )
        output.write(
            "High confidence means transparent sentence grammar places one known agent before a "
            "grant/consent verb and another after it, or expresses an equivalent passive construction. "
            "Medium confidence resolves one role or a directional transfer whose object is not clearly a right. "
            "Low confidence records co-occurrence only. "
            "All results require review; this audit creates no ODRL assertions.\n"
        )

    print(
        f"Found {len(rows):,} directional sentence candidates across "
        f"{len(directional_agreements):,} agreements; {len(complete_pair_agreements):,} "
        "have a complete candidate role pair."
    )
    print(f"Wrote {csv_path.relative_to(ROOT)} and {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
