# 作者接口与交付材料

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

`prepare` 输入沿 AppReleasePrepareRequest：`mutationId`、已授权 `materialRoot: FileResourceRef`、`manifestPath`、可选 expectedReleaseDigest、`target:{appId,installationId,deviceId,sourceId}`。首次个人 sourceId 为服务约定的 `user-managed`，不能用名字冒充目录身份。`commit` 使用原 prepareRef、已解析的 ApplicationInstallationRequest、expectedRevision、submissionId。登记失败先查询同提交，不重新复制/启动软件。

`AppDraftRef` 文件有 `schemaVersion:1`、稳定 draftId/appId、实际授权 `workdir`、绝对 planPath、真实 `source:{agentId,sessionId}`，可选 targetInstallationId/baselineReleaseDigest。文件引用从当前请求或授权读取工具取得，不能复制别的宿主/Agent/root。

release 采用 `schemaVersion:1` / `canonicalization: app-release-c14n-v1`，包括 definition、delivery、files、source、supportedPlatforms、requiredCapabilities。files 的 role 为 definition/ui/runtime/dependency/documentation/license/evidence/data-contract；路径为包内规范 POSIX。definition 文件必须与 manifest.definition 一致。`app-release.json` 本身不放入 files，不能让摘要自引用。

web-bundle.delivery.entrypoints 固定 `{entrypointId,path,spaFallback?}`；native-app保存runtimeInstructionsPath；docker-app同时必填imageRefs，逐项固定显式注册表/repository@sha256，不附登录凭据；实际仍由原容器owner拉取、执行和身份核验。缺容器环境或adapter时明确不可用，不新建容器管理器。平台不解释说明为命令DSL。source 是实际 Git 完整 commit 或工作树内容 sha256；supportedPlatforms 为 darwin/win32/linux/web。最低客户端是 minimumClientVersion，实际能力仍从握手确认。

数据合同声明 formatVersion、readableVersions、writableVersions、有限 files key/path/maxBytes/contentType 和 uninstallRetention: retain。备份/迁移/恢复说明引用必须在 payload 白名单中；说明不授权自动执行，安装历史不代表真实数据备份。

动态 Node 示例的 `/.desirecore-app-identity` 返回当前 TaskHost 注入的 proof/releaseDigest/scopeId/runtimeGeneration；proof 仅用于本次运行身份握手，不当应用 API token，不写日志。`POST /api/apps/runtime/contracts` 使用已 prepare 的材料、installationId、真实 terminalId、endpoint.port/identityPath 与 startupPolicy。服务固定原执行合同后，原 Bash 显式停原命令，正式 commit 后由原 owner 启动新代际再核验。具体环境、执行审批和数据根均由实际 owner 决定。
