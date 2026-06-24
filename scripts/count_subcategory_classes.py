from collections import Counter
from pathlib import Path
from lxml import etree as ET

p = Path("raw/xml/ATNS_XML_05Apr22/ListElements.xml")
root = ET.parse(str(p)).getroot()

counts = Counter()

for e in root.findall("ListElements"):
    if e.findtext("ListID") == "6":
        klass = e.findtext("Class") or "(none)"
        counts[klass] += 1

for k, n in sorted(counts.items()):
    print(f"{k}\t{n}")
