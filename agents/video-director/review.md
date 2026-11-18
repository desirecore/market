# 视频导演条目审核 / Video Director listing review

条目 `video-director`，版本 `0.2.1`，源 UUID `98951c8f-3f46-4215-aea7-db5d06abc942`。本次头像与资料来自[PR19](https://github.com/desirecore-agent/video-director/pull/19)，head CI42631503976 通过，实际合并提交 `5b4ad58b234df525531175711b971e39bff84897` 的单父与 tree 已回读，tree 与已测 preview 相同。市场 pin 更新到该合并来源；旧 pin 后已在上游合并的使用说明一并按来源保留，不冒本次重做媒体功能验收。

The listing pins the actual merged 0.2.1 source. Current-head content CI and the actual merge tree were checked; this is a profile update, not a new video-rendering or runtime qualification. Previously merged upstream usage guidance is included in the new pinned source.

OpenFilm MIT 来源、独立改编及完整许可继续保留，见所 pin 来源的 LICENSE / NOTICE / licenses。运行依赖与可选模型/媒体服务仍需另行安装、授权及承担费用；入口关联不授予工具或文件权限。正式包可用性与已安装实例的更新状态应独立核实。

## 2026-11-09 头像与基础资料 / Portrait and profile

补充原创虚构人物的透明职业肖像、清晰角色定位及中英双语简介。源码 `agent.json` 和市场 `entry.json` 均引用各自目录内的 `assets/avatar.png`，两处文件 SHA256 逐字一致，小于市场 2 MiB 上限，实际解码为 1254×1254 RGBA 且包含真实透明。源码 manual 策略保留字形回落，安装不新增头像生成调用。图片由内置 imagegen 原创生成，不使用特定真人或上游人像。

The source seed and marketplace card each bundle the same original transparent fictional portrait under their own relative asset path. The files have matching SHA256, decode as RGBA and fit the marketplace size limit. The manual policy retains the fallback and does not trigger generation during installation. Bilingual profile text clarifies the role, strengths, collaboration and delivery.

本次内容/打包回归及当前平台 seed Schema、技能 parser 均通过；实际已安装实例的头像显示仍待用户目标实例连接与身份确认，不能用仓库校验替代。视频导演与视频剪辑师保持独立身份；未创建或重组团队。
