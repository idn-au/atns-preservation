from pathlib import Path
from lxml import etree as ET
import sys
import uuid

LIST_ID = sys.argv[1]

UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")

SCHEME = {
    "1": "atns-entity-category",
    "2": "atns-subject",
    "3": "atns-document-type",
    "4": "atns-attachment-type",
    "5": "atns-payment-type",
    "6": "atns-subcategory",
    "7": "atns-reference-type",
    "8": "atns-country",
    "9": "atns-scale",
    "10": "atns-link-type",
    "11": "atns-binomial-name",
    "12": "atns-relationship-type",
}

scheme = SCHEME.get(LIST_ID, "atns-concept")

p = Path("raw/xml/ATNS_XML_05Apr22/ListElements.xml")
root = ET.parse(str(p), ET.XMLParser(recover=True)).getroot()

for row in root.iter("ListElements"):
    d = {c.tag: (c.text or "").strip() for c in row}

    if d.get("ListID") != LIST_ID:
        continue

    notation = d.get("ListElementID")
    pref_label = d.get("Value")

    stable_uuid = uuid.uuid5(
        UUID_NAMESPACE,
        f"atns-list-{LIST_ID}-element-{notation}"
    )

    concept_id = f"{scheme}:{stable_uuid}"

    print(f"{concept_id}\t{pref_label}\t{notation}")