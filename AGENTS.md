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

## IDN Catalogue Profile

- Follow the IDN Catalogue Profile where ATNS resources are being shaped for IDN or Prez-style publication.
- Treat the profile as current project guidance, not natural law. The specification is still settling; if it is inconsistent or underspecified, flag the issue and model pragmatically with the published terms available.
- Use HTTP/HTTPS PID IRIs as resource IRIs where possible, following the profile's identifier requirement.
- Do not duplicate HTTP/HTTPS PID IRIs as `schema:PropertyValue` identifier nodes.
- Use `schema:identifier "..."^^xsd:token` only when a non-HTTP identifier needs to be recorded as a catalogue identifier.
- Keep legacy ATNS identifiers, such as `EntityID`, `RefID`, `Entity_EntityID` and `EID`, as preservation/source-system identifiers unless a more specific publication pattern is agreed.
- Use `schema:conditionsOfAccess "Public"@en` for public sample records. Prefer a controlled access-rights concept later only when suitable concepts and the project pattern are clear. Avoid `schema:permissions` for data access status.

## Tools

- Use the cross-project `kurra-rdf-workflow` skill for RDF, SPARQL, SHACL, and Kurra-oriented work.
- Use `kurra`, `riot`, or `rapper` for RDF validation/querying before adding new dependencies.
- Add `rdflib` only when repeatable Python RDF generation or transformation scripts need it.
