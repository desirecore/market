# 视频剪辑师条目审核 / Video Editor listing review

## 固定来源与许可 / Pinned source and licensing

- 条目 ID / Listing ID: `video-editor`；源 Agent UUID / source Agent UUID: `c5a424f2-d946-47fd-a12e-2602d0da37ed`。市场 slug 与安装后的本地 Agent ID 是不同身份，不改写源 UUID。
- 版本 / Version: `0.1.0`，取自 [固定源码 agent.json](https://github.com/desirecore-agent/video-editor/blob/a9e87d8f7807853e5076f98298afbb191ab778b3/agent.json)。
- 固定提交 / Pinned commit: `a9e87d8f7807853e5076f98298afbb191ab778b3`。本目录只保留 Git 指针；不分发 AgentFS、用户数据、运行回执或媒体文件。
- [MIT](https://github.com/desirecore-agent/video-editor/blob/a9e87d8f7807853e5076f98298afbb191ab778b3/LICENSE)、[NOTICE](https://github.com/desirecore-agent/video-editor/blob/a9e87d8f7807853e5076f98298afbb191ab778b3/NOTICE) 与 [FableCut MIT](https://github.com/desirecore-agent/video-editor/blob/a9e87d8f7807853e5076f98298afbb191ab778b3/licenses/FableCut-MIT.txt) 保留作者与改编说明。新名称表示 DesireCore 独立整合，不声称上游认可。
- 2026-11-01 已从 GitHub 固定 ref 核对配置、LICENSE 与 NOTICE。版本已在源码声明；正式发布日未知，元数据保持 `releasePublishedAt: unknown`。

The listing slug and source Agent UUID are distinct from the local ID returned by installation. The catalog distributes only a pinned Git pointer, preserves MIT notices and does not claim upstream endorsement. Configuration, LICENSE and NOTICE were checked at the fixed GitHub ref on 2026-11-01. The source declares the version; a formal publication date is unknown.

## 安装与关联 / Installation and association

先按独立[视频剪辑应用](https://github.com/desirecore-agent/video-editing)的正式安装约定安装应用并准备其固定运行依赖，再按 [Agent 使用说明](https://github.com/desirecore-agent/video-editor/blob/a9e87d8f7807853e5076f98298afbb191ab778b3/USAGE.md)从市场安装此指针。Node.js >=22、浏览器、FFmpeg、模型额度及可选媒体服务均不由 Agent 包提供；相应许可、部署条件与使用费用另行核对。

客户端版本下限为 `10.0.195`，对应本次受测平台源码版本；还必须实际检查 `app-authoring-v1` 的 release/runtime-binding 能力。版本号不替代能力、应用安装、运行身份或授权证据。关联只设置入口偏好，`contextPermissions` 保持空数组；MCP 经独立管理与授权连接同一个当前代际实例，不启动第二个上游服务。无依赖、能力或授权时明确停止和报告，不伪造完成。

Install the separate Video Editing app through its managed installation flow and explicitly prepare its pinned dependencies before installing this Agent through the market. Follow the pinned upstream usage guide. Node.js >=22, browser/FFmpeg assets, model usage and optional media services are separate dependencies with their own terms and costs. Client `10.0.195` is the floor for the tested platform source; independently check release/runtime-binding capabilities, current runtime identity and authorization. Association conveys no permission. MCP attaches to that same current instance, and the Agent does not start a second service. Missing prerequisites stop the external operation with an explicit report.

## 当前验收与发布门禁 / Acceptance and publication gates

- Windows 与 Ubuntu/WSLg 源码 GUI 已完成限定的实际导入、关联、MCP 编辑、导出、明暗与窄布局、取消及同任务中断恢复。Linux 结果不代表正式 Linux 包或裸机 GPU；Windows 结果不代表正式签名安装器。
- macOS 验收仍待完成，因此当前平台列表只列 Windows/Linux。受控工具协议验证执行与回执，不证明模型自主规划质量。
- 故障前临时分片的非零字节数未直接采样，专门的后代进程停止分支未单独执行；不扩大对应结论。
- 本条目 PR 保持 Draft，依赖[应用 PR1](https://github.com/desirecore-agent/video-editing/pull/1)、[Agent PR1](https://github.com/desirecore-agent/video-editor/pull/1)及必要 macOS 验收，不自动合并。目录 Schema/CI 通过不等于已经从市场安装成功；合并后仍需验证客户端同步、获取、关联和打开。

Windows and an Ubuntu/WSLg source GUI passed bounded real import, association, MCP editing, export, appearance/layout, cancellation and same-job interruption recovery. That does not qualify an official Linux package, bare-metal GPU, a signed Windows installer or autonomous model reasoning. Pre-fault nonzero part bytes and dedicated descendant-stop branches were not separately observed. macOS remains pending, so the platform list currently includes Windows/Linux only. Keep this listing PR Draft until both source PRs and required macOS acceptance complete. Catalog CI does not prove installation from the published market; client synchronization, acquisition, association and opening still require verification after publication.
