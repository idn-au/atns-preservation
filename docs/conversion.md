# ATNS XML-to-RDF conversion

## Purpose

This pipeline makes the conversion of the current public ATNS preservation sample transparent, readable and reproducible without committing the private source export. It does not overwrite published RDF. Generated files remain under the ignored `build/` directory until their graph is proven equivalent to the approved sample.

The conversion follows this boundary:

```text
private checksum-verified XML
    -> generic normalized CSV extraction
    -> declared public sample selection
    -> rdfcon YAML templates and documented editorial inputs
    -> ignored generated Turtle
    -> syntax validation and graph-equivalence checks
```

## Security and source identity

The XML export and source archive remain ignored because they may contain legal or internal-looking content that was not intended for publication. `specs/source-manifest.yaml` records the expected SHA-256 checksums without exposing the source content. An authorised developer must obtain the matching `ATNS_XML_05Apr22` export and place it under `raw/xml/ATNS_XML_05Apr22/` before running the pipeline.

The extractor refuses to continue if any required XML table differs from the tracked checksum. It reports table names and row counts only; it does not print source records.

Each table also declares its primary key, row count and ordered-column signature. Routine source updates may add rows, but they cannot introduce blank or duplicate primary keys or change the column structure without stopping for review.

## Responsibilities by layer

### Generic XML extraction

`scripts/extract_xml.py` verifies and converts the required Microsoft Access XML table exports to normalized CSV. It preserves every source column and contains no RDF vocabulary, class or property decisions.

### Public sample selection

`specs/public-sample-resources.csv` declares every included source row, its stable published resource IRI and whether an entity receives the full or supporting-record profile. `scripts/prepare_public_sample.py` applies that declaration to the normalized tables. The generated sample therefore cannot silently expand to private or deleted records.

### Declarative RDF mapping

The RDF model is visible in these `rdfcon` specifications:

- `specs/catalogue.yaml` describes the sample catalogue and dataset.
- `specs/entities.yaml` maps entity rows and their selected joins.
- `specs/references.yaml` maps reference rows.
- `specs/relationships.yaml` maps preserved entity-to-entity relationship rows.
- `specs/base.yaml` contains shared prefixes and output configuration.

The templates use `scripts/template_functions.py` only for stable resource lookup, controlled-vocabulary lookup, relational joins, source boolean and date normalization, and safe Turtle literal creation. RDF predicates and classes remain in the YAML.

### Editorial decisions

Source-derived facts and project-authored publication decisions are kept distinct:

- `specs/classification-rules.yaml` declares the project interpretation that source CategoryID `1` receives `atns:AgreementRecord` and CategoryID `3` receives `schema:Organization`. These classifications are not represented as authorised by the ATNS source owners.
- `specs/editorial-overrides.yaml` contains the four concise public descriptions written for the preservation sample rather than copied mechanically from the XML.
- `specs/subject-matter-definitions.tsv` records definitions recovered from timestamped Internet Archive captures of the public ATNS subject-matter pages, including the selected capture and review status.
- The `profile` column in `specs/public-sample-resources.csv` explains why the four showcased agreements contain richer descriptive fields while entities included only to support relationships remain deliberately minimal.

Controlled-list IRIs are resolved by their preserved source notations in the committed `vocabs/*.ttl` files. The curated schemes and concepts use the IDN PID pattern `https://data.idnau.org/pid/vocab/atns-{name}`; the structural ATNS model remains in its separate `https://linked.data.gov.au/def/atns/model/` namespace. Project-authored vocabulary definitions, mappings, alignments and history notes remain curated RDF overlays and are not regenerated from `ListElements.xml` by this sample pipeline.

### Archived subject-matter definitions

The public ATNS website published short definitions on pages identified by the preserved subject-matter IDs. `scripts/crawl_subject_matter_definitions.py` uses `reports/subject-matter.tsv` as its fixed crawl manifest, queries the Internet Archive capture index, and samples the earliest, February 2011-nearest and latest distinct captures for each concept. It records the selected definition, timestamped source URL, capture counts and exceptions in `specs/subject-matter-definitions.tsv`.

