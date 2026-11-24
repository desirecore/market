# 原上游交付与市场准入边界复核（2026-11-25）

本次只纠正市场文案/审计注释，不改变来源、安装方法、资源或准入回执。不把合集改成本地整包，也不为规避预算删演示、压包或加按需 fetch。

## 原仓库大小不是“上游技能不可用”

| 固定来源 | 整库跟踪文件 | 市场所选路径 | 超过 1 MiB 的文件合计（不是整个包） |
| --- | --- | --- | --- |
| gif-factory@e89003a4a6ca4fd0e9e39c8859851b58c82bc368 | 1295 文件 / 925968044 bytes（883.07 MiB） | 整库 | 245 文件 / 676.31 MiB |
| stickman-video-director@10287822ba47579321068da1b93801face9160dd | 2207 文件 / 955317387 bytes（911.06 MiB） | skills/directing-stickman-videos：1970 文件 / 579433740 bytes（552.59 MiB） | 整库 176 / 812.54 MiB；所选路径 112 / 465.81 MiB |

数据来自固定 Git tree 的普通 blob 大小，不含 .git、压缩包传输或依赖下载。GIF 的 examples 约 452.21 MiB、skills 约 405.13 MiB；stickman 所选路径 assets 约 543.61 MiB，包含原有口播/音视频库、参考图等。保留这些资源。

市场 [`audit_skill_update.py`](../scripts/catalog/audit_skill_update.py) 的自动审计默认值是单文件 1 MiB、总计 50 MiB、2000 文件；`budgetExemptPaths` 只影响单文件阈值，不放宽总量。它们是审计策略，不是 Git 原生安装限制；不能只因超过 50 MiB 就宣称上游不能用。stickman 所选路径文件数 1970 也未超过 2000。

客户端本次固定核查版本为 [e817d57e](https://github.com/desirecore/desirecore/commit/e817d57e819975052c5da610874b7747de18b7c8)：

- [source-fetch-contract.ts L22–47](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/sync/source-fetch-contract.ts#L22-L47)：Git 缓存默认对象库 256 MiB、检出 200 MiB、缓存 2 GiB；内部调用可通过 `SourceFetchOptions.limits` 覆盖，故不是不可配置的绝对上限。
- [source-cache.ts L242–258](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/sync/source-cache.ts#L242-L258)：检出预算按 `pointer.path` 筛选（另有 10 万项上限），对象完整性/对象库校验仍针对固定提交。两项按当前路径都超过默认检出值；未测出精确网络传输/对象库压缩量，不把 blob 总量冒称对象库实测大小。
- [source-fetch.ts L560–579](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/sync/source-fetch.ts#L560-L579)：固定 SHA 且支持完整性验证的后端走缓存；缓存关闭/旧后端的 clone 路径不同，不能把缓存预算说成所有 Git 路径的绝对限制。
- [market-source-limits.ts L5–23](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/schemas/src/market-source-limits.ts#L5-L23)：ZIP 默认展开 1 GiB、单文件 256 MiB、5000 条；本地 ZIP 设置不控制这两条 Git 指针。当前市场条目不能自选更高客户端 Git 预算。

若以后要支持这些原始大包，应分别决定有限、范围明确的市场审计预算和客户端 Git 配置/安装体验，不全局无限放宽。本 PR 不改两层阈值，也不伪造准入。

## 许可已知、可引用上游，不等于安装副本已保留通知

MIT/Apache 条件中的通知保留，与目录链接到许可明确的原仓库是两件事。这里不是说市场无权引用原仓库，也不把已知 MIT/Apache 改回 unknown。问题是市场客户端实际复制后的文件集合中没有必要的根通知；目录中的 evidencePath 或审计根路径不等于实际附带文件。

固定客户端完整调用链：

1. [fetchSourceRepoToTemp L576–579](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/sync/source-fetch.ts#L576-L579) 返回 `pointer.path` 所定 contentDir。
2. [createCollectionChildWriter L370–491](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/capability-discovery/market-install.ts#L370-L491) 为合集取 `join(contentDir, child.path)`，混合/非混合安装及 Agent 依赖预置共用这套 prepare/publish 实现。
3. [skill-staging.ts L26–74](https://github.com/desirecore/desirecore/blob/e817d57e819975052c5da610874b7747de18b7c8/packages/agent-service/src/capability-discovery/skill-staging.ts#L26-L74) 只复制传入目录、核对 digest，然后移动暂存目录；没有根 LICENSE/NOTICE/COPYING 补入分支。termsNotice 返回提示和 lock provenance 也不等于许可证文本副本。

固定来源路径复核及相同过滤规则的离线复制结果：

| 条目 | 实际安装子目录 | 根通知 | 结果 |
| --- | --- | --- | --- |
| SAG@b6940ac834b3b1ec651c0b49dc1b0c45d4d74c4a | cli/skills/sag（4 文件） | LICENSE | 暂存无 LICENSE |
| pixelfx@5294518ce7c72e48b6100a744596e0acf57f2826 | skills/pixelfx（仅 SKILL.md） | LICENSE、NOTICE.md | 暂存无两者 |
| Blender@904f095d8f36a6e72adaebb08d07f884a074743d | .claude/skills/*（94 子项） | LICENSE | 94/94 子目录缺根通知 |
| gamedev@c6ca6c41c839b68319ffc08430b99ab768debc32 | skills/disciplines/*、skills/engines/* 等（79 子项，以 entry.children 为准） | LICENSE、NOTICE | 79/79 子目录缺根通知 |
| patent@491524bd36a3f9f8d2e35caa5b56368b67d88ced | skills/*（9 子项） | LICENSE | 9/9 子目录缺根通知 |
| stickman@10287822ba47579321068da1b93801face9160dd | skills/directing-stickman-videos | LICENSE | 也缺根通知，先前只写体积是不完整的 |

逐项物理模拟包括 SAG、pixelfx、Blender animation、gamedev audio-design、patent-disclosure，均只出现所选目录内文件，未带上外部根许可。完整树核对覆盖全部 94/79/9 子项。未运行上游脚本，未声称外部服务验收。

正确修复层是客户端：在路径/合集子项 staging 时，将已验证固定来源中的根 LICENSE/NOTICE/COPYING 正确保留到安装副本，并使完整性摘要/锁记录与实际暂存树一致；不能简单在 digest 校验后偷加文件。或由上游自行提供路径内许可。须另行决定客户端方案；本市场修复不改客户端，也不擅自重打包上游。

## 其他 PR 的方向

- #350 AI News Radar 本地完整包是用户显式要求的派生交付，不一刀切撤回；其外部依赖/运行授权边界保留。
- #356 仅纠正 Follow Builders 中英文长描述与 #350 已审核状态冲突，保留 README 一行 MIT 的固定快照例外，不扩大成所有版本的许可回执；无需另开重复修复。
- #355 只改 manifest 和外贸团队 entry/sidecar，不改共同安装/预算机制，本轮不改他人业务。
