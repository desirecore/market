# AMap JSAPI 1.1.1 complete ZIP admission — 2026-11-24

Reviewer: mashagua. Availability: installable. This is a manual package/source review, not a live-map acceptance test or a security certification.

## Artifact and completeness

URL: https://clawhub.ai/api/v1/download?slug=amap-jsapi-skill&version=1.1.1&ownerHandle=lbs-amap

ZIP SHA-256: `9468743ee18dbe1704e8a98f47f6628d6a4e6acec30a05f0b8f59a07603d011f`.
The version URL is paired with this digest rather than assumed permanently immutable. The live download matches it. The unchanged archive contains 36 regular files, 390,853 unpacked bytes; the largest is 45,586 bytes. All are Markdown or JSON. No symlinks, path traversal, binaries or standalone executable scripts were found. `SKILL.md` is at ZIP root, so `source.path` is omitted and the schema field is `source.repoUrl` (not `url`).

All 33 unique referenced Markdown paths (21 Markdown links plus 12 inline references) exist, including `references/security.md`. Every file size and SHA-256 matches the publisher's owner-qualified 1.1.1 manifest. The 7,979-byte SKILL file keeps the previous single-file digest `cf2f06cc5abf5e41a626f823c50575ab52c81aecbceca5abd4e69d56ca5c5d75`, but the newly reviewed installation artifact is the full ZIP digest above, not the old single-file response.

## License decision and preserved discrepancy

- Actual `SKILL.md:5`: `license: MIT`.
- Actual `skill-card.md:13`: `MIT-0`.
- ClawHub owner-qualified 1.1.1 version metadata: `license: MIT-0`.
- There is no standalone LICENSE, COPYING or NOTICE file in the 36-file archive. Current market main declared MIT without an evidencePath.

This admission follows the actual SKILL MIT declaration, conservatively retaining attribution/notice obligations rather than advertising the MIT-0 waiver. `license.evidencePath` and `compliance.licenseEvidencePath` are the real upstream `SKILL.md`; `compliance.noticePath` points to the actual `skill-card.md` so its differing declaration is not hidden. This is an explicit reviewed declaration-based decision, NOT a claim that the publisher clarified the inconsistency, issued dual licensing, or supplied standalone MIT text. No upstream file is modified and no license file or copyright grant is invented. Keep the whole package and its existing author/source/license signals intact; publisher clarification would improve certainty.

中文：按 SKILL 实际声明的 MIT 审核并保留署名义务；完整披露 skill-card/注册信息的 MIT-0 差异及无独立 LICENSE 的事实，不声称上游已经澄清或授予双许可。市场收录许可不替代高德 SDK、地图数据和外部服务条款。

## Static security findings and limits

All 36 text files were included in the content/URL/instruction scan and per-file manifest verification. No silent telemetry endpoint/instruction (including the GitHub 1.1.0 log/init requirement), credential harvesting, malicious executable payload, or instruction to override host safety was identified in this ZIP. No upstream instructions or example requests were executed during review.

The docs do contain normal SDK/API/proxy and geolocation examples, external map/demo resources, legacy HTTP/JSONP examples, and an upstream public demonstration key literal in an API example. That literal was NOT validated, used, or copied into this review; do not treat upstream examples as a usable user credential or copy them into production. Supply the user's own Key via private host configuration, use HTTPS and a secure production proxy, review generated HTML/data handling, and obtain consent for location data. Other example services/resources have their own availability and terms. Static review does not prove all generated applications safe, grant API access, or establish zero unknown vulnerabilities.

## Runtime prerequisites

Require the user's own AMap Web JSAPI Key plus securityJsCode or a correctly configured serviceHost backend proxy; respect authorized domains, service terms, quotas and possible billing. The docs are complete, but the skill is not a bundled SDK entitlement, account, key or paid service. A real authenticated map was not initialized in this audit. Missing user authorization is distinct from the now-fixed missing-document packaging defect.

## Exact file manifest

