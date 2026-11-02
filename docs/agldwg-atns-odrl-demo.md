# AGLDWG ATNS ODRL demo

## Working status

This is an incremental working document for a proposed 20-minute presentation to the Australian Government Linked Data Working Group. It will evolve as the Yamatji Nation Indigenous Land Use Agreement demonstration is completed and tested.

The presentation should distinguish clearly between preserved ATNS source metadata, reviewed IDN enrichment, and authoritative legal interpretation. The demonstration is exploratory and does not claim to reproduce the legal agreement exhaustively.

## Presentation objective

Demonstrate how a preserved ATNS agreement record can remain a `schema:CreativeWork` while being enriched, on the same stable IRI, as a machine-readable `odrl:Agreement`.

The example should show that linked-data publication allows us to:

- preserve the historical ATNS description and source identifiers;
- reuse canonical identifiers for organisations, places and other entities;
- express selected agreement obligations as structured ODRL rules;
- distinguish transferred assets from surrendered rights;
- use a small governed action vocabulary for concepts not supplied by normative ODRL; and
- present the enriched graph coherently on one Prez page.

## Proposed 20-minute structure

| Time | Section | Purpose |
|---:|---|---|
| 0–2 minutes | Why ATNS matters | Introduce the preservation problem and the value of retaining agreement records as linked data. |
| 2–5 minutes | Preservation and enrichment architecture | Explain the immutable XML source, reproducible RDF conversion, reviewed enrichment overlays and publication layer. |
| 5–8 minutes | Combined CreativeWork and ODRL Agreement | Explain why the same resource IRI is typed as both `schema:CreativeWork` and `odrl:Agreement`. |
| 8–14 minutes | Live Yamatji demonstration | Navigate the agreement, its obligations, parties, actions, assets, spatial coverage and supporting references in Prez. |
| 14–17 minutes | Modelling decisions | Discuss reciprocal parties, surrender versus transfer, action-vocabulary extension and canonical agent reuse. |
| 17–20 minutes | Questions for AGLDWG | Canvass unresolved patterns, including how to express a government acting through a particular department. |

## Demonstration resource

The principal example is the **Yamatji Nation Indigenous Land Use Agreement (ILUA)**:

```turtle
<https://data.idnau.org/pid/resource/e450e34e-9806-5ed5-ba85-37a01c121064>
    a
        atns:Entity ,
        odrl:Agreement ,
        schema:CreativeWork ;
    schema:additionalType
        <https://data.idnau.org/pid/vocab/cat-obj-types/Agreement> ;
.
```

The existing CreativeWork retains its title, summary, body, references, ATNS identifiers and spatial coverage. The ODRL enrichment adds reviewed rules to the same resource rather than creating a separate policy object with a competing identity.

## Initial obligation examples

The first draft selects four obligations that can be supported from identifiable clauses in the executed agreement:

1. Provide the Yamatji Nation compensation and benefits package.
2. Surrender native-title rights and interests in the Surrender Area.
3. Transfer the Corporate Headquarters property.
4. Restore and protect water-cultural sites.

These examples allow the demonstration to distinguish:

- `odrl:compensate` from locally governed agreement actions;
- `odrl:transfer`, where ownership passes between parties, from `odrl-action:surrender-rights`, where rights are relinquished or extinguished; and
- a general agreement area expressed through `schema:spatialCoverage` from the particular `odrl:Asset` governed by an individual rule.

## Agent identity and reuse

ODRL enrichment should reuse canonical agent IRIs instead of minting duplicate organisations or people. The ATNS enrichment workflow therefore checks the current IDN Agents Database authoring data before proposing a new agent.

An enduring organisation or person is maintained in the Agents Database as `schema:Organization` or `schema:Person`. Its contextual `odrl:Party` assertion is maintained with the reviewed agreement enrichment. Both graphs use the same canonical IRI, so the combined knowledge graph has both types without duplicating the agent.

For the State-level party in the Yamatji example, the proposed canonical identifier is:

```turtle
<https://ror.org/00wqdbc63>
    a schema:Organization ;
    schema:alternateName "State of Western Australia"@en ;
    schema:name "Government of Western Australia"@en ;
    schema:url "https://www.wa.gov.au/"^^xsd:anyURI ;
.
```

The GeoNames identifier `https://sws.geonames.org/2058645/` denotes the geographic and administrative territory of Western Australia. It is not interchangeable with the ROR organisation and should not be used as an ODRL party.

## Discussion point: the State acting through a department

The executed agreement sometimes identifies the legal party as the State of Western Australia while specifying that the State acts through a particular department. Clause 17.4, for example, says that the State is acting through the Department of the Premier and Cabinet.

For the initial demonstration, the duty identifies the Government of Western Australia as its assignee:

```turtle
idn-resource:restoration-duty
    a odrl:Duty ;
    odrl:assignee <https://ror.org/00wqdbc63> ;
    odrl:action odrl-action:restore-site ;
    odrl:target idn-resource:water-cultural-sites ;
.
```

A possible later refinement is to identify the operational department using its ROR identifier:

```turtle
idn-resource:restoration-duty
    odrl:assignee <https://ror.org/00wqdbc63> ;
    schema:provider <https://ror.org/00ew5at92> ;
.
```

Here `https://ror.org/00ew5at92` identifies the Western Australian Department of the Premier and Cabinet.

The presentation should not claim that `schema:provider` is definitively correct. Instead, it should ask AGLDWG:

> Does `schema:provider` adequately express that a government party acts through a particular department in carrying out an obligation, or should this be represented using a qualified agent relationship or a more specific ODRL pattern?

For the current prototype, departmental-level extraction is out of scope. The Government of Western Australia is sufficient as the identified ODRL party.

## Live demonstration sequence

The intended live sequence is:

1. Open the Yamatji CreativeWork in Prez and identify the preserved ATNS metadata.
2. Show that the same resource is also an `odrl:Agreement`.
3. Expand the ODRL section and inspect the selected obligations.
4. Follow a party link to a reused canonical agent.
5. Compare the surrender-rights and transfer rules.
6. Follow the spatial-coverage link to the NNTT feature and map.
7. Show the evidence or citation associated with an obligation.
8. Return to the agreement page and identify which statements are preservation data and which are reviewed enrichment.

## Questions for AGLDWG

- Is `schema:provider` a reasonable expression of “the State acting through a department” at rule level?
- Would a qualified PROV or agent relationship preserve the legal and operational distinction more accurately?
- Does representing reciprocal agreement commitments through party collections fit current ODRL practice?
- Are `surrender-rights` and `restore-site` appropriate governed extensions to the ODRL action vocabulary?
- What provenance granularity should be required for clause-level ODRL interpretations?
- How should a user interface distinguish authoritative source statements from later machine-readable interpretation?

## Demonstration readiness checklist

- [ ] Yamatji ODRL enrichment reviewed.
- [ ] All enduring parties reconciled with canonical agent IRIs.
- [ ] Every demonstrated rule has an action, assigner, assignee and appropriate target.
- [ ] RDF syntax and ODRL-IDN SHACL validation pass.
- [ ] Combined Prez profile renders the CreativeWork and ODRL sections on one page.
- [ ] Map and full-detail links work in the intended demonstration environment.
- [ ] Public citations resolve on the presentation network.
- [ ] Screenshots are available as a fallback for the live demonstration.
- [ ] Interpretive and non-authoritative status is visible.

## Increment log

- **2026-11-02:** Created the presentation working document and recorded the Government of Western Australia / Department of the Premier and Cabinet discussion point.
