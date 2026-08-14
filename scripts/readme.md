# Scripts

The XML-to-RDF conversion scripts are documented in [the conversion guide](../docs/conversion.md).

`crawl_subject_matter_definitions.py` is a deliberately separate, networked archival-acquisition step. It recovers source-authored ATNS subject definitions from timestamped Internet Archive captures and writes a reviewable TSV. `apply_subject_matter_definitions.py` performs the deterministic offline update of the curated subject vocabulary after that TSV has been reviewed.

`crawl_sub_category_definitions.py` and `apply_subcategory_definitions.py` provide the same networked-acquisition and offline-application separation for the ATNS subcategory vocabulary.
