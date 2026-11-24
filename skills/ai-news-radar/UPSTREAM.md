# Upstream provenance and local edition

Source: https://github.com/LearnPrompt/ai-news-radar/tree/689395109cc962a27c369bdd6fa50d1e090eb319
Immutable source commit: `689395109cc962a27c369bdd6fa50d1e090eb319`. Local packaging version: `2026.11.24` (not an upstream release).

Copyright (c) 2026 LearnPrompt. The 1,068-byte upstream MIT [LICENSE](LICENSE) is preserved verbatim. This is an independently maintained market packaging, not upstream endorsement.

## Changes and exclusions

- Generator, relevance module, overlap helper, requirements, example feed, glossary, original references and selected reader assets (except the explicitly noted classic-page links and CSS EOF whitespace) are byte-identical to the pinned source. No files come from current upstream HEAD.
- Local bilingual SKILL/README instructions replace repository-development guidance with installed-package usage. The new safe launcher requires external absolute output and disables bytecode writes.
- Imported project/skill guides and development docs have an explanatory reference notice and immutable upstream Markdown links. They are reference material, not installed development workflows.
- All original SKILL direct runtime/doc/UI references are represented below. Private feeds, generated data, giant historical archives/caches, screenshots, upstream tests/workflows and external skill-creator tools are not installed; the local SKILL makes no claim they are. Empty history is supported by the unchanged generator.
- Output JSON paths are generated inside the explicitly selected private output directory, not pre-existing package resources. Optional email, social and paid adapters remain separately configured and authorized.

- The classic reader service-status links are normalized for its existing base href. Optional persona scoring and its three prompt files are included; it requires separately authorized provider configuration and is not part of the offline news-generation test. Legacy reader pages are not shipped.
- The optional reader loads GSAP 3.13.0 from jsDelivr with upstream integrity metadata; this third-party CDN dependency is not vendored and requires network access.

## Imported source manifest

