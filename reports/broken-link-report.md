# ATNS `schema:url` link audit

Checked: `2026-09-09T05:50:59+00:00`

`last_url_reached` records where redirect handling ended; it is diagnostic evidence, not a recommended replacement. `possible_updated_url` is populated only when a same-domain changed path returned usable content. `candidate_url` records a predictable mapping that has not been validated inside the destination browser application; these rows have `candidate_status` `candidate_unverified`. `assessment` describes the original URL check and is independent of candidate status. Access restrictions, timeouts and server errors are not automatically called broken. HTTP 204, explicit zero-length responses, 404/410, invalid URLs and detected soft-404 pages are confirmed broken.

## Entity URLs

Full table: `entity-url-audit.csv` (4,031 URL assertions; 1,762 confirmed or likely broken).

| Assessment | Count |
| --- | --- |
| review_required | 1,400 |
| confirmed_broken | 1,187 |
| working | 869 |
| likely_broken | 575 |

| Classification | Count |
| --- | --- |
| access_restricted | 1,184 |
| ok | 869 |
| not_found | 764 |
| dns_error | 556 |
| no_content | 416 |
| timeout | 107 |
| redirect_to_home | 51 |
| connection_error | 36 |
| server_error | 16 |
| tls_error | 10 |
| client_error | 9 |
| soft_404 | 7 |
| request_error | 5 |
| unexpected_status | 1 |

### Most common broken domains

| Domain | Broken URLs |
| --- | --- |
| nntt.gov.au | 878 |
| apps.indigenous.gov.au | 114 |
| ainc-inac.gc.ca | 33 |
| indigenous.gov.au | 24 |
| orac.gov.au | 17 |
| federalfinancialrelations.gov.au | 16 |
| health.gov.au | 7 |
| iluasa.com | 6 |
| info.gov.za | 5 |
| legislation.sa.gov.au | 5 |
| nationalparks.nsw.gov.au | 5 |
| dme.gov.za | 4 |
| ozminerals.com | 4 |
| laws.justice.gc.ca | 4 |
| aiatsis.gov.au | 3 |

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

### Unverified candidate URLs

29 deterministic candidate mappings were generated. They require browser-level validation before the source RDF is changed.

