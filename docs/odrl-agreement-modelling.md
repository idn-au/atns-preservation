# Provisional ODRL modelling for ATNS agreements

## Status

This is an exploratory design note, not an authoritative conversion specification. It records a possible path from preserved ATNS agreement records to richer `odrl:Agreement` interpretations, a provisional vocabulary of agreement-related actions, and the Prez profile behaviour needed to present the resulting graph coherently.

The ODRL statements proposed here are project-authored interpretations. They are not part of the recovered ATNS source model, are not authorised transcriptions of operative legal agreements, and should not be generated indiscriminately from ambiguous text.

The action IRIs use `https://example.org/odrl/action/` deliberately. They are placeholders for discussion and must not be treated as published IDN vocabulary terms.

## Motivation

An agreement commonly has multiple parties, and the direction of an individual permission or obligation may be unclear in the ATNS summary and body text. Earlier ATNS analysis found many candidate directional sentences but very few cases in which an assigner, assignee, action and target could all be identified confidently.

A potentially useful distinction is that an agreement may represent reciprocal commitments: the parties collectively confer and assume responsibilities. For a deliberately general mutual obligation, the same `odrl:PartyCollection` could therefore occupy both the `odrl:assigner` and `odrl:assignee` roles. This avoids inventing unsupported directionality while preserving the fact that identified parties participate on both sides of the agreement relationship.

This compact pattern does not necessarily entail that every member assigns every action to every other member under current ODRL processor semantics. That question should be tested as a use case in the ODRL refresh work. Where clause-level direction is known, separate directional rules may remain preferable.

## Preservation and interpretation boundary

The preserved ATNS entity remains a `schema:CreativeWork` and `atns:Entity`, soft-typed as an Agreement using the IDN Catalogued Object Types vocabulary. A separately minted policy resource represents the interpretive ODRL graph.

The boundary is:

```text
preserved ATNS record
    └── dcterms:source of
        provisional odrl:Agreement
            └── odrl:obligation
                ├── odrl:action
                ├── odrl:assigner ─┐
                ├── odrl:assignee ─┴── same PartyCollection
                └── odrl:target
```











An `odrl:Agreement` may not need to be also typed as`schema:CreativeWork`

 The preserved
 record is evidence for the interpretation; it is not automatically the asset governed by the ODRL rule. A geographic feature can be a target where the rule genuinely concerns the agreement area. If an authoritative agreement document later receives an IRI, it may become another source or target depending on the action being expressed.

A general reciprocal commitment is represented here with `odrl:obligation`. A duty nested under an `odrl:permission` would instead operate as a condition attached to that permission and should only be used when that is what the source means.

## Wickham Motorcross ILUA example

