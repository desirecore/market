# 固定应用版本分发

1. 确认用户要分发的精确版本、真实目标仓库/Registry、公共或私有范围、实际登录连接和材料许可。生成文件、个人发布或已有预览都不是上传授权；既有会话中的明确分发授权直接沿用。
2. 用原 AppManage 的 export_release 动作，从 prepareRef，或 installationId + expectedRevision 导出；完整 AppReleaseExportRequest 放在 owner_request。`paths` 必须显式覆盖全部 payload + app-release.json；不包含服务物化 descriptor、owner 标记、个人数据和秘密。核验响应的 files、size 和下载原始字节 archiveDigest。exportRef/downloadPath 只说明制品已生成，HTTP 下载仍须平台合法管理通道；普通 HttpRequest 不自动注入凭据，缺少实际材料通道时不假称已经取得 ZIP。
3. GitHub Release 通过实际授权工具上传此 ZIP，核读真实下载地址、固定 commit 和原始字节摘要；Gitea 私有仓库可提交 `releases/<version>.zip`，取得完整 commit 与该路径。可变 tag/latest 只作展示，必须解析到固定引用。没有真实来源回执就报告“制品已生成，尚未上传”。
4. 由有合法凭据的平台管理通道调用 `POST /api/apps/distribution/prepare`，普通模型不读取实例 token 或改 Origin 绕过认证。缺少目录生成通道时说明不可用；其输入 `exportRef`、用户已登记的 registryRepoId、`source:{kind:'release'|'git',url,ref,sha256,path?}` 和实际 metadata。git 必须给固定包路径，sha256 必须等于导出 archiveDigest。产品 ID/名称/版本/入口不由 metadata 另填。
5. metadata 包含 author/description/tags/category/license/redistribution/availability/requiredClientVersion，以及实际维护者、品牌和复核材料。证据不足保留 listing-only；不要填不存在的审核者、认证、发布时间或平台验收。已复核的许可证路径应来自同一 release 的 license role 文件。
6. 返回的是 `entries/<id>/manifest.json`、`catalog-metadata.v1.json`、`install.md` 内容和摘要。mapping 关联目标 sourceId、逻辑 ID、releaseDigest 与 archiveDigest，descriptor 安装时按真实来源物化。将三文件写入实际授权的目录仓库后审阅 diff，通过其原治理提交 PR；不能自动合并或说目录已开放。
7. 查询真实目录可获取状态与目标客户端握手，再由第二用户/设备沿原 acquisition/app-install-manager 路径安装并核验。两来源同名不共享实例或数据；目录更新仅给更新候选，不改原安装快照。

候选 Registry 4.3 Schema 与客户端 reader 必须先分别 review；正式 Registry seed 只指已合入的受审提交。候选 reader 仅在明确受信的非官方测试来源开放，正式条目等待客户端能力发行，不能借 10.0.180 字符串跳过 app-authoring-v1。

私有源使用 `access: private` 的真实 Registry 连接，只读登记端点、不转公开镜像；认证失败拒绝新获取。字段不是 ACL，GitHub/Gitea 管理员仍负责实际成员权限。平台团队成员移除不自动改变源端 ACL，不能宣称已撤销。已下载字节不能收回，本机数据不自动删除。

离线可继续使用已核验的本地固定版本，远端依赖如实不可用；离线不能产生新的来源上传成功。目录撤回阻止新获取并保留理由，不自动卸载已安装应用。临时导出不修改当前个人发布，取消分发保留原工作台。
