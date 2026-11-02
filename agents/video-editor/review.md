# 视频剪辑师条目审核 / Video Editor listing review

## 固定来源与许可 / Pinned source and licensing

条目 `video-editor`，Agent 版本 `0.1.0`，源 UUID `c5a424f2-d946-47fd-a12e-2602d0da37ed`。固定已合提交 `c6ffbc603348428a89978bd60db1fd9b448115b1` 来自[Agent PR1](https://github.com/desirecore-agent/video-editor/pull/1)，main CI41447980032通过；与已验19个seed文件/81191B相同。实际安装返回的本地Agent ID另取正常响应，不改写源UUID。目录仅保留Git指针，不带AgentFS数据、媒体、凭据、Provider、MCP grant、目录信任或预审批。

[MIT](https://github.com/desirecore-agent/video-editor/blob/c6ffbc603348428a89978bd60db1fd9b448115b1/LICENSE)、[NOTICE](https://github.com/desirecore-agent/video-editor/blob/c6ffbc603348428a89978bd60db1fd9b448115b1/NOTICE)及[FableCut MIT](https://github.com/desirecore-agent/video-editor/blob/c6ffbc603348428a89978bd60db1fd9b448115b1/licenses/FableCut-MIT.txt)保留作者与独立改编说明。2026-11-02核对源配置/许可与当前平台Schema；不冒上游认可。Agent声明版本的正式publication日期没有独立事实，releasePublishedAt保持unknown。

The listing pins the actual merged Agent source and retains licensing and source identity. The local installed Agent ID is separate. This is a Git pointer without runtime data, credentials or preauthorized permissions; a declared version is not an independently observed publication date.

## 安装、依赖与关联 / Installation, prerequisites and association

单独安装[视频剪辑](https://github.com/desirecore-agent/video-editing)应用0.1.3（产品UUID `0171a763-ad35-4b94-98b9-204782817b44`）并显式准备其固定Node >=22、浏览器、FFmpeg/ffprobe依赖，再从默认官方Agent市场安装本条目，遵循[固定使用说明](https://github.com/desirecore-agent/video-editor/blob/c6ffbc603348428a89978bd60db1fd9b448115b1/USAGE.md)。应用源仓库/skill名是video-editing，UUID才是应用目录身份。两个产品独立版本，不替换既有视频创作/视频导演。模型额度、可选媒体服务许可/账号/费用另计。

最低客户端预定10.0.197，必须实际包含[平台PR5598](https://github.com/desirecore/desirecore/pull/5598)的官方UUID目录与manifest内联appRelease读取能力；还需真实release/runtime-binding能力、安装与当前代际观测。197仍在发行准备阶段，公开196标签源不含此reader，不能仅看同版本号或capability字符串推断兼容。关联仅设置入口偏好，contextPermissions为空；经独立MCP管理/授权连接当前同实例，不自启第二个服务。缺失前置条件时停止外部操作并明确报告。

Prepare the separate Video Editing app 0.1.3 and its pinned runtime dependencies, then install this independent Agent using the official market and pinned usage guide. Client 10.0.197 is the planned floor and is not publicly released yet; it must actually include the new catalog reader and runtime capabilities. The public 196 source lacks the reader. Association grants no permissions. Independently authorize MCP for the same current instance. Model and optional media-service fees and terms are separate.

## 实际资格与发布边界 / Qualification and publication boundaries

应用0.1.3/R14的macOS源码GUI、Windows x64未签GUI、Ubuntu24.04.5/WSLg普通用户源码GUI均完成限定功能验收：真实受管准备与登记、Agent工具与同实例MCP、编辑/自产影片及全解码/画面声音校准、实际UI明暗。Windows和Linux当前取消与原任务Root故障恢复分别有原件；Mac该不变域承接已验R12，不冒新R14全矩阵。Windows当前UI补验不冒新AgentRun。Linux原观察工装退出竞态保留，以同一case只读续核；不是重跑故障后覆盖失败。自有现场和锁均已闭合。

资格不扩展为正式签名客户端/官方Linux包、裸机GPU、所有系统版本或商业模型自主规划质量。旧Windows窗口归档超过hard13.245秒等原边界保留，不因新窗口关闭通过抹除。目录校验不等于从正式市场安装成功；App固定资产、两个目录main和新兼容客户端公开发行与fresh-home默认市场安装/关联/使用仍须实际验证，当前该闭环未完成。发布门禁满足前保持Draft。

Bounded app 0.1.3 qualification covers the three stated native GUI environments, actual managed tools/MCP, media output validation and appearance. Current Windows/Linux recovery and the unchanged prior macOS recovery domain remain distinct. Original timing and observer failures are retained. This does not qualify production installers, bare-metal GPU or autonomous model quality. Catalog validation is separate from public-client distribution and fresh installation, association and use from the published default markets; that final flow is still pending.
