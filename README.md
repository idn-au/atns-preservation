# ATNS preservation

Data extracted from the Agreements, Treaties and Negotiated Settlements [website](https://www.atns.net.au)
.

## Reproducible conversion

The current public preservation sample can be regenerated from the private ATNS XML export through a checksum-verified XML-to-CSV extraction stage and declarative `rdfcon` YAML specifications. The generated RDF is accepted only when it is graph-identical to both the curated aggregate sample and the split publication files. Manual source updates are fail-closed: duplicate identities are rejected and missing, deleted or private published records are reported for removal review. See [Conversion process](docs/conversion.md) for the security boundary, update procedure, editorial inputs, commands and equivalence checks.

## Resource model

The preserved ATNS data is a graph rather than a set of isolated records. The
diagram below shows the principal connections, including how an external
creative work can cite an ATNS agreement. Boxes containing example values are
resources with their own IRIs; predicates are shown on the connecting arrows.
The shaded box with the dashed border is external to the ATNS model.

```mermaid
flowchart LR
    work["schema:CreativeWork"]
    agreement["atns:AgreementRecord; schema:name"]

    category["Category: e.g. Agreement"]
    country["Country: e.g. Australia"]
    subject["Subject: e.g. Agriculture"]
    subcategory["Subcategory: e.g. Litigated Determination"]

    reference["Reference: schema:name; schema:url"]
    referenceType["Reference type: e.g. Journal Article"]

    relationship["Relationship record: atns:EntityRelationship"]
    relatedEntity["atns:Entity; e.g. schema:Organization; schema:name"]
    relationshipType["Relationship type: e.g. Signatory"]

    work -->|schema:citation| agreement

    agreement -->|atns:category| category
    agreement -->|atns:country| country
    agreement -->|schema:keywords| subject
    agreement -->|atns:subcategory| subcategory

    agreement -->|dcterms:references| reference
    reference -->|atns:referenceType| referenceType

    relationship -->|atns:subjectEntity| agreement
    relationship -->|atns:objectEntity| relatedEntity
    relationship -->|atns:relationshipType| relationshipType

    classDef external fill:#fff3cd,stroke:#9a6700,color:#3d2a00,stroke-width:2px,stroke-dasharray:5 3
    class work external
```

`EntityRelationship` is deliberately represented as a resource, rather
than as a direct edge between two entities. This preserves the original ATNS
relationship row and allows its type and source identifier to be described.
The subject and object directions are those recorded by ATNS; any source entity
may occur in either position.

Every record from the legacy ATNS `Entities` table is typed `atns:Entity`. Records
with the source category `Agreement` are more specifically typed
`atns:AgreementRecord`, a subclass of `atns:Entity`. The original ATNS category
concept is retained alongside the class assertion. `atns:AgreementRecord` records
the ATNS source-system type and does not entail `odrl:Agreement`. A published
external class such as `schema:Organization` may also be asserted where the
mapping is clear. Classification values such as `Category`, `Country` and
`Relationship type` remain resources, allowing stable identifiers and labels to
be reused across records.

## Integration with IDN catalogues

The Resource model supports linking and navigation between 
- Creative works that cite an `atns:Entity`, such as an agreement
- Agreements referring to other creative works

See example [‘Changing the Mix’](https://data.idnau.org/pid/resource/f73b42cf-d39b-406c-a8c5-10a01ae0594e
) in the IDN Demonstration Catalogue.

Copyright ATNS 2020.  ATNS is maintained by the Indigenous Studies Unit at The University of Melbourne. 
This work is licensed under a Creative Commons Attribution-Non Commercial-No Derivatives 4.0 International License.
