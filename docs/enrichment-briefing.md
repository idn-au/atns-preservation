# ATNS preservation and enrichment briefing

## Executive summary

The ATNS data is suitable for an initial publication provided that the interface distinguishes preserved historical data from verified, currently accessible resources. Reviewed spatial and agent enrichments can be published now. Further spatial, agent and ODRL enrichment should remain review-led.

## Spatial relationships

The reviewed enrichment contains 469 links from agreements to existing spatial features using `schema:spatialCoverage`. These links were established through exact National Native Title Tribunal identifiers and manually sanity-checked. For example, the Ballardong People Land Use Agreement (`https://data.idnau.org/pid/resource/018a8a09-17ec-52ed-803b-b080115ecc7d`) is linked to feature `https://data.idnau.org/pid/nntt/WI2017-012`.

The audit found at least one candidate feature for 722 of the 2,741 agreement-classified CreativeWorks. Name-derived and ambiguous candidates remain unasserted. More links can therefore be made, but they require review. A spatial association does not assert that the feature is an authoritative legal boundary or an ODRL target.

## Agent extraction

The reviewed enrichment contains 26 subject-agent attributions. The wider audit found 1,814 candidate mentions across 1,318 agreements, including 1,641 high-confidence textual matches. Confidence establishes that an agent name is mentioned; it does not establish an ODRL role.

For example, the Erub Island Multi Purpose Facility ILUA (`https://data.idnau.org/pid/resource/8a3cb6e8-9231-50fd-ae9c-a4fed1777df0`) has a reviewed subject-agent attribution to the Torres Strait Regional Authority, reusing the established identifier `https://linked.data.gov.au/org/capad-TSRA`.

Additional candidates should be reviewed against the IDC agents database and PID register before new organisation identifiers are minted.

## Summary and body text

Source summaries and body text contain embedded HTML and character artefacts such as `<p>`, `<b>`, `<br>` and `&nbsp;`. The Ballardong agreement provides a representative example, including paragraph, emphasis, list and non-breaking-space markup.

The archival XML should remain unchanged. Cleaning should occur reproducibly in the transformation pipeline: downstream of the preserved source, but upstream of generated RDF and presentation. Cleaning only in Prez would leave other RDF consumers with dirty literals, while editing the XML would compromise source fidelity.

## Broken and incomplete links

Some agreement artefact URLs are legacy links that have moved, expired or become difficult to access. Some `dcterms:references` resources have useful metadata but no usable `schema:url`. For example, the Ballardong agreement references “Flow chart for commencement of settlement”; the reference has a name and author but no URL.

Historical URLs should not be silently deleted. Where a verified replacement, persistent identifier or archived copy can be found, it should be added in the transformation or enrichment layer. Unresolved links should carry a visible status such as “unavailable”, “access restricted” or “historical link”, and the interface should not present them as a working primary action.

An otherwise useful record can go live with an unavailable secondary link if the problem is clearly disclosed and the link is not its only evidentiary basis. A known-broken link should not be presented as the primary “View agreement” action.

## ODRL enrichment

ODRL can describe assigners, assignees, permissions, prohibitions, actions, duties, constraints and targets. ATNS text often discusses these matters, but it rarely identifies them with enough structure or directionality for reliable automatic generation.

The directional-language audit found 349 agreements with candidate directional sentences and 478 candidate sentences, but only one high-confidence sentence and four agreements with a possible complete assigner-assignee pair. No agreement combined a high-confidence role pair, action and spatial target.

The principal challenges are unresolved agents, ambiguity between assigner and assignee, collective phrases such as “the parties agree”, unclear permission direction, duties and constraints distributed across several passages, and the risk of treating general spatial coverage as the target of a particular permission. The hand-authored Telstra–Ngaanyatjarra ILUA policy (`https://data.idnau.org/pid/policy/telstra-ngaanyatjarra-ilua`) remains a useful modelling demonstration, not a template that can safely be generated across the collection without review.

ODRL should therefore be treated as a second, expert-led enrichment phase supported by confidence reports and assisted curation forms.

## Recommended decisions

1. Publish the 469 reviewed spatial links and 26 reviewed subject-agent attributions.
2. Schedule further spatial and agent review as a bounded enrichment activity.
3. Clean source HTML and character artefacts during RDF generation while retaining the original XML.
4. Permit records with unavailable secondary links to go live when their status is clearly presented.
5. Repair links through traceable enrichment and presentation rules without overwriting historical evidence.
6. Defer broad ODRL generation to an expert-led second phase.
