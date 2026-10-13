# 作者接口与交付材料

本文是未发行候选协议的知识材料。中文权威接口正文位于主仓 `docs/功能/市场系统/API/应用开发发布接口.md`；该路径与外仓 PR 不声明在线文档、客户端或官方 seed 已更新。每次先读取实际 capability 结果和当前 Schema。

Agent 使用原 `AppManage` 的有限作者动作，直接进入已有 release、preview、runtime 或 Docker owner。原 ToolExecutor 调用源、真实 Run/用户/Agent/宿主、材料读取根、当前策略与审批在效果边界重新核验。参数不自报 owner，也不获得平台管理凭据。以下动作可按目标组合，表格不是固定开发步骤。

| AppManage action | 参数包络 | 返回事实 |
|---|---|---|
| `authoring_capabilities` | 无额外参数 | `capabilities` 的实际 features/policy/hostInstanceId 和当前 Agent 可读的 `fileRoots` |
| `read_draft` | `file_ref: FileResourceRef` | 从真实授权文件读取并核验的 `draft: AppDraftRef` |
| `prepare_release` | `release_request: AppReleasePrepareRequest` | owned candidate、真实 payload/descriptor 摘要、当前 expectedRevision |
| `commit_release` | `release_request: AppReleaseCommitRequest` | 唯一 writer CAS 保存；activation 与保存分别核验 |
| `lookup_release_submission` | `installation_id`、原 `submission_id` | 原提交 committed/absent/unknown，不换 ID 重装 |
| `preview_list` | 无额外参数 | 当前 owner 的实际 previews |
| `preview_read` | `draft_id` | 原草稿的当前预览与 revision |
| `preview_prepare` | `owner_request: AppPreviewRequest` | snapshot/live、实际 revision、隔离 runtime |
| `preview_end` | `owner_request:{draftId,expectedRevision}` | 只结束该原预览，保留 Task 和开发材料 |
| `runtime_read` | `installation_id`、可选 `entrypoint_id` | 精确实例入口的当前运行状态 |
| `runtime_start` | `installation_id` | 原执行 owner 当前再审批后的实际启动结果 |
| `runtime_stop` | `installation_id` | 原执行 owner 当前再审批后的实际停止结果 |
| `runtime_enroll` | `owner_request:{prepareRef,installationId,terminalId,endpoint:{port,identityPath},startupPolicy}` | 原真实已接纳命令的固定 native 执行合同 |
| `development_enroll` | `owner_request:{prepareRef,draft,terminalId,endpoint:{port,identityPath}}` | 原授权可变源码的 development-only 合同，只用于 live 预览 |
| `docker_prepare` | `owner_request: DockerPrepareEnrollmentInput` | 私有短期 CID/env 文件与实际 create 命令，不执行 Docker 命令 |
| `docker_enroll` | `owner_request:{enrollmentRef,terminalId}` | 真实 daemon/CID/RepoDigest/挂载/端口执行合同，不以 CLI 退出代替健康 |
| `release_history` | `installation_id` | 保存材料历史，不假称数据备份 |
| `export_release` | `owner_request: AppReleaseExportRequest` | exportRef、archiveDigest、releaseDigest、实际 files/size 和 downloadPath，不上传 |

例如能力调用为 `AppManage({action:'authoring_capabilities'})`。读草稿使用 `action:'read_draft'` 与返回的授权根对应的 `file_ref`；发布准备/提交分别使用 `release_request`，预览/运行纳管/导出使用 `owner_request`。这些包络不是互换字段，原工具及内部 owner 仍逐个严格核验完整 DTO。

`prepare_release` 的 AppReleasePrepareRequest 包含 `mutationId`、已授权 `materialRoot: FileResourceRef`、`manifestPath`、可选 expectedReleaseDigest、`target:{appId,installationId,deviceId,sourceId}`。FileResourceRef 的 schemaVersion/instanceId/agentId/rootId/path 来自真实 fileRoots 与本次材料；path 是授权根内相对路径，不能复制别的宿主/Agent/root。首次个人 sourceId 为服务约定的 `user-managed`，不能用名字冒充目录身份。

`commit_release` 使用原 prepareRef、expectedRevision（首次为 none，更新取原安装修订）、稳定 submissionId、完整 material（已解析的 ApplicationInstallationRequest）。登记失败先用 lookup_release_submission 查同安装同提交，不重新复制/启动软件。只读动作不触发修改审批；修改动作继续沿原工具审批和最终材料/调用身份复验。调用取消的短授权不保存为长期运行权限，已接纳的后台工作与 owned 临时预览补偿分别按其原 owner 管理。

`AppDraftRef` 文件有 `schemaVersion:1`、稳定 draftId/appId、实际授权 `workdir`、绝对 planPath、真实 `source:{agentId,sessionId}`，可选 targetInstallationId/baselineReleaseDigest。文件引用从当前请求或授权读取工具取得。preview_prepare 用原 draft、mode、expectedRevision，snapshot 还给 release；结束只传原 draftId/revision，不能猜最近草稿或 borrowed 正式作用域。

release 采用 `schemaVersion:1` / `canonicalization: app-release-c14n-v1`，包括 definition、delivery、files、source、supportedPlatforms、requiredCapabilities。files 的 role 为 definition/ui/runtime/dependency/documentation/license/evidence/data-contract；路径为包内规范 POSIX。definition 文件必须与 manifest.definition 一致。`app-release.json` 本身不放入 files，不能让摘要自引用。

