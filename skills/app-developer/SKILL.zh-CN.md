# 应用开发与发布

## L0：职责

Agent 选择技术栈、构建方法与工作方式；平台核验材料、作用域、发布、运行和协作事实。复用文件、执行、Task/Run 与现有安装 writer，不生成固定业务 DAG，不从安装说明自动执行命令。

## L1：先读能力与当前上下文

1. 读取或创建本任务唯一文件化 Plan，保存实际来源 Agent/会话、目标设备、工作目录及开发 Task。已有用户需求和授权直接沿用。
2. 使用原 `AppManage` 的 `authoring_capabilities` 动作。返回的 `capabilities` 必须为 `protocol: app-authoring-v1`，分别看 features 的 supported、authorized、available 和 reason；`fileRoots` 是当前 Agent 可读的真实文件根，`registryTargetIds` 是已登记的目录目标；这些只读事实不授予目录上传或文件写权限。10.0.180 只是代码基线，已发行的同版本客户端不因此支持新协议。作者动作直接进入原领域 owner，不把平台凭据交给模型。
3. 普通自然语言开发不要求新的交接协议。若要登记、安装、更新或卸载，读取 `app-install-manager`；继续沿 ApplicationManagement-v2 解析和唯一 writer，不直接编辑 installed-entries.json。
4. 按需读 [作者接口](references/authoring-api.zh-CN.md) 和 [分发指南](references/distribution.zh-CN.md)。候选主仓正文为 `docs/功能/市场系统/API/应用开发发布接口.md`，按实际能力读取；外仓 PR 不表示客户端或官方 seed 已发行。两份示例位于 `examples/static-workbench/` 与 `examples/service-workbench/`，只是可修改的教学材料，不能代替真实 Agent 开发和业务验收。

## L2：开发、预览和个人发布

- 先确认要解决的工作、数据位置与必要协作。可以使用任何适合的语言/框架，示例不固定技术栈。小任务直接完成；复杂工作保留原 Task、Plan 和用户来源，不另造开发状态机。
- 程序材料、业务数据与秘密分开。作者定义 `application.json` 不包含 sourceId、安装实例、宿主路径、builtin 路由或权限凭据。release 的产品 ID/名称/版本/入口只有这份定义。
- 固定 `app-release.json`：按显式文件白名单、原始字节摘要、入口映射、数据合同和真实平台证据生成；清单自身不进入 files。可用 `scripts/create-release.mjs` 为示例生成清单，平台仍重新核验实际字节。
- 向平台交付 `app-draft.json`，记录真实 fileRef、Plan、Agent/session、稳定 draftId 与目标 installationId。workdir 指向实际完成的 release 材料目录，不猜测 release/ 子目录，也不编造 fileRef。用 `AppManage.read_draft` 的 `file_ref` 读取授权根内实际文件，保留返回的 draft。返回此文件的可点击绝对路径，说明可在应用开发工作区读取并继续。
- 预览沿 `AppManage.preview_prepare` 的 `owner_request` 传原 draft/mode/expectedRevision，snapshot 另给 release；读取用 preview_read，结束用 preview_end。snapshot 预览与正式安装隔离，数据不自动转移。live 预览必须先固定 snapshot 才可发布；刷新/替换用实际 revision。结束预览撤销当前桥并回收本次 owned 临时运行资源，保留数据与开发材料；普通关页不停止正式应用或已接纳的后台 Task，不将预览临时 URL/token 保存为正式入口。
- 原开发服务器/HMR 使用真实授权的 draft 工作目录，由 `AppManage.development_enroll` 的 `owner_request` 传原 prepareRef/draft/terminalId/endpoint 接入。它只用于 live 预览，不能成为正式 startup；可变源码与固定 release 分开。原命令须尊重 owner 注入的 PORT 和 APP_DATA_DIR，初次开发默认值用 shell 的 `${VAR:-default}`，不能写死赋值盖掉预览端口或正式数据根。
- 个人发布由 `AppManage.prepare_release` 的 `release_request` 固定真实材料：materialRoot 使用能力返回的授权根构造 FileResourceRef。检查候选后，`commit_release` 的 `release_request` 使用完整原 AppReleaseCommitRequest，保留精确 prepareRef、installationId、expectedRevision 与原 submissionId；不能把安装 material 对象简化为产品名称或摘要。旧会话里明确授权的发布可继续，不逐命令重复确认。新目标或超出授权的数据/外部副作用沿现有治理处理。
- 发布保存与运行可用分开。静态包通过固定映射承载；带服务应用用 `AppManage.runtime_enroll` 固定原执行 owner 的真实 spawn、代际身份和握手；正式运行用 runtime_read/start/stop，不能把 startupPolicy 当长期执行授权。Docker release 声明完整 imageRefs（注册表/repository@sha256），先用 `AppManage.docker_prepare` 获得私有短期 CID/env 文件及实际命令，沿原审批执行后以 docker_enroll 的原 enrollmentRef/terminalId 核验真实 daemon/CID/RepoDigest/挂载/端口。普通用户启动/停止沿当前审批，私有临时预览回收只补偿原批准的 owned CID；候选、正式和预览的数据根与 nonce 分开。unknown 先检查原 CID，不重复创建；缺 adapter 或支持的环境时保留原 Agent 管理并明确原因。端口响应、Docker CLI 退出、PID、历史 observation 或格式检查不能替代运行绑定；失败如实说明“版本已保存，启动待修复”。
- 写入超时、响应丢失或断线，保留原 mutation/submission/clientRequest ID 与正文；发布用 `AppManage.lookup_release_submission` 的原 installation_id/submission_id 查询，运行和预览分别重读实际状态。unknown 时不创建新 ID 盲重放。修改候选前重读当前版本与数据兼容，迁移中断先观察；代码回退不代表业务数据恢复。