| Path | Bytes | SHA-256 |
|---|---:|---|
| SKILL.md | 7979 | cf2f06cc5abf5e41a626f823c50575ab52c81aecbceca5abd4e69d56ca5c5d75 |
| _meta.json | 136 | e7fb03efc0c0675b8311c834b0716964f050929614ee26ec379bc8be67e8f0dc |
| references/api/common.md | 35194 | eab7a2608f190b40b4f189309f91cb0ccdc211e61971cbd2e46d2b66b9053e75 |
| references/api/context-menu.md | 1116 | 62593b9f38bf1affd6da804739ec485e6ea0c494dc9f30463f7fe053cd92035e |
| references/api/controls.md | 8868 | d61be8eebe092f4ff6b99d1210ee418d50d9445ef8e10ac3cdadb91c82053a14 |
| references/api/events.md | 2359 | 05d077f4367ccfe1e8fb38503231a9434ab30b6ca084424441605da9871ecf43 |
| references/api/foundation.md | 5655 | c105059b808ec4dc796781982b03e68e3d17dcf8e0bb106624c0802b4a85ad48 |
| references/api/geocoder.md | 4189 | 2e6c77590acfd357af40d170ac4f46f7338c43524195b40525975a49a1e3e729 |
| references/api/geolocation.md | 5248 | 46e3bd52d43049f28ce43684120de8b8ff56515d31670d4b2ebff5ea5ef95a1c |
| references/api/info-window.md | 2754 | 5d717c8ba07dd657a12bc36b6519213b0403428af81b6372d978c75600b5498a |
| references/api/layers-custom.md | 20361 | b13cd4e4e31a0cd5e615c59ab8cf75db738192593218993eb2753151da498ad5 |
| references/api/layers-official.md | 25287 | 66657dba0467f9869c2f11235777fb3c86fbe16236952ae5685ae8c73ee3d68d |
| references/api/layers-standard.md | 13607 | 085cb25c707dfd3b9eefd62681f12c553718fc263ba6a65b0f3fc6304eab3d3e |
| references/api/map.md | 20866 | 8972c0614ced623539ef3edcd4854e36be4e785c050baae292e2d29ae996183a |
| references/api/marker.md | 45586 | 09fe0f126bea09e0dc9c8be329d3dac68a2576a53784a808cb9c5a0f8606f00c |
| references/api/overlay-group.md | 4388 | 7c627086fad1315a5b358997f76dcbb0c7dd7c2e955f195e84e4811c338b2fb3 |
| references/api/routing.md | 39883 | 6591c534638236b53714b845e154a3c8b4bcda6946208d6d1693402008760751 |
| references/api/search.md | 14044 | be58063affb1e6a3484bb0abed454d4cd108d2fc70a8c498dcd8d8e26a182e63 |
| references/api/services-other.md | 12583 | 6f016749505379b6a759ce26ff54bfeb2d9fe01c6ae873db13a872ac4cd24745 |
| references/api/services.md | 1907 | fdfb7f17937030ba8534bc2da355299c1fe22cf4e5d1961ec0df2c9a3d628ba4 |
| references/api/tools.md | 9854 | 32ff52bf9f5de92286e1c145ac1b5403bcedfe3c0c897114d055aabf3b2427b8 |
| references/api/vector-graphics.md | 33442 | b143e76a77d68c71051af36ddd6f88b52b20e2d6fa9f893bb3dbb7a1dfcadb1a |
| references/context-menu.md | 1534 | f907bfb8424516cb648fc2092ac5b198505685a9cf0bcd48be7fc348ced2b395 |
| references/custom-layers.md | 6118 | 6e815d5723197566a8a52cca945f2b82cdb01c5fc42e71a8d143d0c71edcef89 |
| references/events.md | 4443 | b8c35746ee6e914f440566ea1e1750de08d070f18184d960923833ba275d5209 |
| references/geocoder.md | 4495 | d2b8b23cf892fbe46ec1352d797b8515fb904fcbb23cff9f59d4e172e135b6e6 |
| references/info-window.md | 7568 | cb5999c377086929ce2c5ea30edb7a1482ae0a161ae23f01f825e47b34d54aed |
| references/layers.md | 1874 | c6ea853a6cbb77cc617e7e246db5213b80c07ac07428d43a2bd31b69cf738a8b |
| references/map-init.md | 6623 | 0f40e339dfa7d1af64af4fb04d8be4cf9ad318bd6ae67ecaa94638fc705818e3 |
| references/marker.md | 8198 | d2439c94534498a17638a3b2b86a2465ac45c8d538c65688b97708310e8f952a |
| references/routing.md | 15336 | 3d865324bbc08eab0025bebac2d6a77079d781efc4517415afba156bab9a6a0a |
| references/search.md | 2640 | c4d0286175077612d0c66f569af5a1a2bc804219105284002f0d53f200065c0f |
| references/security.md | 5665 | b9525f3ae4aab76cf1c0cba6656c9b04abbd6ca4c750872c8c2d34434663388e |
| references/vector-graphics.md | 5073 | a60ae8b97099861d14765c51d8f974270dda8efffeefb2e6f0501319a435504b |
| references/view-control.md | 2835 | 28635775c63963903f2231329e113a376a20d253163c8cb2e1888d9a7c99aad5 |
| skill-card.md | 3145 | 879e21daf4c840684c8d13c438f17655907c97f9a357ab9c68a5d78679eb4a25 |