web-bundle.delivery.entrypoints 固定 `{entrypointId,path,spaFallback?}`；native-app 保存 runtimeInstructionsPath；docker-app 同时必填 imageRefs，逐项固定显式注册表/repository@sha256，不附登录凭据；实际仍由原容器 owner 拉取、执行和身份核验。缺容器环境或 adapter 时明确不可用。平台不解释说明为命令 DSL。source 是实际 Git 完整 commit 或工作树内容 sha256；supportedPlatforms 为 darwin/win32/linux/web。最低客户端是 minimumClientVersion，实际能力仍从握手确认。

数据合同声明 formatVersion、readableVersions、writableVersions、有限 files key/path/maxBytes/contentType 和 uninstallRetention: retain。备份/迁移/恢复说明引用必须在 payload 白名单中；说明不授权自动执行，安装历史不代表真实数据备份。

动态 Node 示例的 `/.desirecore-app-identity` 返回当前 TaskHost 注入的 proof/releaseDigest/scopeId/runtimeGeneration；proof 仅用于本次运行身份握手，不当应用 API token，不写日志。`AppManage.runtime_enroll` 使用已 prepare 的材料、installationId、真实 terminalId、endpoint.port/identityPath 与 startupPolicy。服务固定原执行合同后，原 Bash 显式停原命令，正式 commit 后由原 owner 启动新代际再核验。具体环境、执行审批和数据根均由实际 owner 决定。

原执行命令的初始默认端口写成 `PORT="${PORT:-32000}" node runtime/server.mjs`，其中默认端口需实际可用。重启仍执行原真实 argv，Harness 注入的 preview PORT 不能被写死赋值盖掉。若应用后端需要数据，APP_DATA_DIR 也用已授权 seed 根作为初次默认，后续严格使用 owner 注入的独立根；不可将 seed/candidate 数据自动迁入正式实例。

Docker prepare 的 owner_request 为 `{prepareRef,installationId,endpoint:{port,containerPort,identityPath},startupPolicy}`，可提议清单内 imageRef、容器 commandArgs/entrypoint、materialMountPath/dataMountPath；这些不是执行授权。使用返回的实际 command/cwd 沿原获审批 Bash/TaskHost 执行，拿真实 terminalId 与 enrollmentRef 用 docker_enroll 登记。当前 adapter 只接本地 Linux daemon 上该已核验的固定单容器形态；其他环境/挂载/服务编排保持原 owner 并报告原因，不自动安装 Docker、pull 镜像或修改用户容器。RepoDigest 与 Image ID 分别验证；冷重连核读真实 StartedAt，CID 不存在或结果 unknown 时不补建第二实例。

## 平台 HTTP 管理消费者

HTTP 接口保留给平台 UI 或具有合法管理凭据的消费者，普通 HttpRequest 不自动注入实例凭据。Agent 缺少对应原工具能力时说明不可用，不读取实例 token、不改 Origin 绕过 401，也不把凭据交网页。HTTP 返回包络与原 AppManage 结果各按实际合同读取。

| 平台接口 | 用途 |
|---|---|
| `GET /api/apps/capabilities`、`POST /api/apps/authoring/drafts/read` | 平台能力与草稿读取 |
| `POST /api/apps/releases/prepare`、`commit` | 固定材料与个人发布 |
| `POST /api/apps/authoring/previews`、`:draftId/end` | 平台预览和结束 |
| `POST /api/apps/runtime/contracts`、`development-contracts` | 平台 native/源码纳管 |
| `POST /api/apps/runtime/docker/enrollments/prepare`、`enroll` | 平台 Docker 纳管 |
| `POST /api/apps/runtime/:installationId/start`、`stop` | 平台正式启动/停止 |
| `POST /api/apps/releases/export`、export 返回的 `downloadPath` | 生成归档和下载原始 ZIP 字节 |
| `POST /api/apps/distribution/prepare` | 读取真实 exportRef 生成 Registry 三文件，未上传/未提交 |

当前 export_release 结果中的 downloadPath 仍是平台管理下载路径，不是网页或普通 HTTP 工具的授权。分发需确认真实 ZIP 字节已通过授权的材料/上传通道交付，以及目录生成通道可用。缺少时保留导出事实，不能宣称已上传或目录已提交。

## 网页协作合同

网页工作查询使用原 `{agentId,clientRequestId}`，SDK 不猜最近的 Agent。controlWork 当前只允许原 snapshot.availableActions 中的 abort。readWork.resources 的 `{locator}` 由实际 Run/Task 成果 owner 返回，`openResource({locator})` 回 navigation-requested 不保证文件正文已打开；不要把调用者任意 FileRef、Task ID 或 URL 变成果授权。

设备视图偏好需 manifest.viewStateContract `{schemaVersion:1,keys,maxBytes,formatVersion?}` 与用户 saveViewState grant。connect.viewStates 为 array；device 项带 revision，deviceViewState 为 available（formatVersion/maxBytes）或 unavailable（reason）。默认 memory；显式 device 请求包含 schemaVersion/key/state/persistence/expectedRevision/mutationId，保持同正文同 ID 重试。设备偏好与业务数据、跨设备同步和数据备份是不同事实，preview 不借用正式 device 项。

Web 最终接纳沿可信聊天传输。实际部署需 owner 提供 TLS/domain/DNS/authority port，可信 shell 取得 web-host ticket 并显式 bootstrapSdk；页面不持平台 token，不伪造 native physical intent，不选择管理上游。未支持的 navigate、未配置的 Web 来源或未授权能力分别说明实际 reason。

长期 Web 呈现通过宿主 SDK 的有限同 session 续期维持。SDK connect 先确认原 parent 的当前呈现，再使用同应用来源的空 POST keepalive；它不执行业务命令、不扩权，不为已换版、已撤销或失效的页面延长会话。不要自行复制 ticket、cookie 或平台凭据来修复过期页。
