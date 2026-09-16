# ADR-0001: Adopt curated RDF as the operational source of truth

## Record

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-09-15 |
| Decision owner | ATNS and IDN governance — to be confirmed |
| Scope | ATNS data recovery, enrichment, authoring and publication |
| Primary TOGAF domain | Phase C: Data Architecture |
| Related ADM phases | Phase A; Phases E–H; continuous Requirements Management |
| Supersedes | None |

## Decision summary

Following an approved migration cutover, reviewed canonical RDF will become the operational source of truth for ATNS data. The preserved XML export will remain immutable source evidence and the basis of a frozen migration baseline, but it will no longer be allowed to overwrite subsequent RDF-native corrections or enrichments.

This ADR is TOGAF-aligned rather than a claim of complete TOGAF conformance. It applies the familiar concerns of Architecture Vision, Baseline and Target Data Architecture, Gap Analysis, Transition Architecture, Migration Planning, Implementation Governance and Architecture Change Management in a proportionate form.

## Context and drivers

The ATNS website and content management system are unavailable, and it is uncertain whether they will resume operation or produce another authoritative export. A preserved XML export dated 5 April 2022 is currently the recoverable source for migration. The repository provides a reproducible transformation into RDF and has begun adding reviewed spatial, agent, vocabulary and prospective ODRL enrichment.

The next phase may use the IDN publishing environment, or a related RDF-native system, for ongoing ATNS maintenance. If the XML remains the perpetual operational authority, rerunning the transformation could remove reviewed corrections and enrichments that never existed in the legacy database. Conversely, abandoning the XML would lose essential evidence about provenance and source-system semantics.

The architecture therefore needs an explicit transition from recovery to RDF-native stewardship while preserving traceability to the legacy source.

## Stakeholders and concerns

| Stakeholder | Principal concerns |
| --- | --- |
| ATNS source owners | Authority, confidentiality, cultural and legal sensitivity, editorial control, future operation |
| Indigenous Studies Unit | Faithful preservation, usability, sustainable stewardship and stakeholder confidence |
| IDN governance | Catalogue-profile conformance, stable identifiers, interoperability, CARE-aware handling and publication status |
| Data modellers and enrichers | Clear evidence boundaries, provenance, review status and safe extension of the graph |
| Platform developers | Deterministic inputs, validation, deployment separation and recoverable change processes |
| Data users | Understandable records, reliable links, transparent interpretation and appropriate access controls |

## Architecture principles

1. **Preserve evidence:** immutable source artifacts and accepted migration outputs remain available for audit.
2. **One declared operational authority:** every production data element has an identifiable canonical home.
3. **Separate authority from deployment:** catalogue and database copies are generated publication artifacts unless explicitly designated otherwise.
4. **Preserve stable identity:** established resource IRIs and legacy identifiers survive the transition.
5. **Make interpretation visible:** source-derived, curated and inferred assertions remain distinguishable.
6. **Fail closed for sensitivity:** uncertain access, deletion or confidentiality signals prevent publication pending review.
7. **Review before reconciliation:** later legacy exports propose changes; they do not silently overwrite canonical RDF.
8. **Validate at the authoring boundary:** canonical changes satisfy applicable RDF, SHACL, profile and governance requirements before publication.

## Requirements

- Preserve the original XML export without in-place repair.
- Retain a reproducible transformation capable of explaining the migration baseline.
- Prevent reruns of legacy conversion from deleting reviewed RDF-native work.
- Support corrections, additions and enrichment directly in RDF after cutover.
- Preserve provenance for source-derived and project-authored assertions.
- Keep confidential, private and deleted records out of public outputs.
- Produce deterministic, reviewable publication packages for IDN catalogue and Prez services.
- Reconcile any future XML export by stable source identifiers and reviewed differences.
- Support rollback, audit and reconstruction of published releases.

## Baseline Data Architecture

The current architecture is transformation-led:

```text
Preserved XML export
    └── normalization and CSV extraction
        └── declarative RDF transformation
            ├── curated enrichment merge
            └── generated RDF
                └── catalogue copy / Fuseki / Prez
```

The XML is immutable and checksum-pinned. The transformation is transparent and repeatable. Curated enrichment is maintained separately and merged during generation. The full public output is still treated primarily as a product of the XML-led pipeline.

### Baseline strengths

- Strong preservation and reproducibility.
- Stable source identifiers and deterministic resource IRIs.
- Explicit publication filtering and validation.
- Initial separation of curated enrichments from generated data.

### Baseline limitations

- Regeneration remains conceptually dominant even as RDF-native enrichment grows.
- There is no formally approved authority cutover.
- Publication graphs could be mistaken for authoring masters.
- A future XML export has no fully specified reconciliation process.
- Statement-level authorship, evidence and review status are not yet uniformly represented.

