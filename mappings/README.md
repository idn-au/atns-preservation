# ATNS mapping drafts

These files keep external alignments separate from the preservation vocabularies in `vocabs/`. They are working reconciliation inputs for a later transformation pipeline and are expected to receive manual review.

## Mapping posture

- Use `skos:exactMatch` only for equivalent concepts, including local geographic concepts aligned with preferred GeoNames IRIs.
- Use `skos:closeMatch` or `skos:broadMatch` when the published term is not semantically identical.
- Use `schema:sameAs` for a legacy lookup value that denotes an organization reconciled to a ROR organization IRI.
- Prefer an organization IRI under `https://linked.data.gov.au/org/` when a suitable registered IRI exists; otherwise check ROR.
- Check ORCID for named natural persons. Do not assign an ORCID to an office, title, role string or unnamed person.
- Retain `skos:editorialNote` for unresolved, ambiguous or pipeline-specific decisions.

The public `linked.data.gov.au/org` RDF register supplies preferred IRIs for the Australian/Commonwealth, New South Wales, Queensland and Northern Territory governments. ROR matches recorded for organizations not found there should still receive human review, particularly where an ATNS value represents a historical organization.

The legacy `Binomial Names` list is heterogeneous. Its members should not all be transformed through one property: it contains places, organizations, Indigenous groups, agreement classifications, offices and a null/default value.
