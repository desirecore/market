<!-- locale: zh-CN -->

# clone-agent 技能

## L0：一句话摘要

把一个现有智能体完整克隆为独立的本地副本，并明确处理私有数据与团队分发影响。

## L1：概述

当用户需要“复制一个相同能力的 Agent”“基于现有 Agent 做独立变体”时使用本技能。克隆会保留源 Agent 的 persona、principles、技能与配置，但生成新的 ID 和 UUID；它不是重新创建空模板，也不会在 GitHub、Gitee 等代码托管平台创建 fork。

## L2：详细规范

流程：确认 clone 是否合适 → 检查源 Agent → 确认副本名称与私有数据选项 → 调用 ManageAgent → 报告副本性质与后续影响。

### 1. 判断 clone 还是 create

- 用户要保留现有 Agent 的人格、规则、技能和配置，只做独立副本或后续变体：用 `clone`。
- 用户只想创建同领域但设定不同的新 Agent：加载 `create-agent`，用 `create`。
- 不要为了“像某个 Agent”而重新 create；create 只生成新模板，不会继承源 Agent 的能力包。

### 2. 确认源 Agent

用户未给准确 ID 时先调用 `ManageAgent(action='list')`；必要时用 `ManageAgent(action='get', id)` 核对名称、状态和描述。

以下情况工具会拒绝，直接解释原因，不要绕过：

- 核心智能体 `desirecore` 不可克隆。
- 由人类固定为 fixed 模型路由的 Agent 不允许模型自主克隆，应请用户使用界面完成。
- 源 Agent 不存在。

### 3. 副本名称与私有数据

- `name` 可选；不传时默认为“源名称 (副本)”。
- 默认不复制用户私有数据。只有用户明确要求副本继承记忆、偏好或关系时才传 `copyUserData`。
- `copyUserData.memory`：复制用户与源 Agent 的私有记忆。
- `copyUserData.preferences`：复制用户对源 Agent 的偏好配置。
- `copyUserData.relationship`：复制用户与源 Agent 的关系档案。

启用任一私有数据复制前，向用户说明复制范围并确认；不要根据“完整克隆”自行推断用户同意复制私有数据。

### 4. 执行克隆

基础调用：

```json
{
  "action": "clone",
  "id": "source-agent-id",
  "name": "新副本名称"
}
```

明确复制私有数据时：

```json
{
  "action": "clone",
  "id": "source-agent-id",
  "name": "新副本名称",
  "copyUserData": {
    "memory": true,
    "preferences": false,
    "relationship": false
  }
}
```

ManageAgent 会执行纯本地复制、应用调用方与源 Agent 的 Provider ceiling、注册新 Agent，并在注册失败时清理不完整副本。不要自行调用 git fork、HTTP API 或直接复制 AgentFS 目录。

### 5. 回执与团队影响

成功后向用户说明：

- 新 Agent 的 ID，以及它已经可以用于 Delegate / ManageTeam。
- 实际复制了哪些私有数据；源没有的数据会被跳过，以工具回执为准。
- 副本属于 `local` 来源。把它加入团队会使团队 `distributable=false`；如果团队未来需要发布或供他人 fork，应改用已发布到远程仓库的 Agent。

克隆失败时只按工具返回的原因处理。若工具报告补偿清理失败，保留现场并明确提示需要人工治理，不要再次盲目克隆。
