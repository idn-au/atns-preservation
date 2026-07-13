# ATNS sample TTL files

These files are small modelling samples for public, non-deleted ATNS agreement records:

- `atns-sample-model.ttl` defines conservative draft classes and properties for sample instance data.
- `public-agreements.ttl` contains four public agreement examples and a small set of related public entity/reference records.

## Modelling notes

The sample keeps the original ATNS pattern of treating `Entity` as the central record. The ATNS entity category and subcategory values remain SKOS concepts from `vocabs/`, rather than being replaced by a new class hierarchy.

Instance data uses IDN PID-style resource IRIs scoped under `https://data.idnau.org/pid/resource/atns/`. ATNS entity, reference, relationship-row and sample dataset IRIs are currently treated as preserved data resources. IRI suffixes use deterministic UUIDs rather than source database identifiers; the source identifiers are preserved separately with properties such as `atns:sourceEntityId`, `atns:sourceReferenceId` and `atns:sourceRelationshipId`. The `https://data.idnau.org/pid/org/` and `https://data.idnau.org/pid/person/` bases are reserved for later first-class organisation and person identifiers, rather than being used for every legacy ATNS entity row that happens to describe an organisation or person.

Agreement-like distinctions such as framework agreement, funding agreement, ILUA, treaty, deed of settlement and settlement agreement appear in the source as subcategories. For now the sample models those as `atns:subcategory` links. This avoids prematurely deciding whether they are separate RDF classes, legal-document genres, negotiated-process types, or public-display facets.

Entity-to-entity relationships are represented as relationship nodes. This preserves the source `Entity_EntityID`, the subject entity, the object entity and the ATNS relationship-type concept. It also leaves room to attach provenance or confidence later.

Entity-to-reference links use `dcterms:references` in the simple sample. The ATNS source also records reference-link roles such as `Primary`; if those qualifiers become important, model `Entity_Refs` rows as qualified relationship nodes rather than flattening them to direct reference links.

## Sensitivity note

The sample intentionally uses public, non-deleted entity and reference rows only. It does not include attachment/document binaries or raw legal documents, because project context indicates some source materials may have been internal-only and not intended for public release.
