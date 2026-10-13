# 作者接口与交付材料

本文是未发行候选协议的知识材料。中文权威接口正文位于主仓 `docs/功能/市场系统/API/应用开发发布接口.md`；该路径与外仓 PR 不声明在线文档、客户端或官方 seed 已更新。每次先读取实际 capability 结果和当前 Schema。

使用当前 HttpRequest 的授权通道。不要读取管理 token；应用网页不能调用这些作者管理接口。

| 操作 | 当前接口 | 返回事实 |
|---|---|---|
| 能力 | `GET /api/apps/capabilities` | 实际 features/policy，不由版本推断 |
| 读取交付草稿 | `POST /api/apps/authoring/drafts/read`，`{fileRef}` | 从真实授权文件读取并核验 AppDraftRef |
| 预览 | `POST /api/apps/authoring/previews` | snapshot/live、实际 revision、隔离 runtime |
| 结束预览 | `POST /api/apps/authoring/previews/:draftId/end`，`{expectedRevision}` | 撤销该预览，Task 保留 |
| 固定材料 | `POST /api/apps/releases/prepare` | owned candidate、真实 payload/descriptor 摘要 |
| 个人发布 | `POST /api/apps/releases/commit` | writer CAS 和 activation 分开 |
| 查询原发布 | `GET /api/apps/installations/:installationId/release-submissions/:submissionId` | committed/absent/unknown |
| 历史/更新准备 | `GET /api/apps/installations/:installationId/history`、`update-readiness` | 材料可恢复性与数据兼容，不假定旧数据备份存在 |
| 白名单导出 | `POST /api/apps/releases/export` | exportRef、archiveDigest、releaseDigest、实际 files/size |
| 下载导出 | export 的 `downloadPath` | 原始 ZIP 响应体，摘要不能以文本解析代替 |
| 目录草稿 | `POST /api/apps/distribution/prepare` | Registry 三文件内容、mapping、未上传/未提交事实 |
| 原开发服务器合同 | `POST /api/apps/runtime/development-contracts`，`{prepareRef,draft,terminalId,endpoint:{port,identityPath}}` | 原授权可变源码 owner 的 development-only 合同，只用于 live 预览 |
| Docker 登记准备 | `POST /api/apps/runtime/docker/enrollments/prepare` | `data.preparation`，私有短期 CID/env 文件、nonce、实际 create 命令，不执行 |
| Docker 登记 | `POST /api/apps/runtime/docker/enrollments/enroll`，`{enrollmentRef,terminalId}` | `data.contract`，真实容器执行合同，不把 CLI 退出称为健康 |
| 真实启动/停止 | `POST /api/apps/runtime/:installationId/start`、`stop`，`{}` | 当前 owner 再审批后的实际运行结果 |

`prepare` 输入沿 AppReleasePrepareRequest：`mutationId`、已授权 `materialRoot: FileResourceRef`、`manifestPath`、可选 expectedReleaseDigest、`target:{appId,installationId,deviceId,sourceId}`。首次个人 sourceId 为服务约定的 `user-managed`，不能用名字冒充目录身份。`commit` 使用原 prepareRef、已解析的 ApplicationInstallationRequest、expectedRevision、submissionId。登记失败先查询同提交，不重新复制/启动软件。

`AppDraftRef` 文件有 `schemaVersion:1`、稳定 draftId/appId、实际授权 `workdir`、绝对 planPath、真实 `source:{agentId,sessionId}`，可选 targetInstallationId/baselineReleaseDigest。文件引用从当前请求或授权读取工具取得，不能复制别的宿主/Agent/root。

release 采用 `schemaVersion:1` / `canonicalization: app-release-c14n-v1`，包括 definition、delivery、files、source、supportedPlatforms、requiredCapabilities。files 的 role 为 definition/ui/runtime/dependency/documentation/license/evidence/data-contract；路径为包内规范 POSIX。definition 文件必须与 manifest.definition 一致。`app-release.json` 本身不放入 files，不能让摘要自引用。

