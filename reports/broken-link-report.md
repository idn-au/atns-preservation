# ATNS `schema:url` link audit

Checked: `2026-09-09T05:23:01+00:00`

`assessment` distinguishes working links, confirmed or likely breakage, and results requiring review. Access restrictions, timeouts and server errors are not automatically called broken. HTTP 204, explicit zero-length responses, 404/410, invalid URLs and detected soft-404 pages are confirmed broken.

## Entity URLs

Full table: `entity-url-audit.csv` (4,031 URL assertions; 1,821 confirmed or likely broken).

| Assessment | Count |
| --- | --- |
| review_required | 1,356 |
| confirmed_broken | 1,262 |
| working | 854 |
| likely_broken | 559 |

| Classification | Count |
| --- | --- |
| access_restricted | 1,123 |
| ok | 854 |
| not_found | 810 |
| dns_error | 540 |
| no_content | 445 |
| timeout | 118 |
| redirect_to_home | 53 |
| connection_error | 39 |
| server_error | 17 |
| tls_error | 10 |
| client_error | 9 |
| soft_404 | 7 |
| request_error | 5 |
| unexpected_status | 1 |

### Most common broken domains

| Domain | Broken URLs |
| --- | --- |
| nntt.gov.au | 951 |
| apps.indigenous.gov.au | 114 |
| ainc-inac.gc.ca | 33 |
| indigenous.gov.au | 24 |
| orac.gov.au | 17 |
| federalfinancialrelations.gov.au | 16 |
| health.gov.au | 7 |
| iluasa.com | 6 |
| nationalparks.nsw.gov.au | 5 |
| dme.gov.za | 4 |
| ozminerals.com | 4 |
| laws.justice.gc.ca | 4 |
| legislation.sa.gov.au | 4 |
| aiatsis.gov.au | 3 |
| au.mycompanydetails.com | 3 |

### Observed same-domain path migrations

| Domain | Original path | Final path | Examples |
| --- | --- | --- | --- |
| gbrmpa.gov.au | /our-partners/traditional-owners/traditional-use-of-marine-resources-agreements | /learn/traditional-owners/traditional-use-marine-resources-agreements | 10 |
| legislation.govt.nz | / | / | 3 |
| gunditjmirring.com | / | / | 2 |
| aaco.com.au | / | / | 1 |
| act.gov.au | / | / | 1 |
| aflaca.org.au | /members/queensland-lapidary-and-allied-craft-clubs-association-qlacca | /members/queensland-lapidary-and-allied-craft-clubs-association-qlacca/ | 1 |
| agriinfo.co.za | /index.htm | / | 1 |
| alcoa.com | /australia/en/home.asp | /australia/en | 1 |
| alga.com.au | / | / | 1 |
| angusknight.com.au | /default.htm | /default.htm/ | 1 |
| ansto.gov.au | /index.html | /search | 1 |
| batchelor.edu.au | / | / | 1 |
| bom.gov.au | / | / | 1 |
| bridgeclinic.com.au | / | / | 1 |
| bushheritage.org.au | /about | /who-we-are | 1 |

## Reference URLs

Full table: `reference-url-audit.csv` (1,597 URL assertions; 723 confirmed or likely broken).

| Assessment | Count |
| --- | --- |
| review_required | 457 |
| confirmed_broken | 434 |
| working | 417 |
| likely_broken | 289 |

| Classification | Count |
| --- | --- |
| not_found | 418 |
| ok | 417 |
| access_restricted | 316 |
| dns_error | 278 |
| timeout | 79 |
| redirect_to_home | 37 |
| server_error | 13 |
| soft_404 | 10 |
| connection_error | 6 |
| no_content | 6 |
| tls_error | 6 |
| client_error | 5 |
| request_error | 5 |
| unexpected_status | 1 |

### Most common broken domains

| Domain | Broken URLs |
| --- | --- |
| nntt.gov.au | 116 |
| ainc-inac.gc.ca | 68 |
| indigenous.gov.au | 18 |
| abc.net.au | 17 |
| nlc.org.au | 17 |
| laws.justice.gc.ca | 12 |
| ntru.aiatsis.gov.au | 11 |
| pir.sa.gov.au | 10 |
| gov.nt.ca | 10 |
| ea.gov.au | 9 |
| diavik.ca | 9 |
| nit.com.au | 9 |
| pm.gov.au | 7 |
| aiatsis.gov.au | 6 |
| atsia.gov.au | 6 |

### Observed same-domain path migrations

| Domain | Original path | Final path | Examples |
| --- | --- | --- | --- |
| legislation.govt.nz | / | / | 10 |
| nt.gov.au | /dcm/publications/commonground/200507_CommonGround_Issue5.pdf | / | 3 |
| abc.net.au | /message/news/stories/s1629412.htm | /indigenous | 2 |
| clc.org.au | /media-releases/article/native-title-over-mt-riddock-aileron-and-nolan-bore-to-be-declared | /native-title-over-mt-riddock-aileron-and-nolan-bore-to-be-declared/ | 2 |
| dbca.wa.gov.au | /about | /about-us | 2 |
| riotinto.com | /en/operations/australia/weipa | /en/operations/anz/weipa | 2 |
| tsra.gov.au | /news-and-resources/annual-reports/annual-report-2017-2018/section-4-corporate-governance-and-accountability/enabling-functions | /document/tsra-2017-2018-annual-report/ | 2 |
| abc.net.au | /7.30/content/2005/s1355870.htm | /news/programs/730 | 1 |
| abc.net.au | /am/content/2005/s1356138.htm | /am/archive/default.htm | 1 |
| abc.net.au | /am/content/2005/s1475971.htm | /am/archive/default.htm | 1 |
| abc.net.au | /am/content/2005/s1533165.htm | /am/archive/default.htm | 1 |
| abc.net.au | /message/news/stories/ms_news_1373898.htm | /indigenous | 1 |
| abc.net.au | /message/news/stories/ms_news_1397426.htm | /indigenous | 1 |
| abc.net.au | /message/news/stories/ms_news_1397985.htm | /indigenous | 1 |
| abc.net.au | /message/news/stories/ms_news_1451071.htm | /indigenous | 1 |