| Resource | Name | Original URL | Candidate URL | Status |
| --- | --- | --- | --- | --- |
| https://data.idnau.org/pid/resource/87038c37-8826-5493-a4f3-cc6eaca56160 | Largut v Northern Territory of Australia [2013] FCA 1069 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/003 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F003 | candidate_unverified |
| https://data.idnau.org/pid/resource/f086fafb-fdca-5d61-bab8-ffe49a0ffe7c | Largut v Northern Territory of Australia [2013] FCA 1070 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/004 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F004 | candidate_unverified |
| https://data.idnau.org/pid/resource/3f52da08-6b8a-5577-9ef6-2cb254243194 | Johns v Northern Territory of Australia [2013] FCA 1074 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/007 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F007 | candidate_unverified |
| https://data.idnau.org/pid/resource/f9d19f9d-b5b3-5e90-9ec3-4e27fac34905 | Johns v Northern Territory of Australia [2013] FCA 1075 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/008 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F008 | candidate_unverified |
| https://data.idnau.org/pid/resource/d38df698-8ec9-587b-99f3-f2936291fe66 | Johns v Northern Territory of Australia [2013] FCA 1076 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/009 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F009 | candidate_unverified |
| https://data.idnau.org/pid/resource/67f4f157-9fac-5a64-bbc1-5f2a7dc846e1 | Johns v Northern Territory of Australia [2013] FCA 1077 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/010 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F010 | candidate_unverified |
| https://data.idnau.org/pid/resource/2b3fa225-fee3-544b-9825-b8c0f5a818b5 | Johns v Northern Territory of Australia [2013] FCA 1079 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/012 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F012 | candidate_unverified |
| https://data.idnau.org/pid/resource/e6c455b9-f1ce-5cee-8778-b2e1093ea9c0 | Brown v Northern Territory of Australia [2013] FCA 1080 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/013 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F013 | candidate_unverified |
| https://data.idnau.org/pid/resource/72f81fd9-34e6-5e52-93fe-738035fb63da | Wavehill v Northern Territory of Australia [2013] FCA 1081 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/014 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F014 | candidate_unverified |
| https://data.idnau.org/pid/resource/1f598b58-2a08-5d01-930e-1ed46a68113d | Brown v Northern Territory of Australia [2013] FCA 1082 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/015 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F015 | candidate_unverified |
| https://data.idnau.org/pid/resource/41f860dd-94b4-5d67-b3a0-a1abc787f723 | Brown v Northern Territory of Australia [2013] FCA 1083 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/016 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F016 | candidate_unverified |
| https://data.idnau.org/pid/resource/81ac00d1-e5c5-5a12-8dac-9ab4df79d934 | Brown v Northern Territory of Australia [2013] FCA 1084 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/017 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F017 | candidate_unverified |
| https://data.idnau.org/pid/resource/62d63618-cc5d-5036-bc00-0e17c7dbe7b8 | Wavehill v Northern Territory of Australia [2013] FCA 1086 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/018 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F018 | candidate_unverified |
| https://data.idnau.org/pid/resource/ece77b59-a7d4-5afc-af7b-dcff8f555a18 | Fulton v Northern Territory of Australia [2013] FCA 1088 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/019 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F019 | candidate_unverified |
| https://data.idnau.org/pid/resource/03043c17-d2fe-5788-a719-38e34e7a8c39 | Tonson v Northern Territory of Australia [2013] FCA 1087 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/020 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F020 | candidate_unverified |
| https://data.idnau.org/pid/resource/128f374b-6d8b-5a4e-9c1c-07075037c9aa | Jurluba v Northern Territory of Australia [2015] FCA 1248 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2015/007 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2015%2F007 | candidate_unverified |
| https://data.idnau.org/pid/resource/ee7f496d-5801-5f69-ab20-9d7b76ed419e | Largut v Northern Territory of Australia [2015] FCA 1269 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2015/012 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2015%2F012 | candidate_unverified |
| https://data.idnau.org/pid/resource/15261148-dc67-5653-90de-225fe800c06b | Brown v Northern Territory of Australia [2015] FCA | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2015/013 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2015%2F013 | candidate_unverified |
| https://data.idnau.org/pid/resource/74fbafe5-a93c-5b38-8af2-d6c1714a8571 | Brooks on behalf of the Mamu People v State of Queensland (No 4) [2013] FCA 1453 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2013/005 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2013%2F005 | candidate_unverified |
| https://data.idnau.org/pid/resource/e4a12b80-bddc-5957-8560-a1e07e741006 | Barry Fisher & Ors on behalf of the Ewamian People #2 v State of Queensland & Ors | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2013/006 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2013%2F006 | candidate_unverified |
| https://data.idnau.org/pid/resource/7b9f8708-890b-54c4-9af2-3bff4faefe74 | Barry Fisher & Ors on behalf of the Ewamian People #3 v State of Queensland & Ors | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2013/007 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2013%2F007 | candidate_unverified |
| https://data.idnau.org/pid/resource/ca4faa99-36eb-5a64-82a4-1bfa9b7a82be | Foster on behalf of the Gunggari People #3 v State of Queensland [2014] FCA 1318 - proofing required | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2014/018 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2014%2F018 | candidate_unverified |
| https://data.idnau.org/pid/resource/f06de437-70b6-5419-8b5c-88605a0eeae6 | Far West Coast Native Title Claim and The State of South Australia [2013] FCA 1285 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=SCD2013/002 | https://www.nntt.gov.au/search-the-registers/native-title-register#/SCD2013%2F002 | candidate_unverified |
| https://data.idnau.org/pid/resource/0aed18f6-93cc-58aa-8e8f-7e27abed7056 | Yandruwandha/Yawarrawarrka Native Title Claim and The State of South Australia  ors | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=SCD2015/003 | https://www.nntt.gov.au/search-the-registers/native-title-register#/SCD2015%2F003 | candidate_unverified |
| https://data.idnau.org/pid/resource/f7c6df0d-1803-59c3-b11b-5a83c57accd0 | Largut v Northern Territory of Australia [2013] FCA 1072 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/005 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F005 | candidate_unverified |
| https://data.idnau.org/pid/resource/6d84bef4-3d07-55ab-9399-8e0f32cbccb6 | Johns v Northern Territory of Australia [2013] FCA 1073 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=DCD2013/006 | https://www.nntt.gov.au/search-the-registers/native-title-register#/DCD2013%2F006 | candidate_unverified |
| https://data.idnau.org/pid/resource/d6780c1b-670d-59a2-a1b7-273708da2d9a | Greenwool & Ors on behalf of the Kowanyama People v State of Queensland [2012] FCA1377 (Kooyama People Part B) | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2012/016 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2012%2F016 | candidate_unverified |
| https://data.idnau.org/pid/resource/7d98b4a4-a72f-5d6b-b76b-22cc38e68ec7 | Greenwool & Ors on behalf of the Kowanyama People v State of Queensland [2012] FCA1377 (Kowanyama People Part C) | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=QCD2012/017 | https://www.nntt.gov.au/search-the-registers/native-title-register#/QCD2012%2F017 | candidate_unverified |
| https://data.idnau.org/pid/resource/d4ac6c6e-d430-5a3b-9bea-c7f304e2673a | Gepp-Kennedy on behalf of the Dieri People v State of South Australia [2017] FCA 1156 | http://www.nntt.gov.au/searchRegApps/NativeTitleRegisters/Pages/NNTR_details.aspx?NNTT_Fileno=SCD2017/001 | https://www.nntt.gov.au/search-the-registers/native-title-register#/SCD2017%2F001 | candidate_unverified |

## Reference URLs

Full table: `reference-url-audit.csv` (1,597 URL assertions; 711 confirmed or likely broken).

| Assessment | Count |
| --- | --- |
| review_required | 470 |
| confirmed_broken | 421 |
| working | 416 |
| likely_broken | 290 |

| Classification | Count |
| --- | --- |
| ok | 416 |
| not_found | 405 |
| access_restricted | 331 |
| dns_error | 279 |
| timeout | 77 |
| redirect_to_home | 35 |
| server_error | 13 |
| soft_404 | 10 |
| connection_error | 8 |
| no_content | 6 |
| tls_error | 6 |
| client_error | 5 |
| request_error | 5 |
| unexpected_status | 1 |

### Most common broken domains

| Domain | Broken URLs |
| --- | --- |
| nntt.gov.au | 106 |
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

### Unverified candidate URLs

0 deterministic candidate mappings were generated. They require browser-level validation before the source RDF is changed.

No deterministic candidate mappings were generated.
