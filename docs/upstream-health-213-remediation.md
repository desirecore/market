# Upstream health report 213 remediation

Reviewed on 2026-10-19 against Market baseline `10cb7656db5cbdad21b181e050130942521b1ef7` (the upstream-health checker change in [market#222](https://github.com/desirecore/market/pull/222), on top of `main` at `a514b55b68771ff58d76ed64ac5f42be350f789b`).

Tracking issue: [market#213](https://github.com/desirecore/market/issues/213). This review covers the 28 entries the checker reported on 2026-10-19. It updates 24 pointers and adds three new public children with reviewed translations. Three pins stay on reviewed holds, and the watch finding was superseded on `main` (see below). Top-level inventory remains 8 Agents, 2 Teams and 144 Skills; the nine collections now contain 184 children. A [follow-up review](#follow-up-review-2026-10-27) on 2026-10-27 covers the heads that moved after this review.

## Detector changes

This record depends on [market#222](https://github.com/desirecore/market/pull/222), which:

- Compares collections only within their declared child paths plus root LICENSE/NOTICE/COPYING files; undeclared upstream skills are still reported as `new-skill`.
- Reports reviewed `upstream-health-hold.json` findings as `held`, and turns them back into an actionable `stale-hold` when the pin or the installed-scope content changes after review.
- Links each `outdated` finding to the GitHub compare view.

## Reviewed holds

| Entry | Held findings | Why the pin stays |
|---|---|---|
| skill/geo-optimizer | upstream-path-change, outdated | Upstream renamed `seo/geo-optimizer/SKILL.md` to `WORKFLOW.md`. The new `skills/geo-optimizer/SKILL.md` is a one-line shim that reads `../../seo/geo-optimizer/WORKFLOW.md`, which references `../../docs/safety.md`. The client installs only the declared subtree, so repointing would install a broken skill. The only content change since the pin is a four-line Safety section. |
| skill/marketingskills | outdated | The new head adds sponsor messaging to agent-facing skill content: a referral-tagged promotion of the maintainer's commercial agent in ad-creative, and paid "Verified Partner" placements of a hosted site platform in six children's references and evals. |
| skill/nuwa-skill | outdated | SKILL.md now tells the agent to read `references/about-author.md` and recommend the author's other projects whenever a request goes beyond the skill's scope, so promotion reaches agent behavior. The README banner is a separate, time-limited campaign. |

A hold applies only to the recorded pin and the reviewed upstream head. Any later upstream change within the installed scope makes the hold stale, and the finding returns for review.

## Snapshot decisions

| Entry | Reviewed snapshot or diff | Decision |
|---|---|---|
| skill/agent-reach | [a19a171 → 94f06c1](https://github.com/Panniantong/agent-reach/compare/a19a171fa980a0785849596492e0af4db800c82f...94f06c1969dfc1834001269d79d3ad0972d9dee6) | Removes a maintainer-local conda prefix from the environment check; prerequisites unchanged. |
| skill/anatomy | [e948829 → 1482e84](https://github.com/wheresryan22/anatomy/compare/e9488296a44211c42701ff71705b7901470ec78f...1482e8469b0a9e0d8cc18ea2740a01423d29ae80) | A4/Letter PDF printing uses locally supplied Chrome and downloads nothing; disclosures and compliance updated. Example PDFs add about 15 MB to the installed snapshot. |
| skill/archify | [7158026 → 654da74](https://github.com/tt-a1i/archify/compare/7158026e852f3aa6578c741e673b46d7878c92c1...654da74e084e5a1faf708779c23d6172766be9c1) | Preserves upstream version 3.2 as an opaque identifier. Adds five diagram types and one-page explainers. Discloses the bounded update check and that proactive explainer mode edits the agent's global rules file only after the user accepts. |
| skill/blog-chart | [2500d4c → 3544423](https://github.com/AgriciDaniel/claude-blog/compare/2500d4c765034864cede2bf215d00ccd4d7d6fb8...354442348815a7f0327077ad89af2c43cf4b4ab4) | Upstream now marks it `user-invocable: false`, and the summaries call it an internal helper. Adds a local chart-input schema; chart data stays untrusted. |
| skill/blog-repurpose | [2500d4c → 3544423](https://github.com/AgriciDaniel/claude-blog/compare/2500d4c765034864cede2bf215d00ccd4d7d6fb8...354442348815a7f0327077ad89af2c43cf4b4ab4) | Adds honesty rules: drafts only, never posts, no invented first-hand stories or results. |
| skill/brainstorming | [8ca22db → bb92a77](https://github.com/obra/superpowers/compare/8ca22dba9a94f28898bbce59f2537ff4d87c747d...bb92a77741419a4ab5f06e711a283343f1ada0c3) | Rebuilt conversation flow keeps the approval gate. The optional visual companion binds 127.0.0.1 with a per-session key; its Node.js runtime and default upstream-logo telemetry are now disclosed. |
| skill/dingtalk-cli | [3f0fc94 → 92cb3f5](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/compare/3f0fc94111b1f9cd34e47468980b1f1a723ca69a...92cb3f513c457b9a3578b72ed870632e891dded3) | 16 children retained; contact adds friend management (removal needs confirmation) and recruiting leaves misc. NOTICE adds only an OpenSSL attribution for the separately installed CLI binary; Apache-2.0 unchanged. Unsupported domain and tool counts removed from the parent summary. |
| skill/follow-builders | [ec5b50e → 1c06b01](https://github.com/zarazhangrui/follow-builders/compare/ec5b50e3127ba9cc5e9c54ea7bf409b0654c7f39...1c06b01fa3dfb4ff1785c3e93ebf48c746c68586) | 14 bot feed refreshes only; instructions and scripts unchanged. License evidence remains unknown. |
| skill/humanizer | [225a6f3 → 8c307f3](https://github.com/blader/humanizer/compare/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8...8c307f367c91bd974002f10f2be2965d642c13df) | README sponsor line only; skill 3.1.0 instructions unchanged. |
| skill/humanlayer-skills | [ca7c808 → 653b641](https://github.com/humanlayer/skills/compare/ca7c8088db69e315a8b2deea43820270457f8f3c...653b6411c1f70c275a18e37673b042ff99f67ceb) | 6 to 7 children; adds the explicit-invocation rpi research-design-implement workflow. Root MIT license and review dates recorded. Reviewed summaries replace truncated or invocation-only upstream text; Git/GitHub CLI, CI and separately licensed coding-agent services disclosed. |
| skill/impeccable | [6e802bd → 0665bd8](https://github.com/pbakaus/impeccable/compare/6e802bd0ed99f53180e2359fddab6da8d97970d9...0665bd812ae0908fcab17b96fd4f840defb882d9) | Skill 4.6.0 with engine 0.1.15. The launcher still downloads from upstream GitHub releases and rejects files whose SHA-256 sidecar does not match. Optional detector hooks and desktop-app DevTools audits disclosed. |
| skill/larksuite-cli | [7beffb0 → 017b19a](https://github.com/larksuite/cli/compare/7beffb086d7fa3c5b843d8affa7c089f49cfc65e...017b19a793ad71794a02887ede04757f3d82e10d) | 28 children retained with no version changes. Adds task-section routing, Miaoda app export and the slides chart schema. Separate CLI and account disclosures still fit. |
| skill/last30days | [5103ba4 → 13a6cc5](https://github.com/mvanhorn/last30days-skill/compare/5103ba478b380552207a3754b74c7655d64208cd...13a6cc5fd1f2d8a9b8420bbba6742599b2f4a077) | Skill 3.28.0 splits SKILL.md into staged references. Adds opt-in keyless dev.to, a paid ScrapeCreators YouTube backfill and a Grok Bot host X lane. Python 3.12+, local saves outside the workspace and opt-in ht-ml.app publishing disclosed. |
| skill/mattpocock-skills | [24fe0ef → 49dd158](https://github.com/mattpocock/skills/compare/24fe0ef7737efae15c87225755e9f6f5965e4888...49dd158d1076134a641b33efb035946536778336) | 37 to 38 children; adds chief-of-staff from upstream's in-progress folder, manual invocation only and needs host subagents. Tracker-command fixes and safer wizard `.env` handling; no new external services. |
| skill/planning-with-files | [dab9d16 → d363544](https://github.com/OthmanAdi/planning-with-files/compare/dab9d16fbd9314448b319d112e99f497d7638d89...d363544caea69df35ba624b238662ab861d1d92a) | Skill 3.24.3. Hooks skip unchanged plan views using a private hash-only cache, and plan content stays framed as untrusted data. Automatic lifecycle hooks and their Python 3 requirement are now disclosed. |
| skill/planning-with-files-zh | [dab9d16 → d363544](https://github.com/OthmanAdi/planning-with-files/compare/dab9d16fbd9314448b319d112e99f497d7638d89...d363544caea69df35ba624b238662ab861d1d92a) | Skill 3.24.3. Hook scripts are byte-identical to the English edition; Python 3 for plan injection disclosed. |
| skill/redbookskills | [5d8e7bf → 9934a38](https://github.com/white0dew/XiaohongshuSkills/compare/5d8e7bfde98ab2b3618adf57670ea0b05650bdca...9934a380727a1c2229a753206d7958f132640bb0) | README sponsor swap with a 1 MB banner, plus star-history refreshes. SKILL.md and scripts unchanged and never surface the sponsor. |
| skill/reverse-engineer-anything | [951c2aa → dfe8378](https://github.com/morluto/rea/compare/951c2aae3be1c357df9f23558d8c09680e64c2cb...dfe8378cf5a727e3d93d47a5986233175c6ef898) | Records upstream skill revision 42 as an opaque identifier. Adds static and recorded-artifact inspectors and an agent-driven browser scenario tool; no guidance on bypassing protections. New third-party tools, Fiddler Everywhere licensing and browser-action authorization disclosed; compliance re-reviewed. |
| skill/systematic-debugging | [8ca22db → bb92a77](https://github.com/obra/superpowers/compare/8ca22dba9a94f28898bbce59f2537ff4d87c747d...bb92a77741419a4ab5f06e711a283343f1ada0c3) | Two-line fix: the example reports whether a secret is set without printing it. |
| skill/taste-skill | [ce26fc2 → a9c73c3](https://github.com/Leonxlnx/taste-skill/compare/ce26fc25c0e5e8cab638f883de62d9a86ee5e45b...a9c73c3d5dbf401e3e47f86e7b41f29ede1687df) | v2 rewrite with art-direction scripts and a real-browser inspector; no sponsorship or tracking in the installed folder. Node 22+/local Chrome, open-collection picture search, third-party page resources and a history file outside the workspace disclosed. No upstream skill version is declared. |
| skill/translate-book | [bd5424b → a663b1b](https://github.com/deusyu/translate-book/compare/bd5424b82399c8e4b4cf09310f31b21a103dde7f...a663b1b4f1e625b286cd2a81dffd16571e6f2aa2) | README commercial-sponsorship section only; skill content unchanged. |
| skill/video-use | [b877063 → 43cfc56](https://github.com/browser-use/video-use/compare/b877063835e6ea6e457124da7e28a0ae26691dc3...43cfc566833548093455c9d4a46bd69913b7e552) | README hosted-waitlist link only; the ElevenLabs upload disclosure is unchanged. |
| skill/wechatpay-skills | [9df6ba4 → 039b0ae](https://github.com/wechatpay-apiv3/wechatpay-skills/compare/9df6ba49f6f394f47ca1ee68bf9517d000b2c9d9...039b0ae50d6b5d4631be8ea991155f8a7958a2d9) | Preserves upstream version 1.3 as an opaque identifier. Coding integration and echo signature tests need consent, and signing scripts keep keys local. The online knowledge-base sync, which can replace skill files from the official CDN bundle, and the official CLI prerequisites are disclosed. |
| skill/wecom-cli | [c4b9b66 → 4c74ff2](https://github.com/WecomTeam/wecom-cli/compare/c4b9b6610c7ca2854441bfa336a5b458daeeb707...4c74ff28838d8fba267eaab5179d9d56f9ca61ae) | 14 to 15 children; adds wecomcli-pptx for WeCom online slides. It needs the separately installed wecom-cli 1.2.1+ and WeCom authorization, plus local Python 3, python-pptx/python-docx/openpyxl for material images and optional LibreOffice previews, all disclosed. |

skill/watch was reviewed at [0fd13b7 → 6565030](https://github.com/desirecore-agent/watch-video-skill/compare/0fd13b73b7b37318cada0562ba2263d648c8505f...6565030289dddc91107b20857f9cd24b8f6fbbae), where skill 1.1.1 declares yt-dlp, ffmpeg, ffprobe and python3. [market#221](https://github.com/desirecore/market/pull/221) has since pinned watch 1.1.2 on `main` and made it installable, so this change leaves watch untouched.

Shared upstreams were reviewed once per repository: obra/superpowers for brainstorming and systematic-debugging, OthmanAdi/planning-with-files for both editions, and AgriciDaniel/claude-blog for blog-chart and blog-repurpose. Each pair keeps an identical pin.

## Validation

Run on 2026-10-19 against the reviewed heads above:

- 122 unit tests pass across the i18n (19), catalog-metadata (51), collection-generator (10) and upstream-health (42) suites.
- Catalog metadata validation with `--require-complete`, i18n validation and translation freshness pass with 0 errors.
- All nine pinned collection inventories pass the read-only generation check.
- Online health checks all 111 external entries: no broken, unknown or actionable results. The only findings left were the four `held` findings of the three reviewed holds above; that run still included the watch pin later dropped in favor of market#221.
- `git diff --check` passes.

Catalog and i18n validation retain 104 earlier warnings, down from 106, with no new warning. The two removed warnings are the unverified humanlayer-skills license and its identical child translations. The remaining warnings concern existing license, review and provenance gaps and untranslated child summaries; this change does not claim to resolve those.

Several upstreams moved again after this review, and the 2026-10-26 report lists newer heads. Those heads, and the holds their changes made stale, are reviewed in the [follow-up review](#follow-up-review-2026-10-27) below.

Validation covers catalog contracts, source retrieval, pinned paths, reproducible inventories and the reviewed hold contract. Third-party programs and live account services were not executed; their availability is not implied by a healthy pointer.

## Follow-up review (2026-10-27)

Reviewed on 2026-10-27 against Market baseline `7e7b528b213b72593cebaf32505fc868bb792be9` (the round above, [market#227](https://github.com/desirecore/market/pull/227), stacked on market#222). On that baseline the online check reported 21 outdated pins, two stale holds and the still-valid geo-optimizer hold. This round repins 16 entries, refreshes the two stale holds and adds two new holds; the watch finding is again left to `main`. No children are added or removed, so the inventory above is unchanged.

### Reviewed holds

| Entry | Held findings | Why the pin stays |
|---|---|---|
| skill/agent-reach | outdated (new hold at 14c2134) | The 1.6.0 rebuild of the installed `agent_reach/skill` makes CloakBrowser, a stealth Chromium marketed to pass bot detection and shipped under a restrictive binary license, the default browser for logged-in platform channels, and copies site cookies from a connected Chrome on first use. The installed SKILL.md is also an unrendered template with `{{VERSION}}` and `{{CHANNEL_TABLE}}` placeholders. |
| skill/geo-optimizer | upstream-path-change, outdated | Unchanged from the first round. Upstream moved on to ed835f2, but nothing in the installed scope changed after the reviewed c839f30, so the hold still applies. |
| skill/marketingskills | outdated (refreshed to 17772c7) | The ad-creative referral promotion and the six children's paid "Verified Partner" placements are unchanged, and ai-seo adds a newly paid partner without a marker. Of the two new children, conversion-tracking is built around a paid partner's tracking service and tells the agent to repeat a fixed partner phrase; link-building carries no promotion. |
| skill/nuwa-skill | outdated (refreshed to 7c7edfe) | The only new commit removes the README campaign banner. SKILL.md is unchanged and still recommends the author's other projects whenever a request goes beyond the skill's scope. |
| skill/wecom-cli | outdated (new hold at 55785fa) | The only installed-scope change is a wecomcli-sheet rewrite. Its new `scripts/recalc.py` and `references/xlsx-process.md` are adapted, without attribution, from the source-available xlsx skill in anthropics/skills, whose terms forbid copying, derivative works and redistribution, while the repository declares MIT for everything. The script's LibreOffice macro and LD_PRELOAD socket shim match the market's own `skills/xlsx`, which ships them under that skill's notice; a later bump must disclose both. |

The marketingskills `new-skill` finding (conversion-tracking, link-building) stays actionable. Holds cover only `upstream-path-change` and `outdated`, and the new children cannot be declared while the pin predates them.

### Snapshot decisions

| Entry | Reviewed snapshot or diff | Decision |
|---|---|---|
| skill/archify | [654da74 → 81c6be8](https://github.com/tt-a1i/archify/compare/654da74e084e5a1faf708779c23d6172766be9c1...81c6be8d87090670c45d08a8f97f9d29c5af0bec) | Upstream relicensed from MIT to Apache-2.0; the earlier MIT grants stay in LICENSE-MIT and NOTICE, and generated pages now embed these notices. License recorded as Apache-2.0. Version 3.2, the update check and the opt-in global-rules edit are unchanged. |
| skill/banana | [6a2b1b5 → 08e329b](https://github.com/AgriciDaniel/banana-claude/compare/6a2b1b51fdcc35932184f06e513646a6f6f4f7d8...08e329b37dae396fc869c10d3494c5950d1d61c2) | Skill 3.1.0 makes Nano Banana 2.1 the default model on the same Gemini Developer API and GEMINI_API_KEY. Records the version; Python 3.11+, paid Gemini billing including thinking tokens, Search-grounding retention and local writes outside the workspace are disclosed. |
| skill/brainstorming | [bb92a77 → 2ce8aa1](https://github.com/obra/superpowers/compare/bb92a77741419a4ab5f06e711a283343f1ada0c3...2ce8aa15d05bd57213e6f746f953aafb7ded7a8b) | SKILL.md-only retune (v7.0.1): read the referenced project context first, lay out approaches, then approve a short or full design doc. The visual companion files are byte-identical, so its Node.js and logo-telemetry disclosure still holds. |
| skill/dingtalk-cli | [92cb3f5 → ee61f89](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/compare/92cb3f513c457b9a3578b72ed870632e891dded3...ee61f8945d8b1df6b840d2303152574f31a6f1f8) | 16 children retained; CLI minimums unchanged. Adds standalone mind maps, AI-table role members, app visibility scope and placeholder A2UI cards on replies; full replacements and deletes need confirmation. Apache-2.0 and NOTICE unchanged. |
| skill/follow-builders | [1c06b01 → 3b2cf91](https://github.com/zarazhangrui/follow-builders/compare/1c06b01fa3dfb4ff1785c3e93ebf48c746c68586...3b2cf91f0a01a8dece4b4d9ebb29c4c8beb298a6) | Nine bot feed refreshes only; instructions and scripts unchanged. License evidence remains unknown. |
| skill/frontend-slides | [ef648e0 → 25278e7](https://github.com/affaan-m/ECC/compare/ef648e01899ba3e8dc6371642deaaf64b4477775...25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b) | Three-line `export-pdf.sh` path fix. The pre-existing PDF helper's Playwright and Chromium download and the web-font hosts are now disclosed. |
| skill/himalaya | [6ddf5a6 → 9adda02](https://github.com/openclaw/openclaw/compare/6ddf5a6106c18c4cf803a601b3a099e497d943fb...9adda02605eca1f45eb10f009dd4c3e575713032) | Documentation fix for copy/move (`--to <folder>`) and raw MIME reads. The separately installed CLI, the operator's mail account and credentials, and the lack of a built-in send/delete confirmation are now disclosed. |
| skill/impeccable | [0665bd8 → d34c87e](https://github.com/pbakaus/impeccable/compare/0665bd812ae0908fcab17b96fd4f840defb882d9...d34c87e1a00989ae8dbdd7f6b30b70f23319e860) | Skill 4.8.0 with engine 0.1.18. Downloads must now match SHA-256 digests shipped in the pinned skill instead of a sidecar fetched beside the binary. The unsandboxed, non-blocking hook and the existing optional OpenAI image-API fallback are disclosed. |
| skill/larksuite-cli | [017b19a → a92db87](https://github.com/larksuite/cli/compare/017b19a793ad71794a02887ede04757f3d82e10d...a92db8779c0959bc14beb69d82fb262123cfb79b) | 28 children retained with no version changes; only the lark-apps cloud-dev polling guidance changes. Disclosures still fit. |
| skill/last30days | [13a6cc5 → e06af25](https://github.com/mvanhorn/last30days-skill/compare/13a6cc5fd1f2d8a9b8420bbba6742599b2f4a077...e06af25a9a78487b75e8509e0e1687fec137176e) | Skill 3.31.0 adds a keyless Arctic Shift comment fallback, `--official-site` homepage lookup, a local audit of each new grok CLI build and Dia in the opt-in cookie list. Bright Data, the grok lane, the audit cache and the new endpoints are disclosed. |
| skill/mattpocock-skills | [49dd158 → 59db609](https://github.com/mattpocock/skills/compare/49dd158d1076134a641b33efb035946536778336...59db609eb1e18aaf59b63284d0e52255aff0c63c) | 38 children retained. chief-of-staff stays manual-only and now keeps a dated wiki in a folder agreed with the user; tracker setup files issues only in the user's own repository. No new external services. |
| skill/planning-with-files | [d363544 → dcdfb27](https://github.com/OthmanAdi/planning-with-files/compare/d363544caea69df35ba624b238662ab861d1d92a...dcdfb278de53fdb69b2067ea173dbb1de45345a3) | Skill 3.25.2. New plans start from the bundled initializer, and a read-only `check-complete --validate` checks the format; lifecycle hooks unchanged. |
| skill/planning-with-files-zh | [d363544 → dcdfb27](https://github.com/OthmanAdi/planning-with-files/compare/d363544caea69df35ba624b238662ab861d1d92a...dcdfb278de53fdb69b2067ea173dbb1de45345a3) | Skill 3.25.2 with the same localized creation contract and format check. Hook scripts are still byte-identical to the English edition. |
| skill/redbookskills | [9934a38 → 52622b4](https://github.com/white0dew/XiaohongshuSkills/compare/9934a380727a1c2229a753206d7958f132640bb0...52622b4a57ef44ce11e0827938948d9a2a7c5ef8) | Nine bot star-history refreshes only; SKILL.md, scripts and README unchanged. |
| skill/reverse-engineer-anything | [dfe8378 → 79d2fc0](https://github.com/morluto/rea/compare/dfe8378cf5a727e3d93d47a5986233175c6ef898...79d2fc05405c76bc0a8f71b9c10355135da4747b) | Records upstream revision 50 as an opaque identifier, with rea-agents 6.8.0 on patched Node releases. Adds agent environment bundles recorded from disposable web-app instances (AgentEnv and Docker) and Frida, debugger and process-capture workflows, still without protection-bypass guidance. New tools and authorization gates disclosed; compliance re-reviewed. |
| skill/taste-skill | [a9c73c3 → 12af471](https://github.com/Leonxlnx/taste-skill/compare/a9c73c3d5dbf401e3e47f86e7b41f29ede1687df...12af471f627f866411b4bd785b19646d3672784c) | Maintenance fixes: quoted frontmatter so the skill loads, safer profile cleanup, escaped chart labels, accessibility guidance and a dev-server warning. Nothing new is fetched, installed or promoted; no skill version is declared. |

Planning-with-files was reviewed once for both editions, which keep an identical pin. Other entries on obra/superpowers, openclaw/openclaw and affaan-m/ECC keep their pins because their installed scope did not change, so brainstorming, himalaya and frontend-slides now sit on newer commits than their siblings.

skill/watch is outdated on this baseline only because the baseline predates [market#221](https://github.com/desirecore/market/pull/221); `main` already pins its current head, 4fa94ac.

### Validation

Run on 2026-10-27 against the reviewed heads above:

- 122 unit tests pass across the i18n (19), catalog-metadata (51), collection-generator (10) and upstream-health (42) suites.
- Catalog metadata validation with `--require-complete`, i18n validation and translation freshness pass with 0 errors. The 104 earlier warnings are unchanged, and none is new.
- All nine pinned collection inventories pass the read-only generation check.
- The online health check covers all 111 external entries on this branch. Nothing is broken or unknown, and six `held` findings cover the five holds above. Two findings remain actionable: the marketingskills `new-skill` finding and the watch pin, which is already current on `main`.
- The same check on this branch merged with `main` at `aa6a1a6` covers 112 entries, including agent/video-director, which resolves again. It leaves only the held findings and the marketingskills `new-skill` finding. Two transient TLS failures in that run passed when rechecked individually.
- `git diff --check` passes.

Still open after this round:

- The marketingskills `new-skill` finding, until the sponsor content is removed or accepted, or until a hold can cover undeclared children.
- follow-builders and redbookskills install their whole repository, so bot commits will flag them as `outdated` again within days.
- For the next review: at the current wecom-cli pin, `wecomcli-pptx/references/templates/anti-ai-slop.md` names the source-available pptx skill in anthropics/skills as one source of a reworded checklist.

Third-party programs and live account services were not executed.

## Later correction (2026-10-31)

`skill/reverse-engineer-anything` recorded upstream revision `50` in `latestVersion` and `release.version`. The client pointer contract admits only numeric `x.y` or `x.y.z`, so clients dropped the listing from their index, and the catalog validator did not check skill pointers against that contract. The repin and its review stand. The listing now declares no version (`release: unknown`), and the validator checks skill pointers against the [exported client schema](../schemas/market-skill-entry.client.schema.json).