## Target Data Architecture

The target architecture is RDF-led while remaining preservation-aware:

```text
Immutable legacy evidence ───────────────┐
                                         ↓ provenance
Frozen migration-baseline RDF ──→ Canonical curated ATNS RDF
                                         │
                          validation and release governance
                                         ↓
                              Publication packages
                                         ↓
                           Catalogue / Fuseki / Prez

Future XML export ──→ reconciliation report ──→ reviewed change set ──┘
```

### Architecture Building Blocks

| Building block | Target responsibility |
| --- | --- |
| Preserved XML archive | Immutable evidence of the legacy database export |
| Transformation toolchain | Reproduce and explain the accepted migration baseline |
| Migration-baseline RDF | Frozen record of the initial accepted RDF migration |
| Canonical ATNS RDF | Operational authority for reviewed records and enrichment after cutover |
| Provenance and review metadata | Distinguish source-derived, curated and inferred assertions |
| Validation controls | Enforce RDF syntax, SHACL, access, identity and profile requirements |
| Reconciliation process | Compare later exports and create reviewed change proposals |
| Publication packaging | Generate catalogue-ready files without becoming the authoring master |
| IDN runtime services | Serve released data through databases, APIs and user interfaces |

The exact physical home of canonical RDF remains a governance decision. It may be a dedicated repository, governed RDF-native authoring system, or both with a defined synchronization authority. The current catalogue sync files are not automatically designated canonical merely because they are deployed.

## Gap analysis

| Capability | Baseline | Target | Required change |
| --- | --- | --- | --- |
| Authority | XML-led generation | Declared canonical RDF | Approve and record cutover |
| Preservation | Immutable XML | XML plus frozen RDF baseline | Version and retain accepted baseline |
| Enrichment | Separate overlays merged during generation | First-class governed RDF assertions | Define authoring and acceptance workflow |
| Provenance | Partial file-level separation | Explicit assertion or graph provenance | Adopt a maintained provenance convention |
| Validation | Generation and syntax checks | Authoring-boundary conformance checks | Define SHACL and governance gates |
| Publication | Copied generated files | Deterministic release from canonical RDF | Define packaging and release ownership |
| Future XML | Replacement-oriented update path | Reviewed reconciliation input | Implement additions, changes, removals and conflict reports |
| Change governance | Repository review practices | Named decision and review authorities | Confirm roles, approvals and escalation |

## Decision

The proposed decision is to establish two continuing forms of authority:

1. The preserved XML is authoritative evidence of what the legacy export contained at its recorded date.
2. After an approved cutover, canonical curated RDF is authoritative for the current operational ATNS dataset.

The migration-baseline RDF connects these authorities by recording the accepted transformation of the historical export. Publication databases and catalogue packages are derived views unless a future decision explicitly assigns them authoring authority.

After cutover, the legacy converter must operate in bootstrap, audit or reconciliation mode. It must not replace canonical RDF wholesale.

## Alternatives considered

### Retain XML as the perpetual operational authority

This maximizes transformation reproducibility but cannot safely preserve RDF-native corrections and enrichment that have no legacy XML representation. It also assumes that the abandoned system remains the right conceptual model for future stewardship.

### Treat the deployed Fuseki or catalogue graph as authoritative

This would simplify runtime editing but risks confusing deployment state with governed source data. Database replacement, cache operations and publication workflows could then destroy the only record of editorial changes.

### Keep separate authoritative XML and RDF records indefinitely

This avoids an immediate cutover but creates continuing ambiguity about conflict resolution and increases the likelihood of divergence.

### Adopt curated RDF after a governed cutover

This preserves the historical source while enabling sustainable RDF-native correction, enrichment and publication. It is the preferred target, subject to approval and completion of the transition controls below.

## Transition Architecture and migration plan

The authority change should occur through a bounded transition rather than a single undocumented switch.

### Work package 1: Confirm scope and governance

- Confirm the ATNS and IDN decision owners.
- Confirm which records, vocabularies, enrichments and access classes are in scope.
- Resolve outstanding confidentiality and publication questions.
- Approve identifier, provenance and review principles.

### Work package 2: Freeze the migration baseline

- Generate the accepted public RDF from the checksum-pinned XML.
- Record graph checksums, counts, transformation version and acceptance date.
- Preserve the corresponding code, manifests, vocabularies and reports.
- Identify exclusions and unresolved migration issues.

### Work package 3: Establish canonical RDF stewardship

- Choose the canonical repository or authoring system.
- Separate source-derived, curated and inferred assertions using the approved convention.
- Define correction, addition, deletion, access-change and enrichment workflows.
- Add validation and review gates, including prospective ODRL application-profile checks.

