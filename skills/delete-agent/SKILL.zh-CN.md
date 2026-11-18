<!-- locale: zh-CN -->

# delete-agent 技能

## L0：一句话摘要

归档不再使用的智能体，或从本机归档恢复；保留会话历史，按真实回执报告团队与调度事项。

## L1：概述

用户可以删除、找回误删智能体，或查看本机归档。通过 `ManageAgent` 完成，不直接调用本机 HTTP，不手工移动归档目录。删除即归档：本机可恢复，不自动过期，不进入之后的备份或迁移包。永久删除只能由用户在「设置 → 数据与隐私 → 归档」完成。

## L2：详细规范

### 归档智能体

用户未明确目标时，用 `ManageAgent(action='list')` 列出候选，需要详情时用 `get`。核对名称与 ID，并说明会话历史保留、领导的团队一并归档。用户已明确授权的目标不重复询问；目标含糊时先澄清。工具保留内置智能体、自删及活跃状态保护；活跃目标需先在界面停止或等待空闲。

调用 `ManageAgent(action='delete', id='example-agent')`。不要询问是否同时删除历史，不传 `deleteRuns=true`，新工具会拒绝它。工具按调用方审批模式裁决，不承诺一定弹卡。成功后只根据真实回执报告归档标识、团队和 worktree 处置及警告；解除绑定会保留工作树与分支。保存 `archiveId` 供需要时恢复，不把归档说成释放全部磁盘。

### 查看归档与恢复

用 `ManageAgent(action='list_archived')` 查本机归档。该动作只读，不前滚或修复未完成事务；按 `phase`、`restorable` 和 `originalIdOccupied` 说明当前状态。缺少目标标识或归档已消失时重新查询，不猜 `archiveId`。

对可恢复项调用 `ManageAgent(action='restore', archiveId='列表返回的标识')`。原 ID 被占用时先取得用户选择的新名称，再传 `name`；不得覆盖已有智能体。原 ID 空闲时，提供 `name` 只改名，不强制换 ID。`restoreLedTeams` 默认 `true`，用户要求团队继续留在归档时传 `false`。

原 ID 冲突会导致新 ID：会话历史留在原 ID 下，调度不恢复；私有技能里的绝对路径环境可能要重新准备。执行前说明这些影响。恢复与创建同档，无额外确认；既有身份与权限仍由 owner 校验，不自报 `userId` 或冒充官方 Renderer。

### 按回执完成交接

`agentId` 是实际恢复对象；`idChanged`、`runsAttached` 说明身份与历史归属。逐项报告 `teams.restored`、`teams.pending`、`teams.memberOf` 与 `warnings`。未一并恢复的领导团队需在归档页团队分段处理，原成员资格不还原。

调度不会自动启用：`schedules.reenablable` 可经原入口重新启用，`recreateRequired` 需重新创建（脚本需重新上传），`dropped` 表示新 ID 恢复时未带回的定义。旧实例授权不复活；MCP OAuth、App 链接与 worktree 绑定不还原。不要因 Agent 已恢复而宣称所有团队、调度或授权已恢复。

### 失败和永久删除

保留工具返回的错误码、状态和警告。`AGENT_RESTORE_ID_OCCUPIED` 需要 `name` 或重新查询并发占用事实；`AGENT_RESTORE_USER_MISMATCH` 不可通过自报身份绕过；未完成、损坏或占位待收尾的归档按当前失败说明交接，不私自清理容器。未知结果先用列表核实，不重复创建或恢复。

用户明确要求永久删除或删除历史时，引导到界面，由用户查看凭据文件与历史范围并完成确认；不尝试 `purge`、Bash 删除目录或受 Renderer 保护的 HTTP 端点。此前已有备份副本不受永久删除影响。市场卸载是否可恢复按实际客户端能力判断，不用本技能承诺尚未交付的后续分期。