web-bundle.delivery.entrypoints 固定 `{entrypointId,path,spaFallback?}`；native-app保存runtimeInstructionsPath；docker-app同时必填imageRefs，逐项固定显式注册表/repository@sha256，不附登录凭据；实际仍由原容器owner拉取、执行和身份核验。缺容器环境或adapter时明确不可用，不新建容器管理器。平台不解释说明为命令DSL。source 是实际 Git 完整 commit 或工作树内容 sha256；supportedPlatforms 为 darwin/win32/linux/web。最低客户端是 minimumClientVersion，实际能力仍从握手确认。

数据合同声明 formatVersion、readableVersions、writableVersions、有限 files key/path/maxBytes/contentType 和 uninstallRetention: retain。备份/迁移/恢复说明引用必须在 payload 白名单中；说明不授权自动执行，安装历史不代表真实数据备份。

动态 Node 示例的 `/.desirecore-app-identity` 返回当前 TaskHost 注入的 proof/releaseDigest/scopeId/runtimeGeneration；proof 仅用于本次运行身份握手，不当应用 API token，不写日志。`POST /api/apps/runtime/contracts` 使用已 prepare 的材料、installationId、真实 terminalId、endpoint.port/identityPath 与 startupPolicy。服务固定原执行合同后，原 Bash 显式停原命令，正式 commit 后由原 owner 启动新代际再核验。具体环境、执行审批和数据根均由实际 owner 决定。

原执行命令的初始默认端口写成 `PORT="${PORT:-32000}" node runtime/server.mjs`，其中默认端口需实际可用。重启仍执行原真实 argv，Harness 注入的 preview PORT 不能被写死赋值盖掉。若应用后端需要数据，APP_DATA_DIR 也用已授权 seed 根作为初次默认，后续严格使用 owner 注入的独立根；不可将 seed/candidate 数据自动迁入正式实例。

Docker prepare 输入为 `{prepareRef,installationId,endpoint:{port,containerPort,identityPath},startupPolicy}`，可提议清单内 imageRef、容器 commandArgs/entrypoint、materialMountPath/dataMountPath；这些不是执行授权。使用返回的实际 command/cwd 沿原获审批 Bash/TaskHost 执行，拿真实 terminalId 与 enrollmentRef 登记。当前 adapter 只接本地 Linux daemon 上该已核验的固定单容器形态；其他环境/挂载/服务编排保持原 owner 并报告原因，不自动安装 Docker、pull 镜像或修改用户容器。RepoDigest 与 Image ID 分别验证；冷重连核读真实 StartedAt，CID 不存在或结果 unknown 时不补建第二实例。

网页工作查询使用原 `{agentId,clientRequestId}`，SDK 不猜最近的 Agent。controlWork 当前只允许原 snapshot.availableActions 中的 abort。readWork.resources 的 `{locator}` 由实际 Run/Task 成果 owner 返回，`openResource({locator})` 回 navigation-requested 不保证文件正文已打开；不要把调用者任意 FileRef、Task ID 或 URL 变成果授权。

设备视图偏好需 manifest.viewStateContract `{schemaVersion:1,keys,maxBytes,formatVersion?}` 与用户 saveViewState grant。connect.viewStates 为 array；device 项带 revision，deviceViewState 为 available（formatVersion/maxBytes）或 unavailable（reason）。默认 memory；显式 device 请求包含 schemaVersion/key/state/persistence/expectedRevision/mutationId，保持同正文同 ID 重试。设备偏好与业务数据、跨设备同步和数据备份是不同事实，preview 不借用正式 device 项。

Web 最终接纳沿可信聊天传输。实际部署需 owner 提供 TLS/domain/DNS/authority port，可信 shell 取得 web-host ticket 并显式 bootstrapSdk；页面不持平台 token，不伪造 native physical intent，不选择管理上游。未支持的 navigate、未配置的 Web 来源或未授权能力分别说明实际 reason。

长期 Web 呈现通过宿主 SDK 的有限同 session 续期维持。SDK connect 先确认原 parent 的当前呈现，再使用同应用来源的空 POST keepalive；它不执行业务命令、不扩权，不为已换版、已撤销或失效的页面延长会话。不要自行复制 ticket、cookie 或平台凭据来修复过期页。