### Work package 4: Change publication flow

- Generate catalogue packages from canonical RDF.
- Treat Fuseki and Prez as release destinations.
- Record release versions and deployment provenance.
- Prove that a release can be reconstructed from governed source artifacts.

### Work package 5: Introduce reconciliation mode

- Match later legacy rows using preserved source identifiers.
- Report additions, changes, deletions, visibility changes and conflicts.
- Require review before applying any proposal to canonical RDF.
- Preserve the new export as another dated source artifact.

## Implementation governance and conformance

Cutover must not occur until the decision owner accepts the migration baseline and confirms the canonical RDF location and operating roles.

A conformant implementation must:

- retain the immutable XML and frozen migration baseline;
- prevent legacy regeneration from overwriting curated RDF;
- preserve stable resource IRIs and source identifiers;
- identify the provenance and review status of enrichment;
- apply fail-closed publication filtering;
- pass agreed RDF, SHACL and catalogue-profile validation;
- generate deployment artifacts from the canonical source;
- retain reviewable release and reconciliation records.

Temporary manual processes are acceptable during transition if authority, review responsibility and resulting changes remain explicit and auditable.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| RDF enrichment is mistaken for recovered source fact | Preserve provenance and visible interpretation status |
| Cutover occurs without source-owner approval | Keep this ADR Proposed until named approval is recorded |
| Legacy regeneration removes curated work | Disable wholesale replacement after cutover and use reconciliation reports |
| Deployment database becomes an accidental master | Generate it from canonical RDF and retain versioned source artifacts |
| Sensitive records are published | Maintain fail-closed access checks and source-owner review |
| Canonical RDF becomes difficult to edit | Define an RDF-native authoring workflow suitable for domain specialists |
| New XML conflicts with RDF corrections | Treat it as dated evidence and resolve differences through review |
| ODRL interpretations overstate legal meaning | Apply an explicit evidence gate, provenance and specialist review |

## Consequences

### Positive

- RDF-native corrections and enrichment become durable.
- Historical evidence remains preserved and reproducible.
- Publication systems can be replaced without changing data authority.
- Future imports become controlled, auditable change proposals.
- ATNS can evolve beyond the constraints of its former relational and CMS model.

### Negative or costly

- Canonical RDF requires ongoing governance, validation and editorial tooling.
- Provenance and review status add modelling and operational complexity.
- The project must maintain a reconciliation path for any revived legacy system.
- Some enrichments, particularly ODRL interpretations, require specialist human review.

## Review and change triggers

Review this decision when:

- the ATNS website or CMS resumes authoritative operation;
- a new XML or database export is supplied;
- a production RDF-native authoring environment is selected;
- responsibility for ATNS stewardship changes;
- IDN catalogue architecture or profile requirements materially change;
- legal, cultural, access or confidentiality requirements change;
- ODRL enrichment moves from prototype to production;
- the canonical repository or deployment topology changes.

Material changes should produce a superseding ADR rather than silently rewriting the history of this decision.

## TOGAF traceability

| ADR content | TOGAF alignment |
| --- | --- |
| Context, drivers, stakeholders and scope | Phase A: Architecture Vision |
| Principles and requirements | Preliminary Phase and continuous Requirements Management |
| Baseline and Target Data Architecture | Phase C: Information Systems Architectures — Data Architecture |
| Gap analysis and building blocks | Phase C |
| Transition Architecture and work packages | Phase E: Opportunities and Solutions |
| Cutover and sequencing | Phase F: Migration Planning |
| Conformance and acceptance | Phase G: Implementation Governance |
| Review triggers and supersession | Phase H: Architecture Change Management |
| Version-controlled ADR and related artifacts | Architecture Repository and governance record |

The current TOGAF reference is the [TOGAF Standard, 10th Edition](https://www.opengroup.org/togaf). The Open Group also provides [example deliverable templates](https://help.opengroup.org/hc/en-us/articles/21726647171730-Are-There-Any-Template-Deliverables-for-the-TOGAF-Standard). This ADR deliberately applies those concepts lightly and proportionately.

## Acceptance

This proposal becomes Accepted only when the following are recorded:

- named decision owner;
- approval date;
- canonical RDF location and responsible steward;
- accepted migration-baseline identifier and checksum;
- effective cutover date;
- approved provenance, validation and publication controls.

Until then, the current XML-led pipeline and reviewed enrichment overlays remain the operative transition architecture.

## Related records

- [Conversion process](../conversion.md)
- [ATNS preservation and enrichment briefing](../enrichment-briefing.md)
- [Provisional ODRL modelling for ATNS agreements](../odrl-agreement-modelling.md)
- Repository model and publication profiles under `model.ttl` and `prezconfig/`