Run `task crawl-subject-definitions` only when intentionally refreshing the archival evidence. Review every non-`stable` row in the TSV. If Wayback temporarily refuses requests, `task retry-subject-definitions` retries only unresolved rows at a conservative request rate.

After review, run `task apply-subject-definitions`. This deterministic offline step replaces generated label-as-definition text only where the TSV contains usable evidence, adds a timestamped `dcterms:source` and history note to each enriched concept, updates the scheme modification date, and validates the resulting Turtle. Missing or empty archived definitions are left unchanged for later source-owner review.

The recovered text is represented as historical ATNS-published material, not as newly authorised terminology. The concept scheme records that the definitions have not yet been reconfirmed by the current ATNS custodians.

## Pinned tools

`pyproject.toml` and `uv.lock` pin the conversion environment, including `rdfcon` 1.11.1, lxml and PyYAML. `Taskfile.yml` exposes the supported commands.

Set up the environment once:

```bash
task setup
```

Run the complete conversion and verification:

```bash
task pipeline
```

Individual stages are also available through `task extract`, `task prepare`, `task convert`, `task validate` and `task check`.

## Manual source updates

An updated export with the same columns and additional or changed rows is handled deliberately:

1. Replace the private XML table files under `raw/xml/ATNS_XML_05Apr22/`.
2. Run `task accept-source`.
3. Review the resulting `specs/source-manifest.yaml` diff and the ignored `build/reports/removal-candidates.csv` report.
4. Resolve any removal candidates by deliberately updating the publication selection and published RDF; do not treat the report as an instruction to delete data automatically.
5. Run `task pipeline` and accept the update only when validation and the expected graph comparison pass.

`task accept-source` accepts row-only changes by recording the reviewed table checksums and row counts. It refuses column changes and rejects blank or duplicate source primary keys before updating the manifest.

New source rows are not published automatically because only records declared in `specs/public-sample-resources.csv` enter the RDF conversion. Adding a record requires a new selection entry with a unique source identity and globally unique HTTP(S) resource IRI. This prevents rerunning the transformation from creating another RDF resource for an already selected source row. A genuinely duplicated real-world record represented by two different source IDs cannot be resolved safely by automation and still requires reconciliation.

The preparation stage checks every selected entity and reference against the new export. It writes an `action=remove` candidate when a published row is missing, source-deleted or no longer public. A published relationship is also flagged when it depends on an entity marked for removal. If any candidates exist, conversion stops before generating a silently reduced RDF catalogue.

The golden graph check is expected to fail when an accepted source update legitimately changes published values or when a new resource is deliberately selected. That failure is the review point at which the curated aggregate, split files and golden baseline must be updated together.

## Golden graph and acceptance criteria

`tests/golden-baseline.yaml` freezes the approved graph characteristics:

- 253 triples
- no blank-node triples
- every `atns:AgreementRecord` linked to the Keeping Place ATNS dataset with `schema:isPartOf`
- canonical sorted N-Triples SHA-256 `cfe2734a7dce8b9b76890424ca3a9ddd19b2d6e44246a9f601d8bb9339d27664`
- 26 split resource item files plus the catalogue wrapper

`scripts/check_rdf_equivalence.py` rejects a conversion if the golden baseline changes unexpectedly, if any generated triple is missing or extra, or if the published split files cease to represent the same graph. Turtle whitespace, prefix choice and triple ordering may differ because RDF graph identity—not byte identity—is the preservation requirement.

## Current scope and replacement decision

The pipeline reproduces the complete current public sample exactly. It is safe to use as the maintenance path for that 235-triple sample after review. It is not yet a full-database publication converter: additional ATNS tables, publication filtering, sensitivity decisions and vocabulary-overlay rules must be designed and tested before expanding beyond the declared public resources.
