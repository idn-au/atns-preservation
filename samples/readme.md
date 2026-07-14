# ATNS sample TTL files

These files are small modelling samples for public, non-deleted ATNS agreement records:

- `atns-model.ttl` defines conservative draft classes and properties for sample instance data.
- `public-agreements.ttl` contains four public agreement examples and a small set of related public entity/reference records.

## Modelling notes

The sample keeps the original ATNS pattern of treating `Entity` as the central record. The ATNS entity category and subcategory values remain SKOS concepts from `vocabs/`, rather than being replaced by a new class hierarchy.

Use Schema.org and DCTERMS for stable publication-level meanings such as names, dates, locations, URLs, catalogue membership, citations and simple entity-to-reference links. Keep ATNS-specific terms for source-system semantics that need preservation, including source identifiers, ATNS categories/subcategories, deleted flags, relationship rows and controlled-list values. Do not replace an ATNS term with a broader external term unless the mapping is clear enough that source meaning is not lost.

Instance data uses IDN PID-style resource IRIs scoped under `https://data.idnau.org/pid/resource/atns/`. ATNS entity, reference, relationship-row and sample dataset IRIs are currently treated as preserved data resources, using bases such as `https://data.idnau.org/pid/resource/atns/entity/`, `https://data.idnau.org/pid/resource/atns/reference/`, `https://data.idnau.org/pid/resource/atns/entity-relationship/` and `https://data.idnau.org/pid/resource/atns/sample/`. IRI suffixes use deterministic UUIDs, such as `atns-entity:34524ede-2abc-50f1-af30-8493753c928e`, rather than source database identifiers. Do not duplicate these HTTP PID IRIs as `schema:identifier` nodes.

Legacy ATNS identifiers are preserved separately as source-system values. For example, the public EID `A003259` is recorded with `atns:eid "A003259"^^xsd:token`, the source `Entities.EntityID` value `24` is recorded with `atns:sourceEntityId 24`, source `Refs.RefID` values are recorded with `atns:sourceReferenceId`, and source `Entity_Entity.Entity_EntityID` values are recorded with `atns:sourceRelationshipId`. Use `schema:identifier "..."^^xsd:token` only if a later sample needs a non-HTTP catalogue identifier that is not already covered by one of these preservation properties. The `https://data.idnau.org/pid/org/` and `https://data.idnau.org/pid/person/` bases are reserved for later first-class organisation and person identifiers, rather than being used for every legacy ATNS entity row that happens to describe an organisation or person.

Agreement-like distinctions such as framework agreement, funding agreement, ILUA, treaty, deed of settlement and settlement agreement appear in the source as subcategories. For now the sample models those as `atns:subcategory` links. This avoids prematurely deciding whether they are separate RDF classes, legal-document genres, negotiated-process types, or public-display facets.

Entity-to-entity relationships are represented as relationship nodes. This preserves the source `Entity_EntityID`, the subject entity, the object entity and the ATNS relationship-type concept. It also leaves room to attach provenance or confidence later.

Entity-to-reference links use `dcterms:references` in the simple sample when the only required assertion is that an entity references a source. The ATNS source also records reference-link roles such as `Primary`; model `Entity_Refs` rows as qualified relationship nodes when the row identity, role, provenance, ordering or uncertainty needs to be preserved. In that qualified form, keep a direct `dcterms:references` triple as a convenience assertion only if it does not contradict the qualified node.

## Sensitivity note

The sample intentionally uses public, non-deleted entity and reference rows only. It does not include attachment/document binaries or raw legal documents, because project context indicates some source materials may have been internal-only and not intended for public release.
