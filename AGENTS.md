# ATNS Preservation Working Notes

This repository preserves data recovered from the Agreements, Treaties and Negotiated Settlements website for possible use with Prez.

## Sensitivity

- Treat `raw/xml` as sensitive working data. Some source material may include legal documents supplied for ATNS staff summaries and not intended for public release.
- Do not quote or expose raw internal-looking content in chat or generated public examples unless the user explicitly asks and the record is confirmed public.
- Prefer public, non-deleted records when creating sample TTL, reports, or documentation.
- Avoid using attachments or document binaries in public samples until their publication status is reviewed.

## RDF Modelling

- Preserve source semantics where possible. Fix or update vocabularies only when clearly necessary for migration, validation, or Prez use.
- Treat `Entity` as the central legacy record unless a stronger local model has been agreed.
- Keep ATNS controlled-list values as SKOS concepts from `vocabs/`.
- Represent relationship rows as nodes when source row identity, provenance, or uncertainty matters.
- Model agreement-like distinctions such as ILUA, framework agreement, funding agreement, treaty, deed of settlement, and settlement agreement as subcategory concepts unless the project adopts a richer ontology.

## Tools

- Use the cross-project `kurra-rdf-workflow` skill for RDF, SPARQL, SHACL, and Kurra-oriented work.
- Use `kurra`, `riot`, or `rapper` for RDF validation/querying before adding new dependencies.
- Add `rdflib` only when repeatable Python RDF generation or transformation scripts need it.
