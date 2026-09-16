# Provisional ODRL modelling for ATNS agreements

## Status

This is an exploratory design note, not an authoritative conversion specification. It records a proposed path for enriching selected ATNS agreement records as ODRL policy expressions, a provisional vocabulary of agreement-related actions, and the Prez behaviour needed to present the resulting graph coherently.

The central modelling proposal is that a sufficiently enriched ATNS record may use one stable IRI and be typed both `schema:CreativeWork` and `odrl:Agreement`. A separate ODRL policy resource is no longer the preferred design.

The ODRL statements proposed here are project-authored interpretations. They are not part of the recovered ATNS source model, are not authorised transcriptions of operative legal agreements, and must not be generated indiscriminately from ambiguous text.

The action IRIs use `https://example.org/odrl/action/` deliberately. They are placeholders for discussion and must not be treated as published IDN or W3C vocabulary terms.

## Decision hypothesis

An ATNS agreement record begins as a preserved information resource:

```turtle
<ATNS-record-IRI>
    a
        atns:Entity ,
        schema:CreativeWork ;
    schema:additionalType catobjtyp:Agreement ;
.
```

After reviewed enrichment establishes at least one ODRL rule, its parties, action and any applicable target, the same resource may additionally become an ODRL Agreement:

```turtle
<ATNS-record-IRI>
    a
        atns:Entity ,
        schema:CreativeWork ,
        odrl:Agreement ;
    schema:additionalType catobjtyp:Agreement ;
    odrl:obligation <reviewed-duty-IRI> ;
.
```

This is semantically defensible only when the resource is understood as an enriched, machine-readable information object that now carries an ODRL policy expression. The `odrl:Agreement` type is not another loose classification for every agreement-like ATNS record.

The [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/) defines an Agreement as a Policy containing Rules granted from assigner to assignee Parties. A Policy must contain at least one Permission, Prohibition or Obligation. Accordingly, an ATNS record must not be typed `odrl:Agreement` until the minimum supported rule structure exists.

## Source, interpretation and authority

Multiple RDF types do not remove the distinction between recovered evidence and later interpretation. The graph must preserve that distinction through maintained source and enrichment files, named graphs, provenance, review metadata or another explicit project convention.

The proposed lifecycle is:

```text
preserved ATNS XML
    └── reproducible migration
        └── ATNS RDF CreativeWork
            └── reviewed enrichment on the same resource IRI
                ├── odrl:Agreement
                ├── ODRL Rules
                ├── resolved Parties
                ├── governed Actions
                └── supported Targets and Constraints
```

The preserved XML remains immutable evidence of the legacy system. If canonical authority moves to curated RDF, subsequent ODRL assertions become part of the governed RDF record and must not be erased by rerunning the legacy converter. The proposed authority transition is addressed separately in [ADR-0001: Adopt curated RDF as the operational source of truth](adr/0001-curated-rdf-operational-source-of-truth.md).

## Identity and common metadata

The combined resource should retain one canonical `schema:name` and `schema:description`. ODRL does not require a competing title or description for the Policy.

In ODRL JSON-LD, `uid` supplies the resource identity. In RDF/Turtle, the subject IRI already performs that role; a duplicate `odrl:uid` statement should not be added merely because the resource acquires an ODRL type.

Names and descriptions may be supplied for individual Rules, Party Collections and locally governed Actions when they help people understand the graph. They should not compete with the canonical title of the root ATNS resource.

## Reciprocal parties

An agreement commonly has multiple parties, and the direction of an individual permission or obligation may be unclear in the ATNS summary and body text. Earlier ATNS analysis found many candidate directional sentences but very few cases in which an assigner, assignee, action and target could all be identified confidently.

A potentially useful hypothesis is that many agreements contain reciprocal commitments: the parties collectively confer and assume responsibilities - an agreement is 'reached' between parties. For a deliberately general mutual obligation, the same `odrl:PartyCollection` could occupy both the `odrl:assigner` and `odrl:assignee` roles. This avoids inventing unsupported directionality while preserving the proposition that identified parties participate on both sides of the agreement relationship.

This compact pattern does not necessarily entail that every member assigns every action to every other member under current ODRL processor semantics. It remains a use case for the ODRL refresh work. Where clause-level direction is known, separate directional Rules are preferable.

Every resolved party should be typed `odrl:Party` and, where supported, also `schema:Person` or `schema:Organization`. Where the kind of agent cannot yet be distinguished, use `prov:Agent` rather than guessing.

## Spatial coverage and ODRL targets

`schema:spatialCoverage` and `odrl:target` express different relationships and may both be retained when both are true.

- `schema:spatialCoverage` means that the CreativeWork concerns or applies to a place.
- `odrl:target` means that an identifiable Asset is governed by a particular ODRL Rule.

