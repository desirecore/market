# 视频剪辑师条目审核 / Video Editor listing review

## 固定来源与许可 / Pinned source and licensing

条目 `video-editor`，Agent 版本 `0.1.1`，源 UUID `c5a424f2-d946-47fd-a12e-2602d0da37ed`。固定已合提交 `67b5c7d8e0232102b8abd13d6ff2d4aa11e4afa7` 来自[头像与资料 PR2](https://github.com/desirecore-agent/video-editor/pull/2)，本次 head CI42631514221 通过，实际 merge tree 与已测 preview 相同；21 个 seed 文件包含头像及来源说明。历史 0.1.0 的原生资格继续保留其对应来源边界。实际安装返回的本地Agent ID另取正常响应，不改写源UUID。目录包含自有头像展示资产与 Git 指针，不带用户 AgentFS 数据、影片素材、凭据、Provider、MCP grant、目录信任或预审批。

[MIT](https://github.com/desirecore-agent/video-editor/blob/67b5c7d8e0232102b8abd13d6ff2d4aa11e4afa7/LICENSE)、[NOTICE](https://github.com/desirecore-agent/video-editor/blob/67b5c7d8e0232102b8abd13d6ff2d4aa11e4afa7/NOTICE)及[FableCut MIT](https://github.com/desirecore-agent/video-editor/blob/67b5c7d8e0232102b8abd13d6ff2d4aa11e4afa7/licenses/FableCut-MIT.txt)保留作者与独立改编说明。2026-11-09核对本次头像、配置、许可及当前平台 Schema；不冒上游认可。Agent声明版本的正式publication日期没有独立事实，releasePublishedAt保持unknown。

The listing pins the actual merged Agent source and retains licensing and source identity. The local installed Agent ID is separate. This is a Git pointer without runtime data, credentials or preauthorized permissions; a declared version is not an independently observed publication date.

## 安装、依赖与关联 / Installation, prerequisites and association

单独安装[视频剪辑](https://github.com/desirecore-agent/video-editing)应用0.1.3（产品UUID `0171a763-ad35-4b94-98b9-204782817b44`）并显式准备其固定Node >=22、浏览器、FFmpeg/ffprobe依赖，再从默认官方Agent市场安装本条目，遵循[固定使用说明](https://github.com/desirecore-agent/video-editor/blob/67b5c7d8e0232102b8abd13d6ff2d4aa11e4afa7/USAGE.md)。应用源仓库/skill名是video-editing，UUID才是应用目录身份。两个产品独立版本，不替换既有视频创作/视频导演。模型额度、可选媒体服务许可/账号/费用另计。

最低客户端预定10.0.197，必须实际包含[平台PR5598](https://github.com/desirecore/desirecore/pull/5598)的官方UUID目录与manifest内联appRelease读取能力；还需真实release/runtime-binding能力、安装与当前代际观测。公开196标签源不含此reader，安装时核对实际发行源码与能力，不能仅看版本号或capability字符串推断兼容。关联仅设置入口偏好，contextPermissions为空；经独立MCP管理/授权连接当前同实例，不自启第二个服务。缺失前置条件时停止外部操作并明确报告。

Prepare the separate Video Editing app 0.1.3 and its pinned runtime dependencies, then install this independent Agent using the official market and pinned usage guide. Client >=10.0.197 must actually include the new catalog reader and runtime capabilities. The public 196 source lacks the reader. Association grants no permissions. Independently authorize MCP for the same current instance. Model and optional media-service fees and terms are separate.

## 实际资格与发布边界 / Qualification and publication boundaries

应用0.1.3/R14的macOS源码GUI、Windows x64未签GUI、Ubuntu24.04.5/WSLg普通用户源码GUI均完成限定功能验收：真实受管准备与登记、Agent工具与同实例MCP、编辑/自产影片及全解码/画面声音校准、实际UI明暗。Windows和Linux当前取消与原任务Root故障恢复分别有原件；Mac该不变域承接已验R12，不冒新R14全矩阵。Windows当前UI补验不冒新AgentRun。Linux原观察工装退出竞态保留，以同一case只读续核；不是重跑故障后覆盖失败。自有现场和锁均已闭合。

资格不扩展为正式签名客户端/官方Linux包、裸机GPU、所有系统版本或商业模型自主规划质量。旧Windows窗口归档超过hard13.245秒等原边界保留，不因新窗口关闭通过抹除。目录校验不等于安装成功。App固定资产和两个目录已经发布；客户端197源码候选11285bc284bb0533f24851f9dc6d2f9b60324361的全新隔离home已实际从默认官方目录安装两者、核原fork与正式安装归属、关联空权限、独立同实例MCP24及真实Agent编辑/新影片与完整解码/画面声音校验、原生播放/明暗。停止审批未知结果及原恢复守卫保留，按已有接纳流程修复同一部署后，完整宿主停止审批获得HTTP200和可信TaskHost exit0，数据不变。该限定源码结果不能代替公开签名客户端的全新安装实测；没有模型自主质量结论。

Bounded app 0.1.3 qualification covers the three stated native GUI environments, actual managed tools/MCP, media output validation and appearance. Current Windows/Linux recovery and the unchanged prior macOS recovery domain remain distinct. Original timing and observer failures are retained. This does not qualify production installers, bare-metal GPU or autonomous model quality. Fresh installation of both products, association, same-instance MCP, real Agent edits/output and native appearance/playback passed using the default official catalogs on the stated 197 source candidate. Explicit stop approval and trusted TaskHost termination completed after normal admission repaired the same deployment, with media unchanged. Public signed-client distribution and fresh production-package installation remain separate checks.

## 2026-11-09 头像与基础资料 / Portrait and profile

补充原创虚构人物的透明职业肖像、清晰角色定位及中英双语简介。源码 `agent.json` 和市场 `entry.json` 均引用各自目录内的 `assets/avatar.png`，两处文件 SHA256 逐字一致，小于市场 2 MiB 上限，实际解码为 1254×1254 RGBA 且包含真实透明。源码 manual 策略保留字形回落，安装不新增头像生成调用。图片由内置 imagegen 原创生成，不使用特定真人或上游人像。

The source seed and marketplace card each bundle the same original transparent fictional portrait under their own relative asset path. The files have matching SHA256, decode as RGBA and fit the marketplace size limit. The manual policy retains the fallback and does not trigger generation during installation. Bilingual profile text clarifies the role, strengths, collaboration and delivery.

本次内容/打包回归及当前平台 seed Schema、技能 parser 均通过；实际已安装实例的头像显示仍待用户目标实例连接与身份确认，不能用仓库校验替代。视频导演与视频剪辑师保持独立身份；未创建或重组团队。
