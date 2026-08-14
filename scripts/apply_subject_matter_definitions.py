"""Apply reviewed archived definitions to the curated ATNS subject vocabulary."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "specs" / "subject-matter-definitions.tsv"
VOCABULARY = ROOT / "vocabs" / "atns-sub.ttl"
CONCEPT_HISTORY_NOTE = (
    "Definition published by the ATNS project and recovered from the archived "
    "ATNS website."
)
SCHEME_HISTORY_NOTE = (
    "Subject-matter definitions were recovered from archived ATNS website pages. "
    "Each enriched concept cites the capture used; these historical definitions "
    "have not been reconfirmed by the current ATNS custodians."
)
APPLICABLE_STATUSES = {"stable", "single-sample", "definition-changed"}


def turtle_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False) + "@en"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        raise SystemExit("No subject-matter definition rows found")
    for field in ("concept_iri", "notation"):
        values = [row[field] for row in rows]
        if len(values) != len(set(values)):
            raise SystemExit(f"Duplicate {field} values in {path}")
    return rows


def update_concept(text: str, row: dict[str, str]) -> str:
    iri = row["concept_iri"]
    start = text.find(f"<{iri}>\n")
    if start < 0:
        raise SystemExit(f"Concept not found in vocabulary: {iri}")
    end = text.find("\n.\n", start)
    if end < 0:
        raise SystemExit(f"Concept block has no terminator: {iri}")
    end += 3
    block = text[start:end]

    block = re.sub(
        r"^    dcterms:source <[^>]+> ;\n",
        "",
        block,
        flags=re.MULTILINE,
    )
    block = block.replace(
        "    a skos:Concept ;\n",
        "    a skos:Concept ;\n"
        f"    dcterms:source <{row['source_url']}> ;\n",
        1,
    )
    definition = turtle_literal(row["definition"])
    block, definition_count = re.subn(
        r"^    skos:definition .*? ;\n",
        f"    skos:definition {definition} ;\n",
        block,
        count=1,
        flags=re.MULTILINE,
    )
    if definition_count != 1:
        raise SystemExit(f"Expected one definition in concept block: {iri}")

    block = re.sub(
        r"^    skos:historyNote "
        + re.escape(turtle_literal(CONCEPT_HISTORY_NOTE))
        + r" ;\n",
        "",
        block,
        flags=re.MULTILINE,
    )
    block = block.replace(
        "    skos:inScheme cs: ;\n",
        f"    skos:historyNote {turtle_literal(CONCEPT_HISTORY_NOTE)} ;\n"
        "    skos:inScheme cs: ;\n",
        1,
    )
    return text[:start] + block + text[end:]


def update_scheme(text: str) -> str:
    if turtle_literal(SCHEME_HISTORY_NOTE) not in text:
        marker = "    skos:historyNote\n"
        start = text.find(marker, text.find("\ncs:\n"))
        if start < 0:
            raise SystemExit("Concept scheme history note block not found")
        insertion = start + len(marker)
        text = (
            text[:insertion]
            + f"        {turtle_literal(SCHEME_HISTORY_NOTE)} ,\n"
            + text[insertion:]
        )
    text, count = re.subn(
        r'(    schema:dateModified ")\d{4}-\d{2}-\d{2}("\^\^xsd:date ;)$',
        rf"\g<1>{date.today().isoformat()}\g<2>",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise SystemExit("Expected one schema:dateModified on the concept scheme")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--vocabulary", type=Path, default=VOCABULARY)
    args = parser.parse_args()

    rows = load_rows(args.source)
    applicable = [row for row in rows if row["review_status"] in APPLICABLE_STATUSES]
    skipped = [row for row in rows if row["review_status"] not in APPLICABLE_STATUSES]
    if skipped:
        details = ", ".join(
            f"{row['notation']} ({row['review_status']})" for row in skipped
        )
        print(f"Skipping definitions that require manual resolution: {details}")

    text = args.vocabulary.read_text(encoding="utf-8")
    if "PREFIX dcterms:" not in text:
        text = text.replace(
            "PREFIX cs:",
            "PREFIX dcterms: <http://purl.org/dc/terms/>\nPREFIX cs:",
            1,
        )
    for row in applicable:
        text = update_concept(text, row)
    text = update_scheme(text)
    args.vocabulary.write_text(text, encoding="utf-8")
    print(f"Applied {len(applicable)} archived definitions to {args.vocabulary.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
