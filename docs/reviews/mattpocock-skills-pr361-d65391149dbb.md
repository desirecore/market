# PR361 实际安装范围许可复审

旧 pin：`5863806dd4e15c63174bee4e7515a4256792ecfa`；目标 pin：`d65391149dbb5fe76478e76fa8d5122b2aa5a70e`。

## 2026-11-27 07:43:23（新加坡时间 UTC+8）官方审核通过并签发新 pin 回执

官方 `audit_snapshots` 已对 pin `d65391149dbb5fe76478e76fa8d5122b2aa5a70e` 通过，并签发绑定该 pin 的新回执；`reviewedRef` 与范围已同步为新 pin、39 条 paths。旧回执未延伸到新 pin。这不是许可例外，也不代表安全认证或运行验收。

依据：

1. 客户端 [desirecore#6426](https://github.com/desirecore/desirecore/pull/6426) squash `28128a15b3abd76e1529b983ca8a921bdfe9ff30`（tree `e8c1321e6a098eb905f4646b2027bc7b2259ca6b`）已合入 `dev`。2026-11-27 00:04:23（新加坡时间 UTC+8）安装回读：39/39 子项副本都附上名为 `LICENSE` 的普通文件（`sourceName=LICENSE`，无命名冲突），哈希 `0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`。源树 39/39 子目录仍无 LICENSE。
2. [market#374](https://github.com/desirecore/market/pull/374) 增加 `acceptedClientAttachedNotices` 与 `acceptedDescriptionAndLocales`（最终 head `ccdd35dea8d66a7a97b324caff167a0582805bfe`；相关测试 150 passed / 190 subtests）。本分支用正常 merge 合入该挂钩，未合并 #374。
3. `acceptedDependencyIdentities` 绑定根 `package.json`（SHA-256 `405ad26c331e1f345de2221f2d8883083f0b9d4f29bc5aba06e683c6c866c235`，已去掉 version）与 `package-lock.json`（git blob `2787482775ab39d301710ce8b78ce1bb3730a98b`），对应已复核的 `yaml@^2.9.1` 与 `check-frontmatter` 脚本。
4. `acceptedDescriptionAndLocales` 绑定 chief-of-staff 的旧/新 pin、新 frontmatter 哈希 `a7e51a294e73a8b36aa90d1d90ad281e397bf7b5e9cbc544469b52de09409242`，以及已更新并与 catalog 镜像一致的中英 `shortDesc`。

回执 `reviewedAt`：`2026-11-26T23:43:23Z`（新加坡时间 2026-11-27 07:43:23 UTC+8）。`upstream-audit.v1.json` 现绑定新 pin、39 条 paths。

## 2026-11-27 更新（新加坡时间 UTC+8）

客户端 [desirecore#6426](https://github.com/desirecore/desirecore/pull/6426) 已 squash 合入 `dev`：`28128a15b3abd76e1529b983ca8a921bdfe9ff30`（tree `e8c1321e6a098eb905f4646b2027bc7b2259ca6b`）。当前 `dev` 已前移到 `accccc6747ac0ead52d0be248f9918130164d0e0`，该修复仍在历史中，且 `attachRootNoticeFiles` 代码未被改动。

2026-11-27 00:04:23（新加坡时间 UTC+8）用与 `28128a15…` 同一 tree 的 `stageMarketSkillDirectory` 做了诚实安装回读：39/39 子项安装副本都附上了名为 `LICENSE` 的普通文件（`sourceName=LICENSE`，无命名冲突），哈希与合集根 LICENSE 一致：`0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`。源树 39/39 子目录仍无 LICENSE。权威是安装副本里的完整 MIT 文本，不是审核时看到根 LICENSE。

市场侧专项复核挂钩已写入 [market#374](https://github.com/desirecore/market/pull/374)（head `dd8707029923bf9c9371f0d2e3d176a853c87a12`），并用正常 merge 合入本分支（merge `2c74a8eda913c17c08910b7044f5980c1020a9ee`）。`inspect_snapshots` 在绑定当前 pin、已核验客户端提交和逐项回读后，将 39 项 `installed-project-notice` 记为 `info`，不再因源子目录缺 LICENSE 而 blocked。这不是许可例外，也不能自动延伸到新 pin。

此前官方 `audit_snapshots` 在通知门禁清除后，曾被以下专项复核项挡住；这些项已在本次正式审核中绑定并通过对应当前 hook：

1. 根 `package.json` / `package-lock.json` 变化：新增开发依赖 `yaml@^2.9.1` 与 `check-frontmatter` 脚本（包版本 0.0.0→1.3.2；package.json 身份比较会去掉 version）。此变化此前已人工复核，可用既有 `acceptedDependencyIdentities` 绑定哈希，但须与完整通过的审核一起写入。
2. `skills/in-progress/chief-of-staff/SKILL.md` 上游简介变化。本分支已人工更新中英 `shortDesc`，但 `description-and-locales` 在条目已有 i18n 时仍为 `manual_review`；现行 schema 没有能把该项从 `manual_review` 清成可通过的字段。这些阻塞随后已通过 `acceptedDependencyIdentities` 与 `acceptedDescriptionAndLocales` 解除，见上文正式回执。

以下为 2026-11-25 对源树子目录的历史复审（源树结论仍成立，但不再是安装副本交付的最终结论）。

## 结论

**（历史源树结论，仍然成立于源目录）** 39/39 个可发现子技能的源树安装范围仍缺完整必要 MIT 通知。该结论已被安装回读取代为交付证据：安装副本携带根 LICENSE。正式新 pin 回执已在上文签发。

根 LICENSE 实际全文已读，要求在复制品或实质部分中包含 copyright notice 和 permission notice。根 LICENSE SHA-256 为 `0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`。完整固定源码归档逐个扫描每个子目录及全部文件：没有子目录 LICENSE/NOTICE/COPYING，也没有任何文件含 `Copyright (c) 2026 Matt Pocock`、`Permission is hereby granted` 或完整根 MIT 文本。不把一行 MIT 声明/目录 evidencePath 当成通知全文。

客户端固定源码复核：
- [market-install.ts L406-L446](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/capability-discovery/market-install.ts#L406-L446)：对子项选择 `join(contentDir, child.path)`，传给 staging。
- [skill-staging.ts L26-L74](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/capability-discovery/skill-staging.ts#L26-L74)：只复制选中目录，未附根通知。

这是安装范围与通知交付阻塞，不是上游许可未知，也不是发现安全漏洞。当前市场 PR 不能在不改客户端/上游交付的情况下消除该阻塞；不使用本地重打包、删资源、改子项路径或扩大例外来绕过。需要后续单独授权上游每个子目录附必要通知，或客户端随安装副本附通知；本轮均未实施。仍保留原 source/ref、子项点选路径与历史许可证据。

## 已完成的可独立修复

- 38→39项登记，补 software-factory 两种语言及手动调用/设计非执行授权边界；这是旧 YAML 引号修复重新被发现，上游技能文件新增/移除/移动均0。
- 更新 chief-of-staff 两种语言及可再生成覆盖：工作委派、日期/提交依据 wiki、遇阻后先提议环境改进；不谎称 recurring job 已移除，wiki/Git/跟踪工具写入和定期任务仍需用户授权。
- 全部34项既有英文回退补中文，并纳入持久覆盖；不是将其误报为本次引入。
- 两份派生目录、39项计数和双语描述同步。未写新审核日期，旧 reviewedRef 与 upstream-audit 回执保留。
- 精确复读 yaml 开发依赖及锁文件、frontmatter 校验脚本，记录内容哈希；未执行上游代码。该脚本只读本地技能文件并解析 YAML，无网络/写盘/命令执行；开发依赖不是终端技能运行依赖。

## 每个实际安装范围

| 子路径 | 普通文件数 | 必要根MIT通知 |
|---|---:|---|
| `skills/engineering/ask-matt` | 3 | 缺失 |
| `skills/engineering/code-review` | 2 | 缺失 |
| `skills/engineering/codebase-design` | 4 | 缺失 |
| `skills/engineering/diagnosing-bugs` | 3 | 缺失 |
| `skills/engineering/domain-modeling` | 4 | 缺失 |
| `skills/engineering/grill-with-docs` | 2 | 缺失 |
| `skills/engineering/implement` | 2 | 缺失 |
| `skills/engineering/implement-spec` | 2 | 缺失 |
| `skills/engineering/improve-codebase-architecture` | 3 | 缺失 |
| `skills/engineering/pr` | 3 | 缺失 |
| `skills/engineering/prototype` | 4 | 缺失 |
| `skills/engineering/research` | 2 | 缺失 |
| `skills/engineering/retro` | 2 | 缺失 |
| `skills/engineering/setup-matt-pocock-skills` | 7 | 缺失 |
| `skills/engineering/tdd` | 4 | 缺失 |
| `skills/engineering/to-spec` | 2 | 缺失 |
| `skills/engineering/to-tickets` | 2 | 缺失 |
| `skills/engineering/triage` | 4 | 缺失 |
| `skills/engineering/wayfinder` | 2 | 缺失 |
| `skills/engineering/wizard` | 3 | 缺失 |
| `skills/in-progress/chief-of-staff` | 2 | 缺失 |
| `skills/in-progress/claude-handoff` | 2 | 缺失 |
| `skills/in-progress/loop-me` | 2 | 缺失 |
| `skills/in-progress/setup-ts-deep-modules` | 3 | 缺失 |
| `skills/in-progress/software-factory` | 6 | 缺失 |
| `skills/in-progress/writing-beats` | 2 | 缺失 |
| `skills/in-progress/writing-fragments` | 2 | 缺失 |
| `skills/in-progress/writing-shape` | 2 | 缺失 |
| `skills/misc/git-guardrails-claude-code` | 3 | 缺失 |
| `skills/misc/migrate-to-shoehorn` | 2 | 缺失 |
| `skills/misc/scaffold-exercises` | 2 | 缺失 |
| `skills/misc/setup-pre-commit` | 2 | 缺失 |
| `skills/productivity/grill-me` | 2 | 缺失 |
| `skills/productivity/grilling` | 2 | 缺失 |
| `skills/productivity/handoff` | 2 | 缺失 |
| `skills/productivity/teach` | 6 | 缺失 |
| `skills/productivity/to-questionnaire` | 2 | 缺失 |
| `skills/productivity/wait-what` | 2 | 缺失 |
| `skills/productivity/writing-for-agents` | 3 | 缺失 |

逐文件 SHA-256、固定源归档哈希、结构化声明与依赖复审证据见同名 JSON。JSON 的 status=blocked，并非可用于宣称自动成功的专项接受记录。市场既有审计器并未核验通知实际携带；即便其静态 delta 项通过也不能推翻本阻塞，本次不伪造新成功回执。

## 本地实测结果（未宣称审计通过）

- 全量 `pytest -q scripts`：200 passed / 397 subtests passed（仅仓库本身测试，未运行上游代码）。
- `translate.py skills/mattpocock-skills --check`：exit 0。
- 39项路径集合、78条双语描述与覆盖/两份目录一致；旧回执内容和旧 reviewedRef 完整保留。
- `git diff --check`：通过。
- `validate_catalog_metadata.py --require-complete` 和 `validate-i18n.py`：各 exit 1，同样3个真实错误：reviewedRef 不匹配新 pin、旧回执 provenance 不匹配、旧38项回执 scope 不覆盖新39项。未通过修改旧回执抹掉错误。另104条既有警告，不作为本次成功证据。
- 新pin audit / required checks 不宣称全部通过；缺通知阻塞解决前，不生成成功新回执，不转正式，不合并。
