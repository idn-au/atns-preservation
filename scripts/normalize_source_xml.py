"""Create a strictly valid, text-normalized working copy of the ATNS XML export.

The supplied export is preservation evidence and is never modified. This stage
copies it to an ignored build directory, removes characters forbidden by XML
1.0, and converts legacy HTML in Entity Summary and Body fields to structured
plain text. An audit report records changes without reproducing private text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import uuid
from collections import Counter
from pathlib import Path

import yaml
from lxml import etree, html as lxml_html


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "specs" / "source-manifest.yaml"
SOURCE_DIR = ROOT / "raw" / "xml" / "ATNS_XML_05Apr22"
OUTPUT_DIR = ROOT / "build" / "normalized-xml" / "ATNS_XML_05Apr22"
REPORT_PATH = ROOT / "build" / "reports" / "text-normalization.csv"
REVIEW_REPORT_PATH = ROOT / "build" / "reports" / "text-normalization-review.csv"
SAMPLE_REGISTRY = ROOT / "specs" / "public-sample-resources.csv"
PID_BASE = "https://data.idnau.org/pid/resource/"
UUID_NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://data.idnau.org/pid/resource/atns-preservation/source-identity",
)

RICH_TEXT_FIELDS = {"Summary", "Body"}
BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "div", "footer", "h1",
    "h2", "h3", "h4", "h5", "h6", "header", "main", "p", "section",
}
SKIP_TAGS = {"head", "meta", "noscript", "script", "style", "title", "xml"}
KNOWN_INLINE_TAGS = {
    "a", "abbr", "b", "big", "cite", "code", "del", "em", "font", "i",
    "ins", "label", "mark", "q", "s", "small", "span", "strike", "strong",
    "sub", "sup", "time", "u",
}
STRUCTURAL_TAGS = BLOCK_TAGS | {
    "br", "hr", "li", "ol", "table", "tbody", "td", "tfoot", "th", "thead",
    "tr", "ul",
}
TAG_PATTERN = re.compile(r"<\s*/?\s*([A-Za-z][\w:-]*)\b[^>]*>")
ILLEGAL_XML_10 = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def existing_entity_iris() -> dict[str, str]:
    with SAMPLE_REGISTRY.open(newline="", encoding="utf-8") as stream:
        return {
            row["source_id"]: row["resource_iri"]
            for row in csv.DictReader(stream)
            if row["kind"] == "entity"
        }


def entity_resource_iri(source_id: str, overrides: dict[str, str]) -> str:
    return overrides.get(
        source_id,
        f"{PID_BASE}{uuid.uuid5(UUID_NAMESPACE, f'entity:{source_id}')}",
    )


def local_name(tag: object) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def remove_illegal_xml_characters(value: str) -> tuple[str, int]:
    return ILLEGAL_XML_10.subn("", value)


def normalize_whitespace(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    value = value.replace("\\n", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r" *\n *", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def render_node(node: etree._Element, list_depth: int = 0) -> str:
    tag = local_name(node.tag)
    if tag in SKIP_TAGS or ":" in tag:
        return ""
    if tag == "br":
        return "\n"
    if tag == "hr":
        return "\n\n"
    if tag == "table":
        rows: list[str] = []
        for row in node.xpath(".//tr"):
            cells = []
            for cell in row.xpath("./th|./td"):
                text = normalize_whitespace(render_contents(cell, list_depth))
                if text:
                    cells.append(text)
            if cells:
                rows.append(" | ".join(cells))
        return "\n\n" + "\n".join(rows) + "\n\n"
    if tag == "tr" or tag in {"td", "th"}:
        return ""
    if tag == "li":
        content = normalize_whitespace(render_contents(node, list_depth + 1))
        bullet = "  " * list_depth + "• "
        return f"\n{bullet}{content}\n" if content else ""
    if tag == "a":
        content = render_contents(node, list_depth)
        href = (node.get("href") or "").strip()
        if href and href not in content and re.match(r"^(?:https?://|mailto:)", href):
            return f"{content} ({href})" if content.strip() else href
        return content

    content = render_contents(node, list_depth)
    if tag in BLOCK_TAGS or tag in {"ul", "ol"}:
        return f"\n\n{content}\n\n"
    return content


def render_contents(node: etree._Element, list_depth: int = 0) -> str:
    parts = [node.text or ""]
    for child in node:
        parts.append(render_node(child, list_depth))
        parts.append(child.tail or "")
    return "".join(parts)


def html_to_structured_text(value: str) -> tuple[str, list[str], Counter[str]]:
    """Convert a legacy HTML fragment while retaining paragraphs and lists."""
    tags = Counter(match.group(1).lower() for match in TAG_PATTERN.finditer(value))
    if not tags:
        return normalize_whitespace(value), [], tags

    review_reasons: list[str] = []
    unknown = sorted(
        tag for tag in tags if tag not in KNOWN_INLINE_TAGS | STRUCTURAL_TAGS
    )
    if unknown:
        review_reasons.append("unknown-tags:" + ",".join(unknown))
    if tags["table"]:
        review_reasons.append("table-flattened")

    try:
        wrapper = lxml_html.fragment_fromstring(value, create_parent="div")
        rendered = render_contents(wrapper)
    except (etree.ParserError, ValueError):
        review_reasons.append("html-parser-fallback")
        rendered = TAG_PATTERN.sub("", value)

    normalized = normalize_whitespace(rendered)
    if value.strip() and not normalized:
        review_reasons.append("empty-after-normalization")
    return normalized, review_reasons, tags


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-source-update",
        action="store_true",
        help="build a review copy before a replacement export has been checksum-accepted",
    )
    return parser.parse_args()


def verify_source(manifest: dict, allow_source_update: bool) -> None:
    for table, details in manifest["tables"].items():
        source = SOURCE_DIR / f"{table}.xml"
        if not source.exists():
            raise FileNotFoundError(f"Private source table is missing: {source}")
        actual = sha256_bytes(source.read_bytes())
        if not allow_source_update and actual != details["sha256"]:
            raise ValueError(
                f"Checksum mismatch for {source.relative_to(ROOT)}: expected "
                f"{details['sha256']}, got {actual}. Review the replacement export, "
                "then run 'task accept-source'."
            )


def main() -> None:
    args = parse_args()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    verify_source(manifest, args.allow_source_update)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    shutil.copytree(SOURCE_DIR, OUTPUT_DIR)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entity_iri_overrides = existing_entity_iris()

    audit_rows: list[dict[str, object]] = []
    for table in manifest["tables"]:
        original = SOURCE_DIR / f"{table}.xml"
        output = OUTPUT_DIR / original.name
        raw = original.read_text(encoding="utf-8")
        sanitized, illegal_count = remove_illegal_xml_characters(raw)
        parser = etree.XMLParser(recover=False, huge_tree=True, remove_blank_text=False)
        tree = etree.fromstring(sanitized.encode("utf-8"), parser=parser).getroottree()

        changed_fields = 0
        if table == "Entities":
            for row in tree.getroot():
                if local_name(row.tag) != "entities":
                    continue
                source_values = {
                    local_name(child.tag): (child.text or "").strip()
                    for child in row
                }
                source_id = source_values.get("entityid", "")
                title = source_values.get("name", "")
                is_published = (
                    source_values.get("public") == "1"
                    and source_values.get("deleted") == "0"
                    and bool(title)
                )
                publication_status = (
                    "published-in-sandbox" if is_published else "not-published-in-sandbox"
                )
                resource_iri = (
                    entity_resource_iri(source_id, entity_iri_overrides)
                    if is_published
                    else ""
                )
                for child in row:
                    field = local_name(child.tag)
                    canonical_field = next(
                        (name for name in RICH_TEXT_FIELDS if name.lower() == field), None
                    )
                    if canonical_field is None or not child.text:
                        continue
                    before = child.text
                    after, review_reasons, tags = html_to_structured_text(before)
                    if after == before:
                        continue
                    child.text = after
                    changed_fields += 1
                    audit_rows.append(
                        {
                            "table": table,
                            "source_id": source_id,
                            "resource_iri": resource_iri,
                            "title": title,
                            "publication_status": publication_status,
                            "field": canonical_field,
                            "status": "review" if review_reasons else "normalized",
                            "rules": (
                                "html-to-structured-text;whitespace-normalization"
                                if tags
                                else "whitespace-normalization"
                            ),
                            "review_reasons": ";".join(review_reasons),
                            "source_characters": len(before),
                            "normalized_characters": len(after),
                            "source_sha256": sha256_text(before),
                            "normalized_sha256": sha256_text(after),
                            "tags": ";".join(f"{tag}:{count}" for tag, count in sorted(tags.items())),
                        }
                    )

        source_digest = sha256_bytes(original.read_bytes())
        comment = etree.Comment(
            " Derived working copy; original preserved unchanged. "
            f"Source SHA-256: {source_digest}. "
            "XML-invalid controls removed and Entity rich text normalized by "
            "scripts/normalize_source_xml.py; see build/reports/text-normalization.csv. "
        )
        tree.getroot().addprevious(comment)
        tree.write(
            output,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=False,
        )
        etree.parse(str(output), etree.XMLParser(recover=False, huge_tree=True))
        print(
            f"{table}: derived XML valid; removed {illegal_count} forbidden controls; "
            f"normalized {changed_fields} rich-text fields"
        )

    fieldnames = [
        "table", "source_id", "resource_iri", "title", "publication_status",
        "field", "status", "rules", "review_reasons", "source_characters",
        "normalized_characters", "source_sha256", "normalized_sha256", "tags",
    ]
    with REPORT_PATH.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_rows)
    review_rows = [row for row in audit_rows if row["status"] == "review"]
    with REVIEW_REPORT_PATH.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)
    print(
        f"Wrote {len(audit_rows):,} field changes to {REPORT_PATH.relative_to(ROOT)}; "
        f"{len(review_rows):,} flagged fields to {REVIEW_REPORT_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
