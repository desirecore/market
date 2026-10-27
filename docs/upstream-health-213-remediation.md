# Upstream health report 213 remediation

Reviewed on 2026-10-19 against Market baseline `10cb7656db5cbdad21b181e050130942521b1ef7` (the upstream-health checker change in [market#222](https://github.com/desirecore/market/pull/222), on top of `main` at `a514b55b68771ff58d76ed64ac5f42be350f789b`).

Tracking issue: [market#213](https://github.com/desirecore/market/issues/213). This review covers the 28 entries the checker reported on 2026-10-19. It updates 24 pointers and adds three new public children with reviewed translations. Three pins stay on reviewed holds, and the watch finding was superseded on `main` (see below). Top-level inventory remains 8 Agents, 2 Teams and 144 Skills; the nine collections now contain 184 children.

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

Several upstreams moved again after this review, and the 2026-10-26 report lists newer heads. Those heads are not reviewed here. They, and any hold that their changes make stale, are left for the next round.

Validation covers catalog contracts, source retrieval, pinned paths, reproducible inventories and the reviewed hold contract. Third-party programs and live account services were not executed; their availability is not implied by a healthy pointer.