The preserved source record is [Wickham Motorcross Indigenous Land Use Agreement (ILUA)](https://data.idnau.org/pid/resource/00129161-6f7d-5a0c-b270-2238ccaf75e5). Its mapped spatial coverage is [NNTT feature WI2011-008](https://data.idnau.org/pid/nntt/WI2011-008).

The current structured ATNS relationships identify these entities as Signatories:

- [Ngarluma Aboriginal Corporation RNTBC](https://data.idnau.org/pid/resource/317d807c-63df-5f9f-8218-6498ba52c192)
- [State of Western Australia](https://data.idnau.org/pid/resource/eb6b6bc9-ee8f-53f9-aecb-c53787816cc9)

The descriptive text also names the Minister for Lands and the Shire of Roebourne. Those mentions show that the structured party set may be incomplete. They should not be silently added to the ODRL party collection until their identities and roles have been reviewed.

### Provisional agreement graph

```turtle
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX idn-policy: <https://data.idnau.org/pid/policy/>
PREFIX idn-resource: <https://data.idnau.org/pid/resource/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX odrl-action: <https://example.org/odrl/action/>
PREFIX schema: <https://schema.org/>

idn-policy:wickham-motorcross-ilua
    a
        odrl:Agreement ,
        schema:CreativeWork ;   # not needed if odrl:Agreement added as a main class
    dcterms:source
        idn-resource:00129161-6f7d-5a0c-b270-2238ccaf75e5 ;
    odrl:obligation
        idn-policy:wickham-motorcross-ilua-mutual-obligation ;
    odrl:uid idn-policy:wickham-motorcross-ilua ;
    schema:conditionsOfAccess "Public"@en ;
    schema:description
        "A provisional ODRL interpretation derived from the preserved ATNS record. It represents the currently identified signatories as jointly assigning and assuming a general obligation. It is not an authoritative transcription of the operative agreement."@en ;
    schema:keywords "Demo" ;
    schema:name
        "Wickham Motorcross Indigenous Land Use Agreement — provisional ODRL interpretation"@en ;
.

idn-policy:wickham-motorcross-ilua-mutual-obligation
    a odrl:Duty ;
    odrl:action odrl-action:fulfil-agreement-commitments ;
    odrl:assigner idn-policy:wickham-motorcross-ilua-parties ;
    odrl:assignee idn-policy:wickham-motorcross-ilua-parties ;
    odrl:target <https://data.idnau.org/pid/nntt/WI2011-008> ;
    odrl:uid idn-policy:wickham-motorcross-ilua-mutual-obligation ;
    schema:description
        "The parties are mutually responsible for fulfilling their respective commitments concerning the registered agreement area."@en ;
    schema:name "Mutual obligation to fulfil the agreement"@en ;
.

idn-policy:wickham-motorcross-ilua-parties
    a odrl:PartyCollection ;
    odrl:uid idn-policy:wickham-motorcross-ilua-parties ;
    schema:description
        "The parties represented by structured ATNS Signatory relationships. Other parties mentioned in the descriptive text require further identity resolution."@en ;
    schema:hasPart
        idn-resource:317d807c-63df-5f9f-8218-6498ba52c192 ,
        idn-resource:eb6b6bc9-ee8f-53f9-aecb-c53787816cc9 ;
    schema:name "Identified Wickham Motorcross ILUA signatories"@en ;
.

idn-resource:317d807c-63df-5f9f-8218-6498ba52c192
    a
        odrl:Party ,
        schema:Organization ;
    odrl:partOf idn-policy:wickham-motorcross-ilua-parties ;
    odrl:uid idn-resource:317d807c-63df-5f9f-8218-6498ba52c192 ;
    schema:name "Ngarluma Aboriginal Corporation RNTBC"@en ;
.

idn-resource:eb6b6bc9-ee8f-53f9-aecb-c53787816cc9
    a
        odrl:Party ,
        schema:Organization ;
    odrl:partOf idn-policy:wickham-motorcross-ilua-parties ;
    odrl:uid idn-resource:eb6b6bc9-ee8f-53f9-aecb-c53787816cc9 ;
    schema:name "State of Western Australia"@en ;
.
```

### Party typing

Every party should be typed `odrl:Party` and, where supported by reviewed source data or identity reconciliation, also typed `schema:Person` or `schema:Organization`.

Where the party category cannot yet be distinguished, use the broader `prov:Agent` rather than guessing:

```turtle
PREFIX idn-policy: <https://data.idnau.org/pid/policy/>
PREFIX idn-resource: <https://data.idnau.org/pid/resource/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <https://schema.org/>

idn-resource:unresolved-party
    a
        odrl:Party ,
        prov:Agent ;
    odrl:partOf idn-policy:wickham-motorcross-ilua-parties ;
    odrl:uid idn-resource:unresolved-party ;
    schema:name "Party name as recorded by ATNS"@en ;
.
```

The placeholder IRI above is illustrative only. Production data must use a stable reviewed IRI and preserve the relevant ATNS source identifier.

## Provisional agreement-related action vocabulary

The following scheme is a design hypothesis, not a vocabulary extracted directly from the ATNS database. Its initial concepts have different evidentiary bases:

| Action | Basis | Current status |
| --- | --- | --- |
| `fulfil-agreement-commitments` | Derived from the proposed reciprocal-party model | Cross-domain proposal |
| `manage-asset` | Grounded in the Wickham agreement's reserve and management provisions | ATNS-evidenced candidate |
| `provide-resources` | Suggested by ATNS records describing funding, personnel and service delivery | ATNS-inferred candidate |
| `report-performance` | Suggested by ATNS records containing reporting, milestones and performance requirements | ATNS-inferred candidate |
| `protect-cultural-heritage` | Strongly characteristic of the ATNS domain but not yet systematically extracted | ATNS-oriented proposal |
| `consult` | Applicable across many agreement domains | Cross-domain proposal |
| `cooperate` | Applicable across many agreement domains | Cross-domain proposal |

Before publication, candidate actions can be tested by mining public Agreement summaries and bodies for recurring verb phrases and recording occurrence counts and example resource IRIs. Existing ODRL actions should also be reviewed before minting overlapping terms.

### Concept scheme sketch

```turtle
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX odrl-action: <https://example.org/odrl/action/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

odrl-action:
    a skos:ConceptScheme ;
    skos:definition
        "Provisional actions used to express responsibilities and permissions arising from negotiated agreements."@en ;
    skos:hasTopConcept odrl-action:fulfil-agreement-commitments ;
    skos:historyNote
        "Created as an exploratory vocabulary for modelling preserved ATNS agreement records with ODRL. Its terms are not assertions by the ATNS source owners and are not currently part of the normative ODRL vocabulary."@en ;
    skos:prefLabel "Agreement-related ODRL actions"@en ;
    schema:name "Agreement-related ODRL actions"@en ;
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
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Cooperate with other parties in carrying out an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "cooperate"@en ;
.

odrl-action:consult
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Consult the parties or communities identified by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "consult"@en ;
.

odrl-action:manage-asset
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Manage land, infrastructure or another asset in accordance with an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "manage asset"@en ;
.

odrl-action:provide-resources
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Provide funding, personnel, services or other resources required by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "provide resources"@en ;
.

odrl-action:protect-cultural-heritage
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Protect cultural heritage, places, knowledge or objects in accordance with an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "protect cultural heritage"@en ;
.

odrl-action:report-performance
    a
        odrl:Action ,
        skos:Concept ;
    skos:broader odrl-action:fulfil-agreement-commitments ;
    skos:definition
        "Report progress, performance or outcomes required by an agreement."@en ;
    skos:inScheme odrl-action: ;
    skos:prefLabel "report performance"@en ;
.
```

The SKOS hierarchy supports human navigation and vocabulary presentation. It must not be assumed to provide formal action-subsumption semantics to an ODRL evaluator. If the ODRL refresh requires machine-operational relationships among actions, their semantics should be defined separately and tested against `odrl:includedIn` and other ODRL mechanisms.

## Prez presentation

The desired Agreement page should bring the `odrl:Agreement`, its `odrl:Duty`, its `odrl:PartyCollection`, the individual `odrl:Party` resources, the action and the target into one response graph. A possible page structure is:

```text
ODRL Agreement
├── description and source ATNS record
├── permissions, where present
├── obligations
│   └── mutual obligation
│       ├── action: fulfil agreement commitments
│       ├── assigner: identified signatory parties
│       │   ├── Ngarluma Aboriginal Corporation RNTBC
│       │   └── State of Western Australia
│       ├── assignee: the same identified signatory parties
│       └── target: WI2011-008 agreement area
└── link to full target details and on-demand map, where available
```

The profile determines which triples Prez returns. The PrezUI component still determines layout, headings, collapsible sections and map behaviour.

### Expanded Agreement profile sketch

```turtle
PREFIX altr-ext: <http://www.w3.org/ns/dx/connegp/altr-ext#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX prez: <https://prez.dev/>
PREFIX prof: <http://www.w3.org/ns/dx/prof/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shext: <http://example.com/shacl-extension#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

prez:OdrlAgreement
    a
        prof:Profile ,
        prez:ObjectProfile ,
        sh:NodeShape ;
    schema:identifier "odrl-agreement"^^xsd:token ;
    schema:name "ODRL Agreement presentation profile"@en ;
    schema:description
        "Presents an ODRL Agreement with its permissions, obligations, actions, party collections, parties and targets."@en ;
    altr-ext:constrainsClass odrl:Agreement ;
    altr-ext:hasDefaultResourceFormat "text/anot+turtle" ;
    altr-ext:hasResourceFormat
        "application/anot+ld+json" ,
        "application/ld+json" ,
        "text/anot+turtle" ,
        "text/turtle" ;
    sh:property [
        sh:path [
            sh:union (
                shext:allPredicateValues

                odrl:permission
                ( odrl:permission rdf:type )
                ( odrl:permission schema:name )
                ( odrl:permission schema:description )
                ( odrl:permission odrl:action )
                ( odrl:permission odrl:assigner )
                ( odrl:permission odrl:assignee )
                ( odrl:permission odrl:target )

                odrl:obligation
                ( odrl:obligation rdf:type )
                ( odrl:obligation schema:name )
                ( odrl:obligation schema:description )
                ( odrl:obligation odrl:action )
                ( odrl:obligation odrl:action rdf:type )
                ( odrl:obligation odrl:action skos:prefLabel )
                ( odrl:obligation odrl:action skos:definition )

                ( odrl:obligation odrl:assigner )
                ( odrl:obligation odrl:assigner rdf:type )
                ( odrl:obligation odrl:assigner schema:name )
                ( odrl:obligation odrl:assigner schema:description )
                ( odrl:obligation odrl:assigner schema:hasPart )
                ( odrl:obligation odrl:assigner schema:hasPart rdf:type )
                ( odrl:obligation odrl:assigner schema:hasPart schema:name )

                ( odrl:obligation odrl:assignee )
                ( odrl:obligation odrl:assignee rdf:type )
                ( odrl:obligation odrl:assignee schema:name )
                ( odrl:obligation odrl:assignee schema:description )
                ( odrl:obligation odrl:assignee schema:hasPart )
                ( odrl:obligation odrl:assignee schema:hasPart rdf:type )
                ( odrl:obligation odrl:assignee schema:hasPart schema:name )

                ( odrl:obligation odrl:target )
                ( odrl:obligation odrl:target rdf:type )
                ( odrl:obligation odrl:target schema:name )
                ( odrl:obligation odrl:target schema:description )
            )
        ]
    ] ;
.
```

The current `idn-prez4/prez-profiles.trig` appears to contain both `prez:odrl-agreement` and `prez:OdrlAgreement` with the same `dcterms:identifier`. Those definitions should be consolidated before this expanded profile is implemented.

## Publishing and rendering ODRL actions

An action does not need to be typed `schema:CreativeWork`. The preferred publication pattern is:

- the vocabulary file has one `skos:ConceptScheme` main entity;
- each action is typed both `odrl:Action` and `skos:Concept`;
- the action is linked to the scheme with `skos:inScheme`;
- the catalogue manifest declares `skos:ConceptScheme` as the artifact's main-entity class;
- Prez can render the actions through its vocabulary/concept support.

If direct object-profile rendering of `odrl:Action` resources is also wanted, the IDN index profile can select a dedicated action profile:

```turtle
PREFIX altr-ext: <http://www.w3.org/ns/dx/connegp/altr-ext#>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX prez: <https://prez.dev/>
PREFIX prof: <http://www.w3.org/ns/dx/prof/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX shext: <http://example.com/shacl-extension#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

prez:CustomIndexProfile
    altr-ext:hasNodeShape [
        a sh:NodeShape ;
        sh:targetClass odrl:Action ;
        altr-ext:hasDefaultProfile prez:OdrlActionProfile ;
    ] ;
.

prez:OdrlActionProfile
    a
        prof:Profile ,
        prez:ObjectProfile ,
        sh:NodeShape ;
    schema:identifier "odrl-action"^^xsd:token ;
    schema:name "ODRL Action presentation profile"@en ;
    schema:description
        "Presents an ODRL Action and its vocabulary relationships."@en ;
    altr-ext:constrainsClass odrl:Action ;
    altr-ext:hasDefaultResourceFormat "text/anot+turtle" ;
    sh:property [
        sh:path [
            sh:union (
                shext:allPredicateValues
                rdf:type
                skos:prefLabel
                skos:definition
                skos:broader
                skos:narrower
                skos:inScheme
            )
        ]
    ] ;
.
```

Ingestion and presentation are separate concerns. The catalogue manifest identifies the main entity in an artifact for KGM/Prez loading; `idn-prez4` profiles determine what is returned and how a class is profiled. For this vocabulary, the Concept Scheme should normally be the manifest main entity even though the member concepts are also `odrl:Action` resources.

## Alternative directional expansion

If a source clause clearly identifies direction, the compact mutual-duty pattern should be expanded into separate rules. For two parties A and B, that could mean one duty assigned by A to B and another assigned by B to A. The rules may use different actions and targets because reciprocal agreements do not imply that every party has identical commitments.

The dual-role PartyCollection is therefore most defensible when all of the following hold:

1. The source establishes that the identified entities are parties or signatories.
2. The statement being represented is intentionally general and reciprocal.
3. Clause-level direction cannot be established reliably or is deliberately outside scope.
4. The resource is labelled as an interpretation rather than an authoritative transcription.

## Candidate workflow for ATNS enrichment

1. Select a public Agreement-classified ATNS record.
2. Identify structured Signatory relationships and reconcile the related entities with stable organization or person IRIs.
3. Compare structured parties with names appearing in the public summary and body; flag missing or ambiguous parties.
4. Extract candidate action phrases from public text without asserting ODRL rules automatically.
5. Map a candidate phrase to an existing ODRL action where the semantics match exactly; otherwise propose a documented profile action.
6. Identify whether the statement is a permission, prohibition, standalone obligation or duty attached to a permission.
7. Assert direction only when supported. Use the reciprocal PartyCollection pattern only for genuinely mutual general commitments.
8. Link the ODRL interpretation to the preserved ATNS record with `dcterms:source`.
9. Use `odrl:target` only for the asset governed by that rule, not merely for any resource associated with the ATNS record.
10. Record reviewer, evidence, confidence and interpretation status before publication.

## Open questions

- Does using the same PartyCollection as both assigner and assignee entail the intended all-party reciprocity in ODRL, or is an explicit collection or pairwise semantic rule required?
- Should a reciprocal agreement use one general Duty, mirrored directional Duties, or a distinct agreement-level construct in a future ODRL model?
- Which candidate actions recur often enough in ATNS to justify controlled terms?
- Which candidates can reuse normative ODRL actions without changing the source meaning?
- Should the action scheme remain agreement-specific, become a broader IDN policy-action vocabulary, or become input to a future ODRL community vocabulary?
- What provenance pattern should connect each generated rule to the supporting ATNS text or source relationship rows?
- How should incomplete party sets be presented without implying that identified structured Signatories are the complete legal party list?
- When the target is a spatial feature, does its IRI identify the governed real-world area closely enough, or should a separate asset representing the agreement area be minted?
- Which parts of this pattern belong in an ATNS-specific ODRL profile and which are general ODRL requirements or best practices?

## Potential GitHub work items

This note can be refined before implementation and then divided into focused issues:

1. **ATNS modelling:** test reciprocal party roles and action candidates against a reviewed set of public ATNS agreements.
2. **IDN vocabulary:** decide whether to govern and publish an agreement or policy action vocabulary.
3. **IDN Prez:** consolidate and expand the ODRL Agreement profile, then design the Agreement page sections in PrezUI.
4. **ODRL refresh:** submit the reciprocal assigner/assignee Agreement scenario as a use case, including its compact and directional alternatives.

The detailed examples and evidence should remain version-controlled here. GitHub issues can then record decisions, implementation scope and responsibility without becoming the only copy of the evolving model.
