from collections import Counter
from pathlib import Path
from lxml import etree as ET

XML = Path("raw/xml/ATNS_XML_05Apr22")
parser = ET.XMLParser(recover=True)

# Category names and subcategories
root = ET.parse(str(XML / "ListElements.xml"), parser).getroot()

categories = {}
subcats = {}

for e in root.findall("ListElements"):
    listid = e.findtext("ListID")

    if listid == "1":
        categories[e.findtext("ListElementID")] = e.findtext("Value") or ""

    elif listid == "6":
        subcats[e.findtext("ListElementID")] = (
            e.findtext("Value") or "",
            e.findtext("Class") or "(none)",
        )

# EntityID → CategoryID
entity_cat = {}

root = ET.parse(str(XML / "Entities.xml"), parser).getroot()

for e in root.findall("Entities"):
    entity_cat[e.findtext("EntityID")] = e.findtext("CategoryID")

# Count category/subcategory combinations
counts = Counter()

root = ET.parse(str(XML / "Entity_SubCategory.xml"), parser).getroot()

for e in root.findall("Entity_SubCategory"):
    entity_id = e.findtext("EntityID")
    subcat_id = e.findtext("SubCategoryID")

    cat_id = entity_cat.get(entity_id)

    category = categories.get(cat_id, "?")
    subcat, klass = subcats.get(subcat_id, ("?", "?"))

    counts[(category, subcat, klass)] += 1

print("entityCategory\tsubcategory\tsubcategoryClass\tcount")

for (category, subcat, klass), n in sorted(counts.items()):
    print(f"{category}\t{subcat}\t{klass}\t{n}")