## L3：网页与 Agent 协作

应用网页只使用有限 `window.desirecoreApp.call(method,payload)`/`onEvent`，Web 由独立来源的 MessagePort SDK 连接。没有 Conveyor、任意 invoke、平台管理 token、任意文件代理或通用 fetch 工具。缺宿主/授权时禁用相应操作并给出真实原因。

- `connect.application` 仅为正式实例提供来源/应用/实例前缀；对象 namespace/objectId/revision 由业务 owner 提供并再次校验。预览不借用正式实例，缺对象引用可以只讨论摘要。
- 持久数据只用已声明 key 的 readData/saveData；新文件 expectedAbsent，已有文件 expectedETag，unknown 沿原 mutationId 查询。原生后端使用单独获授权数据根，不能把数据库写入固定 release 目录。
- 选中对象可 publishSelection。发起工作先 prepareWork，最终接纳由平台自己的控件处理：桌面沿真实输入证明与单次 intent，Web 沿原可信聊天接纳传输，不让网页自签原生输入证明。prepare/proposalRef 不等于 Task 已创建；只在 work-accepted 的实际 reserved/committed 回执后显示接纳，queued 不说执行完成。
- 请求恢复沿原 `{agentId,clientRequestId}`；订阅出现 reset_required 时读快照并从合法 cursor 重订阅。controlWork 只用实际 availableActions，当前为 abort，不提供任意 resume。readWork.resources 中的真实 task-binding locator 可以 `openResource({locator})` 定位；navigation-requested 只表示发出定位请求，原文件 owner 继续核验与加载。data-files 对象沿精确业务引用在只读检查器中呈现；不构造自由 FileRef/URL，navigate 未获真实 grant 不使用。
- 业务正文仍由数据 owner 保存。视图恢复默认内存；用户明确选择设备记忆时，先声明 viewStateContract 的有限 key/预算/格式，再取得 saveViewState grant。connect 返回真实 device 状态和各 key revision，device 保存沿原 mutationId、expectedRevision 和正文 CAS；超时保留同一请求，不能换 ID 盲覆盖。只保存必要的筛选/选择/位置，不把笔记正文或凭据作为视图偏好。
- Web 承载需要部署 owner 已配置实际 TLS、域名、DNS 和公开端口，由可信 shell 取得本次 ticket 并明确 bootstrapSdk 注入。SDK/宿主缺失时说明不可用；不关闭 TLS 验证、不让应用选择上游 URL/管理端口，不把 HTTP200 或本机 loopback 当远端浏览器可达。

## L4：分发与交付证据

个人发布默认私有本机，不隐含上传。用户要求分发后，用 `AppManage.export_release` 的 `owner_request` 导出固定版本的完整白名单，审阅确切文件与目标。业务库、.env、凭据、聊天/Task/Plan、日志、机器路径和安装身份不得进入包；环境模板可以包含名称和说明，不能包含真实值。

需要交给上传工具的 ZIP 时，export_release 另在顶层提供 `export_file_ref`（原工具真实写权限目录中的目标 FileResourceRef），并二选一给 `expected_absent:true` 或原 `expected_etag`。返回的 `archiveFile` 包含实际 fileRef/sha256/size/etag/replayed；核验 sha256 等于 archiveDigest，再交已授权的 GitHub/Gitea 上传工具并核读不可变提交/制品 SHA。响应丢失保留同一目标、条件与完整正文查询/重试，不覆盖未知文件；只有只读 fileRoots 不代表有写权限。随后用 `AppManage.distribution_prepare` 的 `owner_request`，以同一 exportRef、能力返回的 registryTargetIds 中的目标、实际固定来源和 metadata 生成 Registry `manifest.json`、`catalog-metadata.v1.json`、`install.md`。草稿仍未上传、未提交目录；缺少真实目标或上传通道时分别说明不可用。普通 HttpRequest 不自动注入平台凭据，不能读取实例 token 或变更 Origin 绕过 401。目录身份由目标 Provider 注入，个人安装仍是原实例。archiveDigest、releaseDigest、物化 descriptorDigest 分别核验；同版本异内容创建新修订，不覆盖旧固定材料。

按真实情况分别报告：代码/业务验证、预览、个人发布、启动、来源上传、目录 PR/准入、第二用户安装。候选 4.3 Schema、外仓 PR 或 ZIP 生成都不代表官方市场已开放，也不能代替客户端能力发行或另一设备运行。外部托管/数据库/Git服务的登录、许可、部署及费用由其真实连接和条款决定，缺少时停止相应外部调用。