| Upstream path | Package path | Source bytes | Source SHA-256 | Changes |
|---|---|---:|---|---|
| LICENSE | LICENSE | 1068 | 1eef1394cbdc77865323cb153d3ffc241af74184246ee253ce5bcfd65b61cc0b | none |
| assets/app.js | assets/app.js | 92066 | 4ee5e351689fb88020c726affdd1bf767bb6b42aa2aa90e6f770f25f1b8eafaa | none |
| assets/icons/apple-touch-icon.png | assets/icons/apple-touch-icon.png | 27296 | 2a3dbb278f16bf538dbbe29fada7b28dddecc3d51f7506d793964e808850d1b7 | none |
| assets/icons/favicon-32.png | assets/icons/favicon-32.png | 2578 | 70a1aa71a978aafbe06ecb8a78cddf0f1f2c16644b59c5f20ec4a90b3464f6a6 | none |
| assets/icons/icon-192.png | assets/icons/icon-192.png | 28836 | 1a3075115f032bee0005ad02a50dcba0c60006e6fd130caa74816081c001df0c | none |
| assets/icons/icon-512.png | assets/icons/icon-512.png | 77149 | 6b2899f623812c35edc3f3a31a5c942229d6a2369639cd971592f827e24d757f | none |
| assets/logo.svg | assets/logo.svg | 1258 | 89c98d5e8288984f204da770eebb7f0dfc37f3e29daeb58787fd69adfbe9fafd | none |
| assets/motion.js | assets/motion.js | 1281 | b27fae1fd3990aced1c803ce619686eadd888b9059933680b4ffd8e7c5118dcd | none |
| assets/og.png | assets/og.png | 48055 | 21cb49329c88a13b1ff149603dbacd872f206ae9e018e2fc4f86fdf49034f5b1 | none |
| assets/service-status.css | assets/service-status.css | 2130 | cbb4e02f81e4f91d7b97d6c9262bccae8f53e831122d976e90cfd85dc525905d | none |
| assets/service-status.js | assets/service-status.js | 5369 | 0aa01cd32c346d778badd1ce51636da77188701f989cc2f99921a42810b7a78f | none |
| assets/styles.css | assets/styles.css | 38747 | 889a68cb3c4c1a3bca9181493612c09bc7cea31e8ebb3bfbd4477eca28e49140 | trim extra blank line at EOF only |
| assets/view-mode.js | assets/view-mode.js | 4373 | 77c2f6834fc7e64f31e0c28a302b9c57a7868aa5f6856300d36f7e8905dac8a2 | none |
| assets/view-switch.css | assets/view-switch.css | 2528 | 05b70dd29586a784674f59472f5c9aa5532ac7fe544510ee82fc711a47a0feab | none |
| feeds/follow.example.opml | feeds/follow.example.opml | 2400 | c8f61d59f098f4e0da0de35356b6eae90eb3c4a794b057afd40048bc6ba42ede | none |
| index.html | index.html | 10230 | fac7af098270897f347f46e777a1e8227863fcb2fb642d0f6eead57bce6d2c73 | none |
| requirements.txt | requirements.txt | 88 | f206ef31decbffd0ade3fbfebb513158ad27521ee541969e517535865c629ba8 | none |
| scripts/ai_relevance.py | scripts/ai_relevance.py | 13733 | 97d1ea44d04663d21af8ac60ed3b26bd9ee4b55418e6979a31baeea6df0bb4bb | none |
| scripts/evaluate_source_overlap.py | scripts/evaluate_source_overlap.py | 15274 | 9558f13ffc310d4d8523f22d77280f5a470f2e5df3c1c9d477461ac91f9d8375 | none |
| scripts/update_news.py | scripts/update_news.py | 273569 | 7cf57bb45f8ea48e731d7dd8b27392c4ec2e5844acfd7c137edf0920e03a1165 | none |
| skills/ai-news-radar/agents/openai.yaml | agents/openai.yaml | 294 | 1fbeab04768ce9d0ea35d8c1ae177f626235c2ec615cf7584688d93ca2606324 | none |
| skills/ai-news-radar/references/source-intake.md | references/source-intake.md | 6737 | 1e18da6313d647924c68b49bdc86873b829fa343c55f0dd727f240f6e820692c | none |
| skills/ai-news-radar/references/v2-method.md | references/v2-method.md | 4218 | f415f236fce6981e6f05e063f463e8a412e4cd9b964550184f1b3db7b2c4e8b7 | none |
| translation-glossary.txt | translation-glossary.txt | 1181 | 8eb25938e8436c0f989dbb9f6bc9721cba83889bb48d26fde867d385e65b8b4a | none |
| README.md | references/upstream-project-readme.md | 27963 | 660d1359c8ce8cf50e6b051a67de1158353238a4506d06579d9b0ffa5333968c | reference notice and immutable upstream Markdown links |
| README.en.md | references/upstream-project-readme.en.md | 25716 | 4ced637ac7f9040824774d25de5a0bce4bafaa3a4afcef47aa824fe1a00318ec | reference notice and immutable upstream Markdown links |
| skills/ai-news-radar/README.md | references/upstream-skill-readme.md | 14882 | cea932f854bbbc8473ec1a7fd58e5018833e338fcd7a645da2a3d9fbe1e6fa64 | reference notice and immutable upstream Markdown links; normalize trailing whitespace |
| docs/GPT_HANDOFF.md | docs/GPT_HANDOFF.md | 4650 | cea73994fee7ed4f4485ddb284d4bc66d55aa862412056ba2831ebeabf71f46e | reference notice and immutable upstream Markdown links |
| docs/ROADMAP.md | docs/ROADMAP.md | 5051 | ae5091f2fd10eed5f9e35d5471e4d5c4c70b6cf2ca445cca1db083edb8115934 | reference notice and immutable upstream Markdown links |
| docs/SOURCE_COVERAGE.md | docs/SOURCE_COVERAGE.md | 16386 | 14dc0f660bb5b4d5a89bcfa096ae4aad2d8adea876c5705cd601b9cf4ecc94f0 | reference notice and immutable upstream Markdown links |
| docs/V2_PRODUCT_BRIEF.md | docs/V2_PRODUCT_BRIEF.md | 2129 | ff52e938535276b18d70af846659adfecdf56d105310591bd4c6133a499dd2c3 | reference notice and immutable upstream Markdown links |
| site.webmanifest | site.webmanifest | 563 | 5659abfef2d7f05b9a6ace0a876ef8e4ea44e3cc00b0f82fd8b9626feea1d1b9 | none |
| classic/index.html | classic/index.html | 11772 | beeb670897d9aaadcd90b858b7faad260c4f3130cc8c505b52527bd4576f772b | normalize service-status asset links under upstream base href |
| scripts/__init__.py | scripts/__init__.py | 28 | c2bbbed5cc8ac8d07249f7d977b61fe2309393444646d0d449b6d7ce7dcf2434 | none |
| scripts/persona_score.py | scripts/persona_score.py | 16284 | 2076ac04af453de9a8c3704f83941fd8fa47b7c29bd3bc4679ec6ed47f001926 | none |
| classic/assets/app.js | classic/assets/app.js | 121340 | 08afcfe3e8184f3ab364ae7a8ae39f6e57ee2c376076b866c22aa029ad2c45a9 | none |
| classic/assets/motion.js | classic/assets/motion.js | 3185 | 90102cd08928d9389fa78dc83a666d58a423202591a3865dd67d78b1cbd95918 | none |
| classic/assets/styles.css | classic/assets/styles.css | 48135 | 1d07798dc15c4dd3360496ee2f8865611cba09db4fe3bfaded9a20b00b46cdff | none |
| personas/README.md | personas/README.md | 2379 | 3f751906d12eeec8945c6e4e903fb5407103df0c2106f2d589f1d3ac00f9dafd | none |
| personas/cynic.md | personas/cynic.md | 1611 | 72a3c6e4b8619f1568d56af45c57df8b7ff06f4fc80afd17b264df9d3903d6cb | none |
| personas/paper-police.md | personas/paper-police.md | 1679 | 12080a8c861872a214e8a250b63232dea1be53bb87263ed98ff65bd2deb64911 | none |
| personas/pragmatic.md | personas/pragmatic.md | 1674 | d61315341defc8b786aa435dadc19a3fbacd919aa5520644f68addcfd17a79b9 | none |
