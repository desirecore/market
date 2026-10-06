<!-- locale: zh-CN -->

# manage-teams 技能

## L0：一句话摘要

通过 `ManageTeam` 查询、创建和治理 Agent 团队，并在组织变更或远程同步前完成必要检查。

## L1：何时使用

以下情况使用团队：

- 多个 Agent 需要围绕同一任务持续协作并共享团队工作目录；
- 需要稳定的组长、成员关系或父子团队组织结构；
- 需要发布、安装或同步一个团队仓库。

以下情况不要创建团队：

- 一次性向一个专家求助：直接 `Delegate(mode="sync" | "async")`；
- 多个专家只需各自给出一次意见：直接 `Delegate(mode="fan-out")`；
- 只是临时文件探索：使用 Worker，不要制造长期组织关系。

团队只定义组织、共享目录和治理关系。实际给成员分派工作仍使用 `Delegate`。

## L2：执行规范

### 1. 先查再改

- 不知道 `teamId` 时先执行 `ManageTeam(action="list")`。
- 修改、解散或远程同步前执行 `ManageTeam(action="get", teamId=...)`，核对名称、类型、组长、成员、本地仓库目录和远程状态。
- 不要猜测 `~/.desirecore` 下的路径；本地仓库绝对路径只使用 `get` 返回值。
- `list` 可传 `parentTeamId` 过滤；`tree=true` 返回组织树，此时 `teamId` 表示子树根，`parentTeamId` 不生效。

### 2. Action 对照表

| action | 用途 | 关键参数与注意事项 |
|---|---|---|
| `list` | 列出团队或组织树 | `parentTeamId?`、`tree?`、`teamId?` |
| `get` | 查看单个团队详情和仓库路径 | `teamId` |
| `create` | 创建临时团队 | `name` 或 `task`；`supervisor?`、`members?`、`memberRouting?`、`parentTeamId?`、`workdirMode?` |
| `add_member` | 添加一个成员 | `teamId`、`agentId` |
| `add_members` | 批量添加成员 | `teamId`、`members` |
| `remove_member` | 移除一个成员 | `teamId`、`agentId` |
| `remove_members` | 批量移除成员 | `teamId`、`members` |
| `set_supervisor` | 更换组长 | `teamId`、`agentId` |
| `set_member_source` | 声明成员 Agent 的来源 | `teamId`、`agentId`、`memberSource`；`git` 必填 `url`（https，将被 clone）与 `ref`（默认 `main`），`registry` 必填 `id`+`version`，`core`/`local` 无附加字段 |
| `update` | 部分更新团队配置 | `teamId`；可更新 `name/type/isolation/parentTeamId/description/avatar/avatarImage` |
| `promote` | 临时团队升级为持久团队 | `teamId`；单向操作，不得隐式执行 |
| `disband` | 解散团队 | `teamId`；若提交审批；完整归档，恢复需重新绑定目录和核准内容 |
| `fork_team` | 从远程仓库安装团队 | `url`；`name?`、`installMembers?`；进入审批闸门 |
| `push` | 把本地团队仓库推送到已连接的远程 | `teamId`；进入审批闸门 |
| `pull` | 从已连接的远程拉取并校验团队 | `teamId`；进入审批闸门 |
| `add_remote` | 配置或更换发布目标 | `teamId`、`url`；`connectionId?`、`branch?`、`isPrivate?`；不创建远程仓库 |
| `remove_remote` | 移除远程配置与本机连接绑定 | `teamId`；不删除远程仓库 |
| `install_members` | 按现有 lock 补齐成员 | `teamId`；`forceUpdate?`，默认 false |
| `upgrade_members` | 解析新 lock 并尝试安全升级 | `teamId`；`forceUpdate?`，默认 true；保留本机修改和提交 |
| `release` | 创建本地版本或发布精确版本 | `teamId`；`push?` 默认 false、`changelogEntry?`、`expectedCommit?`；重试已有版本用 `releaseTag` |

### 3. 创建团队

创建前必须满足：

1. `supervisor` 和 `members` 中的 Agent 均已存在。缺少时先用 `ManageAgent(action="list" | "get")` 核对，确需新增时再按对应 Agent Skill 创建。
2. DesireCore 核心智能体 `desirecore` 不能担任组长。由核心智能体发起创建时必须显式指定普通 Agent 为 `supervisor`。
3. 通常不要把 `desirecore` 加入成员；需要核心能力时通过 `Delegate` 调用。
4. 一个 Agent 只能担任一个团队的组长；目标组长已有团队时，先为原团队指定接替者。

工作目录选择：

- `merged`（默认）：团队共享目录优先，同时保留成员和全局工作目录；
- `team_only`：只暴露团队共享目录，适合所有成员必须围绕同一项目目录工作的高可靠任务；不会删除成员原有目录配置。

智能路由通过 `memberRouting` 表达意图，不写死 Provider 或模型：

```json
{
  "supervisor-agent": {
    "tier": "flagship",
    "requiredCapabilities": ["reasoning"],
    "reasoning": "high"
  },
  "member-agent": {
    "tier": "balanced"
  }
}
```

- 键必须属于本次 `supervisor` 或 `members`；
- 使用 fixed 模型的成员不能出现在 `memberRouting`；
- 未填写的 Smart 成员保留现有路由档案；具体 Provider/模型在成员实际执行任务前解析。

示例：

```json
{
  "action": "create",
  "name": "合同审查项目组",
  "supervisor": "legal-lead",
  "members": ["contract-reviewer", "risk-analyst"],
  "task": "持续审查合同并汇总风险",
  "workdirMode": "team_only"
}
```

### 4. 修改组织与配置