A mapped agreement area should remain `schema:spatialCoverage` even when it cannot safely be treated as a Rule target. Add `odrl:target` only when the evidence supports the stronger assertion that the Rule operates on that area or another identified Asset.

Prefer placing `odrl:target` on the applicable Permission, Prohibition or Duty. A compact Policy-level target is appropriate only when it is deliberately shared by every Rule and can be expanded according to the ODRL compact-policy rules.

A target area may be typed both `geo:Feature` and `odrl:Asset` when the governed asset is genuinely the identified real-world area. If the Rule instead governs a legal interest, activity, document or service associated with that area, model that asset rather than treating the map feature as a convenient substitute.

## Wickham Motorcross ILUA example

The public source record is [Wickham Motorcross Indigenous Land Use Agreement (ILUA)](https://data.idnau.org/pid/resource/00129161-6f7d-5a0c-b270-2238ccaf75e5). Its reviewed spatial coverage is [NNTT feature WI2011-008](https://data.idnau.org/pid/nntt/WI2011-008).

The structured ATNS relationships identify Ngarluma Aboriginal Corporation RNTBC and the State of Western Australia as Signatories. The descriptive text names other participants, demonstrating that the structured party set may be incomplete. No Party Collection should be represented as complete until that discrepancy has been reviewed.

### Combined resource sketch

```turtle
PREFIX atns: <https://linked.data.gov.au/def/atns/model/>
PREFIX catobjtyp: <https://data.idnau.org/pid/vocab/cat-obj-types/>
PREFIX idn-resource: <https://data.idnau.org/pid/resource/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX odrl-action: <https://example.org/odrl/action/>
PREFIX schema: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

idn-resource:00129161-6f7d-5a0c-b270-2238ccaf75e5
    a
        atns:Entity ,
        odrl:Agreement ,
        schema:CreativeWork ;
    atns:sourceEntityId "5618"^^xsd:token ;
    schema:additionalType catobjtyp:Agreement ;
    schema:description
        "Public ATNS description of the agreement. The ODRL statements on this resource are a reviewed interpretation and not an authoritative transcription of the operative agreement."@en ;
    schema:name "Wickham Motorcross Indigenous Land Use Agreement (ILUA)"@en ;
    schema:spatialCoverage <https://data.idnau.org/pid/nntt/WI2011-008> ;
    odrl:obligation idn-resource:wickham-motorcross-mutual-obligation ;
.

idn-resource:wickham-motorcross-mutual-obligation
    a odrl:Duty ;
    odrl:action odrl-action:fulfil-agreement-commitments ;
    odrl:assigner idn-resource:wickham-motorcross-parties ;
    odrl:assignee idn-resource:wickham-motorcross-parties ;
    odrl:target <https://data.idnau.org/pid/nntt/WI2011-008> ;
    schema:description
        "The identified parties are provisionally represented as mutually responsible for fulfilling their respective commitments concerning the agreement area."@en ;
    schema:name "Mutual obligation to fulfil the agreement"@en ;
.

idn-resource:wickham-motorcross-parties
    a odrl:PartyCollection ;
    schema:description
        "A provisional collection of parties established from reviewed ATNS Signatory relationships; completeness must be assessed against the public text and supporting sources."@en ;
    schema:hasPart
        idn-resource:317d807c-63df-5f9f-8218-6498ba52c192 ,
        idn-resource:eb6b6bc9-ee8f-53f9-aecb-c53787816cc9 ;
    schema:name "Identified Wickham Motorcross ILUA signatories"@en ;
.

idn-resource:317d807c-63df-5f9f-8218-6498ba52c192
    a
        odrl:Party ,
        schema:Organization ;
    odrl:partOf idn-resource:wickham-motorcross-parties ;
    schema:name "Ngarluma Aboriginal Corporation RNTBC"@en ;
.

idn-resource:eb6b6bc9-ee8f-53f9-aecb-c53787816cc9
    a
        odrl:Party ,
        schema:Organization ;
    odrl:partOf idn-resource:wickham-motorcross-parties ;
    schema:name "State of Western Australia"@en ;
.
```

The readable child IRIs in this sketch are placeholders. Production Rules and Party Collections require stable reviewed IRIs following the adopted IDN identifier policy.

A general reciprocal commitment is represented here with `odrl:obligation`. A Duty nested under an `odrl:permission` instead acts as a condition that must be fulfilled for that Permission and should be used only when the source supports that meaning.

## Provisional agreement-related action vocabulary

The action scheme remains a strong design proposal. It gives recurring agreement actions stable identifiers, human-readable definitions and governance independently of any particular ATNS record. It may ultimately support domains beyond ATNS, but that scope should be decided through vocabulary governance rather than assumed from the examples.

The scheme is not extracted directly from an ATNS database table. Its initial concepts have different evidentiary bases:

| Action | Basis | Current status |
| --- | --- | --- |
| `fulfil-agreement-commitments` | Derived from the reciprocal-party model | Cross-domain proposal |
| `manage-asset` | Grounded in reserve and management provisions | ATNS-evidenced candidate |
| `provide-resources` | Suggested by records concerning funding, personnel and services | ATNS-inferred candidate |
| `report-performance` | Suggested by reporting, milestone and performance provisions | ATNS-inferred candidate |
| `protect-cultural-heritage` | Strongly characteristic of ATNS subject matter | ATNS-oriented proposal |
| `consult` | Common in agreements and other policy domains | Cross-domain proposal |
| `cooperate` | Common in agreements and other policy domains | Cross-domain proposal |

Before publication, public ATNS summaries and bodies should be analysed for recurring action phrases and reviewed examples. Existing ODRL actions must also be considered before minting terms with overlapping meanings.

### Concept scheme sketch

```turtle
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX odrl-action: <https://example.org/odrl/action/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

odrl-action:
    a skos:ConceptScheme ;
    schema:dateCreated "2026-09-15"^^xsd:date ;
    schema:dateModified "2026-09-16"^^xsd:date ;
    skos:definition
        "Provisional actions used to express responsibilities and permissions arising from negotiated agreements."@en ;
    skos:hasTopConcept odrl-action:fulfil-agreement-commitments ;
    skos:historyNote
        "Created as an exploratory vocabulary for reviewed ODRL enrichment. Its terms are not assertions by the ATNS source owners and are not part of the normative ODRL vocabulary."@en ;
    skos:prefLabel "Agreement-related ODRL actions"@en ;
.

odrl-action:fulfil-agreement-commitments
    a
        odrl:Action ,
        skos:Concept ;
    skos:definition
        "Perform the commitments for which a party is responsible under an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:narrower
        odrl-action:cooperate ,
        odrl-action:consult ,
        odrl-action:manage-asset ,
        odrl-action:provide-resources ,
        odrl-action:protect-cultural-heritage ,
        odrl-action:report-performance ;
    skos:prefLabel "fulfil agreement commitments"@en ;
    skos:topConceptOf odrl-action: ;
.

odrl-action:cooperate
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Cooperate with other parties in carrying out an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "cooperate"@en ;
.

odrl-action:consult
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Consult the parties or communities identified by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "consult"@en ;
.

odrl-action:manage-asset
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Manage land, infrastructure or another asset in accordance with an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "manage asset"@en ;
.

odrl-action:provide-resources
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Provide funding, personnel, services or other resources required by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "provide resources"@en ;
.

odrl-action:protect-cultural-heritage
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Protect cultural heritage, places, knowledge or objects in accordance with an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "protect cultural heritage"@en ;
.

odrl-action:report-performance
    a odrl:Action, skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition "Report progress, performance or outcomes required by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "report performance"@en ;
.
```

The SKOS hierarchy supports human navigation and vocabulary presentation. It does not by itself provide formal action-subsumption semantics to an ODRL evaluator. If machine-operational relationships among Actions are required, their semantics must be defined separately and tested against `odrl:includedIn`, `odrl:implies` and the future ODRL model.

## Prez presentation hypothesis

The combined resource should render as one coherent page. ODRL detail should appear in a visually separate card so readers can distinguish preserved descriptive metadata from the reviewed policy interpretation.

```text
ATNS agreement page
├── Overview
│   ├── canonical name and description
│   ├── dates, access status and source identifiers
│   └── interpretation status and provenance
├── ATNS classification
│   ├── category and subcategory
│   └── subject keywords
├── ODRL interpretation                 [separate card]
│   ├── obligations, permissions and prohibitions
│   ├── action definitions
│   ├── assigners and assignees
│   ├── targets and constraints
│   └── interpretation warning
├── Agreement area
│   ├── on-demand map from schema:spatialCoverage
│   └── indication when the same feature is a Rule target
└── References and provenance
```

The profile determines which triples Prez returns. PrezUI determines ordering, cards, headings, collapsible sections, warnings and map behaviour.

The current profile reflects the earlier separate-policy design: the ATNS profile traverses `dcterms:relation` to an ODRL resource, while another profile constrains `odrl:Agreement`. Before implementation, these should be replaced or consolidated into a combined-resource profile that:

- returns ordinary ATNS and schema.org predicates from the root resource;
- traverses its direct `odrl:permission`, `odrl:prohibition` and `odrl:obligation` Rules;
- returns Action labels and definitions;
- returns Party Collections, their members and useful agent labels;
- returns target labels and sufficient geometry for the on-demand map;
- avoids returning the complete coordinate detail in the initial human-readable view;
- gives PrezUI enough information to separate ODRL assertions visually from source-derived metadata.

Because the same node matches both `atns:Entity` and `odrl:Agreement`, profile selection and precedence must be tested in Prez before replacing the deployed configuration. `shext:allPredicateValues` may continue to provide common root metadata, while explicit property paths bring the nested ODRL subgraph into the response.

## Publishing and rendering ODRL Actions

The proposed publication pattern is:

- the vocabulary file has one `skos:ConceptScheme` main entity;
- each Action is typed both `odrl:Action` and `skos:Concept`;
- each Action is linked to the scheme with `skos:inScheme`;
- the catalogue manifest declares `skos:ConceptScheme` as the artifact's main-entity class;
- Prez renders Actions through vocabulary/concept support;
- a dedicated `odrl:Action` object profile is added only if direct Action pages require behaviour beyond the normal concept presentation.

Ingestion and presentation remain separate concerns. The catalogue manifest identifies the main entity in the vocabulary artifact; the Prez profile determines what is returned and how individual resources are presented.

## Alternative directional expansion

If a source clause clearly identifies direction, the compact mutual-duty hypothesis should be expanded into separate Rules. For parties A and B, one Duty may be assigned by A to B and another by B to A. The Rules may use different Actions and Targets because reciprocal agreements do not imply identical commitments.

The dual-role Party Collection is most defensible when all of the following hold:

1. The evidence establishes that the identified entities are parties or signatories.
2. The statement being represented is intentionally general and reciprocal.
3. Clause-level direction cannot be established reliably or is deliberately outside scope.
4. The resource is labelled as a reviewed interpretation rather than an authoritative transcription.

## Candidate enrichment workflow

1. Select a public ATNS CreativeWork soft-typed as an Agreement.
2. Confirm that the record is eligible for enrichment and carries no unresolved access or confidentiality concern.
3. Identify structured Signatory relationships and reconcile related entities with stable organization or person IRIs.
4. Compare structured parties with names in the public summary, body and supporting sources; flag incomplete or ambiguous party sets.
5. Extract candidate action phrases without asserting ODRL Rules automatically.
6. Reuse an existing ODRL Action where the semantics fit; otherwise propose a governed Action concept with evidence.
7. Determine whether each statement is a Permission, Prohibition, standalone Obligation, or Duty attached to a Permission.
8. Assert assigner and assignee direction only when supported. Use the reciprocal Party Collection hypothesis only for genuinely mutual general commitments.
9. Add `odrl:target` only for the Asset governed by the Rule; retain `schema:spatialCoverage` independently.
10. rdf:Type the object of odrl:Target as odrl:Asset, if not already typed this way.
10. Record evidence, reviewer, confidence, interpretation status and derivation provenance.
11. Add `odrl:Agreement` to the existing CreativeWork only after the minimum ODRL structure passes review and validation.

## Minimum publication gate

An ATNS record should not be published as `odrl:Agreement` unless it has:

- at least one reviewed Permission, Prohibition or Obligation;
- an identified Action for every Rule;
- an assigner and assignee supported for the Agreement's Rules;
- a target wherever the Action requires an identifiable Asset;
- stable IRIs for Rules, Parties, Party Collections, Actions and Targets;
- recorded evidence and reviewer responsibility;
- an explicit indication that the ODRL layer is an interpretation unless it is an authoritative transcription;
- successful RDF and applicable SHACL validation.

## Open questions

- Does the same Party Collection as assigner and assignee express the intended reciprocity, or is pairwise expansion or a future ODRL construct required?
- Should the first ATNS prototype use a general Obligation, clause-level Rules, or both at different confidence levels?
- Which candidate Actions recur often enough to justify governed vocabulary terms?
- Should the Action scheme remain agreement-specific, become a broader IDN policy-action vocabulary, or be proposed to the ODRL community?
- What provenance granularity is needed for individual Rules and their supporting text?
- How should incomplete party sets appear without implying that known Signatories are the complete legal party list?
- When does a spatial feature identify the governed Asset closely enough to be an `odrl:target`?
- How should Prez choose one combined profile when the root resource matches multiple classes?
- Which validation rules belong to an ATNS-specific ODRL profile and which belong to general ODRL conformance?

## Proposed next work

1. Select one public, well-evidenced agreement as the combined-resource prototype.
2. Review the provisional Action scheme with ATNS, IDN and ODRL stakeholders.
3. Define a small ATNS ODRL application profile and SHACL publication gate.
4. Prototype the combined Prez response graph and visually separate ODRL card.
5. Compare the prototype with the current separate-policy demonstration before changing production data or profiles.
6. Submit the reciprocal-party scenario and action-vocabulary experience as use cases for the ODRL refresh.

The examples and rationale should remain version-controlled here. GitHub issues can record implementation scope and responsibility without becoming the only copy of the evolving model.
