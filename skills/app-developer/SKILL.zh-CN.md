# 应用开发与发布

## L0：职责

Agent 选择技术栈、构建方法与工作方式；平台核验材料、作用域、发布、运行和协作事实。复用文件、执行、Task/Run 与现有安装 writer，不生成固定业务 DAG，不从安装说明自动执行命令。

## L1：先读能力与当前上下文

1. 读取或创建本任务唯一文件化 Plan，保存实际来源 Agent/会话、目标设备、工作目录及开发 Task。已有用户需求和授权直接沿用。
2. 使用当前授权的 HttpRequest 读取 `GET /api/apps/capabilities`。必须得到 `protocol: app-authoring-v1`，分别看 features 的 supported、authorized、available 和 reason。10.0.180 只是代码基线，已发行的同版本客户端不因此支持新协议。
3. 普通自然语言开发不要求新的交接协议。若要登记、安装、更新或卸载，读取 `app-install-manager`；继续沿 ApplicationManagement-v2 解析和唯一 writer，不直接编辑 installed-entries.json。
4. 按需读 [作者接口](references/authoring-api.zh-CN.md) 和 [分发指南](references/distribution.zh-CN.md)。两份示例位于 `examples/static-workbench/` 与 `examples/service-workbench/`，只是可修改的教学材料，不能代替真实 Agent 开发和业务验收。

## L2：开发、预览和个人发布

- 先确认要解决的工作、数据位置与必要协作。可以使用任何适合的语言/框架，示例不固定技术栈。小任务直接完成；复杂工作保留原 Task、Plan 和用户来源，不另造开发状态机。
- 程序材料、业务数据与秘密分开。作者定义 `application.json` 不包含 sourceId、安装实例、宿主路径、builtin 路由或权限凭据。release 的产品 ID/名称/版本/入口只有这份定义。
- 固定 `app-release.json`：按显式文件白名单、原始字节摘要、入口映射、数据合同和真实平台证据生成；清单自身不进入 files。可用 `scripts/create-release.mjs` 为示例生成清单，平台仍重新核验实际字节。
- 向平台交付 `app-draft.json`，记录真实 fileRef、Plan、Agent/session、稳定 draftId 与目标 installationId。workdir 指向实际完成的 release 材料目录，不猜测 release/ 子目录，也不编造 fileRef。返回此文件的可点击绝对路径，说明可在应用开发工作区读取并继续。
- snapshot 预览与正式安装隔离，数据不自动转移。live 预览必须先固定 snapshot 才可发布；刷新/替换用实际 revision。关闭预览撤销当前桥，不取消后台 Task，不将预览临时 URL/token 保存为正式入口。
- 个人发布沿 prepare → 用户检查候选 → commit；提交精确 releaseDigest、installationId、expectedRevision 与原提交 ID。旧会话里明确授权的发布可继续，不逐命令重复确认。新目标或超出授权的数据/外部副作用沿现有治理处理。
- 发布保存与运行可用分开。静态包通过固定映射承载；带服务应用由原执行 owner 的真实 spawn、代际身份和握手接入。Docker release另声明完整imageRefs（注册表/repository@sha256），通过原容器/执行/服务owner核验镜像、环境和身份；缺adapter时保留Agent管理，不把格式检查当真实容器验收。端口响应、PID、历史 observation 不能替代运行绑定；失败如实说明“版本已保存，启动待修复”。
- 写入超时、响应丢失或断线，保留原 mutation/submission/clientRequest ID 与正文，查询原结果；unknown 时不创建新 ID 盲重放。修改候选前重读当前版本与数据兼容，迁移中断先观察；代码回退不代表业务数据恢复。

## L3：网页与 Agent 协作

应用网页只使用有限 `window.desirecoreApp.call(method,payload)`/`onEvent`，Web 由独立来源的 MessagePort SDK 连接。没有 Conveyor、任意 invoke、平台管理 token、任意文件代理或通用 fetch 工具。缺宿主/授权时禁用相应操作并给出真实原因。

- `connect.application` 仅为正式实例提供来源/应用/实例前缀；对象 namespace/objectId/revision 由业务 owner 提供并再次校验。预览不借用正式实例，缺对象引用可以只讨论摘要。
- 持久数据只用已声明 key 的 readData/saveData；新文件 expectedAbsent，已有文件 expectedETag，unknown 沿原 mutationId 查询。原生后端使用单独获授权数据根，不能把数据库写入固定 release 目录。
- 选中对象可 publishSelection。发起工作先 prepareWork，最终接纳由平台自己的控件签发真实 intent。prepare/proposalRef 不等于 Task 已创建；只在 work-accepted 的实际 reserved/committed 回执后显示接纳，queued 不说执行完成。
- 请求恢复沿原 clientRequestId；订阅出现 reset_required 时读快照并从合法 cursor 重订阅。取消 Task/Run 只作用于原归属，不用页面关闭或任意 resume 掩盖失败。成果读取/打开仍须核验精确资源引用。

## L4：分发与交付证据

个人发布默认私有本机，不隐含上传。用户要求分发后，导出固定版本的完整白名单，审阅确切文件与目标。业务库、.env、凭据、聊天/Task/Plan、日志、机器路径和安装身份不得进入包；环境模板可以包含名称和说明，不能包含真实值。

先用已授权 GitHub/Gitea 工具上传并核读不可变提交/制品 SHA，再从同一 exportRef 生成 Registry `manifest.json`、`catalog-metadata.v1.json`、`install.md`。目录身份由目标 Provider 注入，个人安装仍是原实例。archiveDigest、releaseDigest、物化 descriptorDigest 分别核验；同版本异内容创建新修订，不覆盖旧固定材料。

按真实情况分别报告：代码/业务验证、预览、个人发布、启动、来源上传、目录 PR/准入、第二用户安装。候选 4.3 Schema、外仓 PR 或 ZIP 生成都不代表官方市场已开放，也不能代替客户端能力发行或另一设备运行。外部托管/数据库/Git服务的登录、许可、部署及费用由其真实连接和条款决定，缺少时停止相应外部调用。