- 成员增删优先使用批量 action，避免多次调用产生中间状态。
- `set_supervisor` 使用 `agentId` 指定新组长；先确认其未担任其他团队组长。
- `set_member_source` 声明来源，不搬运文件。名册里只要还留着 `local` 成员，团队就**不可分发**——`members.lock.json` 无法锁定一个只存在于本机的 ID，别处 fork 出来会静默缺员。发布前把每个成员改为 `git` 或 `registry`；该动作会自动解析并写 lock，核对解析回执即可。它改不了成员的 `role`，换组长用 `set_supervisor`。
- `update` 是部分更新：未传字段保持原值。
- `parentTeamId: null` 表示摘除父团队成为顶层团队；空字符串非法。
- `type` 只允许 `ephemeral → persistent`。原值幂等更新可以接受；明确升级优先使用 `promote`。
- `isolation`：`soft` 共享会话隔离，`hard` 使用独立 Agent 副本。
- `description` 是团队市场简介，不等同于 `create` 的 `task`。

声明头像使用：

```json
{
  "action": "update",
  "teamId": "team-id",
  "avatar": { "char": "审", "color": "purple" }
}
```

图片头像使用 `avatarImage.source`，可传 `dc-media://<mediaId>`、裸 `mediaId` 或工作目录内图片路径。支持 PNG/JPEG/WebP；不传 HTTP(S) URL 或 base64。移除图片使用 `{ "remove": true }`，不得与 `source` 同时出现。

### 5. 团队生命周期

- 临时团队完成一次项目后应解散，避免组织结构长期堆积。
- 只有明确存在长期协作需求时才 `promote`；这是单向升级。
- `disband` 完整归档团队目录并结束本机工作目录绑定；不依赖 Git 初始化。归档失败保留原数据并报告失败。该动作提交审批，是否显示真人卡片由调用方的审批模式决定。恢复时先确认 teamId 未被占用，再绑定工作目录、重新核准内容。

### 6. 团队仓库与远程同步

团队目录是 Git 仓库，包含 `team.json`、成员锁和 `shared/rules.md` 等治理文件。

本地 Git 操作：

1. 用 `get` 取得仓库绝对路径；
2. 用 Bash 在该目录执行 `status/log/diff/add/commit/tag`；
3. 本地提交完成后，再调用 `ManageTeam(action="push")`。

远程 `fork_team/push/pull` 必须走 `ManageTeam`，原因是工具会执行团队 Schema、名册一致性、核心智能体组长禁令、工作区类型和越界符号链接校验，并进入审批闸门。不要用裸 `git push/pull` 绕过这些治理步骤；这条规则不是基于“Agent 一定拿不到凭据”的假设。

- `push/pull` 要求已有远程配置；未连接时使用 `add_remote` 配置目标和已有连接。客户端团队设置也是可选入口。Agent 可以自主选择配置方式。
- `create` 和 `fork_team` 得到的本地团队默认都不继承可直接推送的远程配置。
- `fork_team` 默认 `installMembers=true`；本机已偏离锁定版本的同名 Agent 会被跳过保护，不会覆盖。
- `pull` 可能覆盖本地团队配置；先查看本地状态并说明审批卡中的目标远程。

发布与成员版本：

- `release` 默认只创建本地版本；明确要对外发布时传 `push=true`。审批摘要显示实际目标和版本，只推分支及本次正式 tag，不推 `backup/`、`archive/` 或其他 tag。
- 先用 `get` 核对团队；新版本可传 `expectedCommit` 约束 HEAD。返回 `tag/version/commitHash` 与 `branchPushed/tagPushed/pushed`，本地成功和远端发布分别核验。
- 网络失败或远端结果未知时，先检查远端；用返回的 `releaseTag` 重试同一版本，不再次运行无 tag 的 release。重试时不得传 `changelogEntry`。
- `install_members` 按精确 lock 安装；`upgrade_members` 先解析当前声明，再按新 pin 尝试安全更新。它们不覆盖用户修改、本机提交，不自动回退，也不自动核准内容。
- `complete=false` 或成员 `outdated/diverged/failed/unreachable` 表示未对齐；不要把 `success=true`、`skippedCount` 或 `failedCount=0` 当成全员升级完成。读取逐成员回执，确认后选择修复方法。
- 同一 Agent 在多个团队有不同 pin 时，不自动覆盖现有分叉；保留数据并报告冲突。
- 远程动作、远程来源声明和远程目标配置提交审批；`ask-external` 对这些动作保留审批，`allow-all` 保留用户对执行主体的全量信任。

### 7. 分派与收尾

创建团队后，用 `Delegate` 向组长或成员分派任务：

- 单成员：`Delegate(target=..., mode="sync" | "async", teamId=...)`；
- 多成员：`Delegate(targets=[...], mode="fan-out", teamId=...)`；
- 需要持续协作时优先团队内成员，一次性外部意见无需先入队。

完成后向用户报告：团队名称与 ID、类型、组长和成员、工作目录模式、发生的组织变更，以及远程动作是否完成。不要暴露凭据或带 token 的远程 URL。

### 8. 失败恢复

- `Agent 不存在`：核对 ID；先创建或安装 Agent，再重试团队操作。
- `核心智能体不能担任组长`：显式指定普通 Agent 为 `supervisor`。
- `组长已管理其他团队`：先为原团队执行 `set_supervisor`，再重试。
- `未配置远程`：调用 `add_remote` 配置目标，或使用客户端团队设置；不要猜测隐藏 API。
- `本地内容已变化/存在冲突`：先用 `get` 获取目录并检查 Git 状态，保留用户改动后再决定提交、拉取或重试。
- Skill 缺失或禁用时，仍可根据 `ManageTeam` 的 action、参数 Schema 和错误提示执行最小操作，不要因此绕过工具直接修改 AgentFS。
