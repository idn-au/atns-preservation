from pathlib import Path
from lxml import etree as ET
from collections import defaultdict
import html
import re
import sys

BASE = Path("raw/xml/ATNS_XML_05Apr22")

def clean(s):
    if s is None:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def rows(filename, row_tag):
    parser = ET.XMLParser(recover=True, encoding="utf-8")
    root = ET.parse(str(BASE / filename), parser).getroot()
    out = []
    for row in root.iter():
        if not row.tag.endswith(row_tag):
            continue
        d = {child.tag.split("}", 1)[-1]: clean(child.text) for child in row}
        out.append(d)
    return out

entities = rows("Entities.xml", "Entities")
list_elements = rows("ListElements.xml", "ListElements")
entity_refs = rows("Entity_Refs.xml", "Entity_Refs")
refs = rows("Refs.xml", "Refs")
entity_entity = rows("Entity_Entity.xml", "Entity_Entity")

category = {
    r["ListElementID"]: r["Value"]
    for r in list_elements
    if r.get("ListID") == "1"
}

refs = [r for r in refs if r.get("RefID")]
entities = [e for e in entities if e.get("EntityID")]

ref_by_id = {r["RefID"]: r for r in refs}
entity_by_id = {e["EntityID"]: e for e in entities}

refs_for_entity = defaultdict(list)
for r in entity_refs:
    refs_for_entity[r["EntityID"]].append(r)

rels_for_entity = defaultdict(list)
for r in entity_entity:
    rels_for_entity[r["EntityID"]].append(r)

def md_entity(eid):
    e = entity_by_id[eid]
    lines = []
    lines.append(f"# {e.get('Name','(no name)')}")
    lines.append("")
    lines.append(f"- EntityID: {e.get('EntityID')}")
    lines.append(f"- EID: {e.get('EID')}")
    lines.append(f"- Category: {category.get(e.get('CategoryID'), e.get('CategoryID'))}")
    lines.append(f"- Location: {e.get('Location','')}")
    lines.append(f"- Place: {e.get('Place','')}")
    lines.append(f"- State: {e.get('State','')}")
    lines.append(f"- Country: {e.get('Country','')}")
    lines.append(f"- Date from: {e.get('DateFrom') or e.get('DateFromDesc','')}")
    lines.append(f"- Date to: {e.get('DateTo') or e.get('DateToDesc','')}")
    lines.append(f"- Public: {e.get('Public')}")
    lines.append(f"- Deleted: {e.get('Deleted')}")
    lines.append("")
    if e.get("Summary"):
        lines.append("## Summary")
        lines.append("")
        lines.append(e["Summary"])
        lines.append("")
    if e.get("References"):
        lines.append("## Free-text references")
        lines.append("")
        lines.append(e["References"])
        lines.append("")
    if rels_for_entity[eid]:
        lines.append("## Related entities")
        lines.append("")
        for rel in rels_for_entity[eid]:
            target_id = rel.get("RelatedEntityID")
            target = entity_by_id.get(target_id, {})
            lines.append(f"- {rel.get('Relationship','(relationship?)')}: {target.get('Name', target_id)}")
        lines.append("")
    if refs_for_entity[eid]:
        lines.append("## Structured references")
        lines.append("")
        for er in refs_for_entity[eid]:
            ref = ref_by_id.get(er["RefID"], {})
            bits = [
                ref.get("Author"),
                f"({ref.get('Year')})" if ref.get("Year") else "",
                ref.get("Title"),
                ref.get("Publisher"),
            ]
            citation = " ".join(b for b in bits if b)
            lines.append(f"- {er.get('Relationship')}: {citation} [RefID {er.get('RefID')}]")
        lines.append("")
    return "\n".join(lines)

# default: first 5 agreements
if len(sys.argv) > 1:
    ids = sys.argv[1:]
else:
    ids = [e["EntityID"] for e in entities if e.get("CategoryID") == "1"][:5]

for eid in ids:
    print(md_entity(eid))
    print("\n---\n")
