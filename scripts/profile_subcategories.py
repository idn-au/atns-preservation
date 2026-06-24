from pathlib import Path
from lxml import etree as ET

p = Path("raw/xml/ATNS_XML_05Apr22/ListElements.xml")
root = ET.parse(str(p)).getroot()

print("subcategory\tclass\tcat")

for e in root.findall("ListElements"):
    if e.findtext("ListID") != "6":
        continue

    value = e.findtext("Value") or ""
    klass = e.findtext("Class") or ""
    cat = e.findtext("Cat") or ""

    print(f"{value}\t{klass}\t{cat}")