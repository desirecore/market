# Upstream health report 189 remediation

Reviewed on 2026-10-05 against Market baseline `04042d44bff2503095840597696450a9fcdeb4f8`.

Tracking issue: [market#189](https://github.com/desirecore/market/issues/189). This review updates 26 pointers, pins both previously mutable collections, and leaves two identical-tree Agent pins unchanged. Top-level inventory remains 7 Agents, 2 Teams and 73 Skills; the nine collections contain 181 children.

## Detector repairs

- Resolve exact branch refs so `changeset-release/main` cannot be selected as `main`.
- Discover exact tracked `SKILL.md` files; exclude symlinks, fixtures, missing frontmatter names and `metadata.internal: true`.
- Check installed paths at the pin; report branch-head moves separately when the installed pin still resolves.
- Ignore identical Git trees and unrelated single-skill subtree feed/site changes, while retaining root license/notice review.
- Treat transient fetch failures as unknown. JSON workflow decisions keep unpinned and unknown entries visible.
- Apply reviewed child translations from fixed presentation-only overrides; reject missing IDs or attempts to override source facts.

## Snapshot decisions

| Entry | Reviewed snapshot or diff | Decision |
|---|---|---|
| agent/dingtalk-workspace | [746d011 → 186d850](https://github.com/desirecore-agent/dingtalk-workspace/compare/746d011a64db4061a68e512f3e5aaa4c0ec5abe5...186d850da13edbaceab5bb9cccffe5ff7cff6a12) | AGENTS.md/CLAUDE.md update-delivery documentation only; Agent version remains 1.0.1. |
| agent/feishu-orchestrator | [8f1d810 → 3b22436](https://github.com/desirecore-agent/feishu-orchestrator/compare/8f1d8102f4b934c8b7f0999c325a59a4e7b3b86c...3b22436d4c0a98124946fe935f816fde1b49fa4f) | AGENTS.md/CLAUDE.md update/fork documentation only; Agent version remains 1.0.1. |
| agent/invoice-organizer | [4970ade → d22395a](https://github.com/desirecore-agent/invoice-organizer/compare/4970adebc906d83dd35953ea00aa941eb3dcfed5...d22395a0c9387b283ab5b86d6a66a47d48e29f75) | AGENTS.md/CLAUDE.md update-delivery documentation only; Agent version remains 1.1.2. |
| agent/mimo-model-quota-monitor | [0abbfc2 → 5e68bab](https://github.com/desirecore-agent/mimo-model-quota-monitor/compare/0abbfc28f4fe3fffd6da0708a361a9c0a1fe15b9...5e68bab7afacb54705f7cc99c337ec3b6d4ebb84) | AGENTS.md/CLAUDE.md update-delivery documentation only; Agent version remains 1.0.1. |
| agent/tender-review-assistant | [d58ed0a → 5bc9ebf](https://github.com/desirecore-agent/tender-review-assistant/compare/d58ed0a0de03628357e8d9fd166ba929c2c275ba...5bc9ebf036be63c0c9e01f04658e84dde2836807) | Identical Git tree: retain the reviewed pin and version. |
| agent/wecom-assistant | [d08336c → 4e040ea](https://github.com/desirecore-agent/wecom-assistant/compare/d08336c6080e40f178a33d11b811b91a98f48ce9...4e040eab6c2198babcfaa15b764a373d261b4a7c) | Identical Git tree: retain the reviewed pin and version. Merge metadata alone no longer triggers an update. |
| skill/agent-reach | [e825f67 → a19a171](https://github.com/Panniantong/agent-reach/compare/e825f6740d24c6c315c3b0dc41907e6c87ff39a5...a19a171fa980a0785849596492e0af4db800c82f) | Channel/browser and credential handling reviewed; needs operator-installed CLIs and authorized platform sessions. |
| skill/ai-news-radar | [f23ce28 → 6893951](https://github.com/LearnPrompt/ai-news-radar/compare/f23ce289695aaf8808f4c19b0b815b51b20730a9...689395109cc962a27c369bdd6fa50d1e090eb319) | Opt-in QQ Agent Mail adapter reviewed. Generated news-feed refreshes do not change the installed skill subtree. |
| skill/archify | [c1443b3 → 7158026](https://github.com/tt-a1i/archify/compare/c1443b31b496eebf4a68bf83151816c955ddb796...7158026e852f3aa6578c741e673b46d7878c92c1) | Preserves upstream version 3.0 as an opaque identifier; Node/browser prerequisites and verification boundaries disclosed. |
| skill/baoyu-skills | [6b7a2e4 → 1567581](https://github.com/JimLiu/baoyu-skills/compare/6b7a2e417500561a5ecdd0b168332f4142584617...1567581c26ec29f4216c6e6835415bf30343b0e3) | 21 public children retained; baoyu-image-gen 2.2.0 and provider guidance updated. External API entitlements remain separate. |
| skill/dingtalk-cli | [pin 3f0fc94](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/tree/3f0fc94111b1f9cd34e47468980b1f1a723ca69a) | Pins exact main; 15 to 16 public children, adds dingtalk-aicard. Internal mono and lowercase reference documents excluded; bilingual summaries retained. |
| skill/flyai-skill | [54277b2 → 86fe2cc](https://github.com/alibaba-flyai/flyai-skill/compare/54277b27b68e53741954c08541faedba1d45cc7b...86fe2cc3e25464d0e0bd6a769b27b5f9f3b04128) | README/support and notification workflow only; skill version remains 1.0.15. |
| skill/follow-builders | [239227d → ec5b50e](https://github.com/zarazhangrui/follow-builders/compare/239227ddea46dfb9db6ed23e5864a5fabb9cee83...ec5b50e3127ba9cc5e9c54ea7bf409b0654c7f39) | Public feed and delivery references reviewed; optional delivery needs operator credentials and authorization. License evidence remains unknown. |
| skill/humanizer | [523374d → 225a6f3](https://github.com/blader/humanizer/compare/523374dee72d67c7b2b5f858ea0094ffda49c3ac...225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8) | Skill 3.1.0; editing preserves factual content and treats supplied text as material. |
| skill/humanizer-zh | [91f3d39 → f4518a8](https://github.com/op7418/Humanizer-zh/compare/91f3d394db8419c20d67ebe22a96cf8fee0a404b...f4518a8eab97b8bfebc66a89d34320a89bef6930) | Editing rules preserve facts and author voice; supplied text remains data. No upstream release version is declared. |
| skill/ian-xiaohei-illustrations | [91b5608 → 4102eb8](https://github.com/helloianneo/ian-xiaohei-illustrations/compare/91b560849e8f883922cc2fa8a358a668caa94105...4102eb807f03bcb6e538a16e8b31b41db8b5b954) | README punctuation only; skill content unchanged. Image-provider prerequisites disclosed. |
| skill/impeccable | [e4ab5e2 → 6e802bd](https://github.com/pbakaus/impeccable/compare/e4ab5e24bdf5321b72163d2fbcbe6fa985c848ba...6e802bd0ed99f53180e2359fddab6da8d97970d9) | Skill 4.5.0; standalone binary launcher and its first-run download/fallback disclosed. |
| skill/khazix-skills | [d4e43c9 → 322346d](https://github.com/KKKKhazix/khazix-skills/compare/d4e43c91f16dcd859748c1d71ec7d8aa1ebb4694...322346ded8129436b3f64707789a73e732ae24d9) | 5 to 6 children; adds leader. AIHOT service/data terms are distinct from the MIT license on skill files. |
| skill/larksuite-cli | [a257fcb → 7beffb0](https://github.com/larksuite/cli/compare/a257fcbaf9f07787b6c170d9265e9ef273b0c579...7beffb086d7fa3c5b843d8affa7c089f49cfc65e) | 28 children retained; lark-base 1.2.23 and lark-sheets 3.5.2. Separate CLI, account scopes and product entitlements disclosed. |
| skill/last30days | [a218eda → 5103ba4](https://github.com/mvanhorn/last30days-skill/compare/a218edadbc3361672f5e5e2cd72a8212b0b3fbb8...5103ba478b380552207a3754b74c7655d64208cd) | Skill 3.26.0; source outcomes, optional API accounts and browser-consent requirements reviewed. |
| skill/marketingskills | [7868cb9 → dda3841](https://github.com/coreyhaines31/marketingskills/compare/7868cb9251fad80a73d26e488a5ad5f6c4a9f335...dda3841f0b294e01e93b1541486beefbfab0915e) | 49 to 50 children; adds events. Updated marketing guidance and optional paid-tool prerequisites disclosed. |
| skill/mattpocock-skills | [pin 24fe0ef](https://github.com/mattpocock/skills/tree/24fe0ef7737efae15c87225755e9f6f5965e4888) | Pins exact main; 35 to 37 children. Removes resolving-merge-conflicts; adds implement-spec, pr and retro at skills/engineering/. |
| skill/mt-paotui-for-client | [dc5cc22 → 05ead23](https://github.com/meituan/MT-Paotui-For-Client/compare/dc5cc223a010c2fe4377088affc2fbe4c6c6473d...05ead232ae2b94b9b55b2a1e126e039a1cb6db00) | Order/authentication flow reviewed; account authorization, real-order confirmation and separate charges disclosed. License evidence remains unknown. |
| skill/nuwa-skill | [27642f5 → fe03746](https://github.com/alchaincyf/nuwa-skill/compare/27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7...fe0374687037c4cc51a65c1e0c145afe2981dc69) | Adds a bounded update notice; updating remains the user's decision. |
| skill/taste-skill | [ccbc156 → ce26fc2](https://github.com/Leonxlnx/taste-skill/compare/ccbc15639c97057cbfcf32ecebc38ef716e4bb37...ce26fc25c0e5e8cab638f883de62d9a86ee5e45b) | README sponsorship changes only; installed skill content unchanged. |
| skill/watchless | [a09c0ed → 34e2fa8](https://github.com/chenzixin1/watchless/compare/a09c0edc6c3121c05e9824ef556256441d291d4f...34e2fa861a2e31bb4197e9e0a7b8d90e76ebeb6b) | Default ASR changes to Tencent Cloud; separate credentials, billing and audio-transfer permission disclosed. |
| skill/wechatpay-skills | [8573bdc → 9df6ba4](https://github.com/wechatpay-apiv3/wechatpay-skills/compare/8573bdc38b86fa67a42acfc422d6b4dbca4ada21...9df6ba49f6f394f47ca1ee68bf9517d000b2c9d9) | Preserves upstream version 1.2 as an opaque identifier; merchant authorization is separate from document lookup. |
| skill/wecom-cli | [78c514b → c4b9b66](https://github.com/WecomTeam/wecom-cli/compare/78c514b2afee7c0d3d7be715628478421f37ee63...c4b9b6610c7ca2854441bfa336a5b458daeeb707) | 14 children retained; minimum CLI 1.2.1 and python-docx/openpyxl generation prerequisites disclosed. |

## Validation

- 99 unit tests pass across i18n, catalog, collection-generator and upstream-health suites.
- Catalog coverage, i18n validation and translation freshness pass.
- All nine pinned collection inventories pass the read-only generation check.
- Online health reports 41 checked entries, no broken pointers, no actionable findings and no unknown results.
- Python and workflow shell syntax, plus `git diff --check`, pass.

Catalog validation retains 105 earlier warnings, down from 123, with no new warning groups. They concern existing license/review/provenance gaps and untranslated child summaries outside the new reviewed translations. This change does not claim to resolve those separate catalog-wide gaps.

Validation covers catalog contracts, source retrieval, pinned paths and reproducible inventories. Third-party programs and live account services were not executed; their availability is not implied by a healthy pointer.
