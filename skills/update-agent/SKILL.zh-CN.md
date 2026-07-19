<!-- locale: zh-CN -->

# update-agent 技能

## L0：一句话摘要

通过自然语言对话，安全地修改 Agent 的配置、人格、规则和技能。

## L1：概述

元技能：识别修改意图 → 生成可审阅 diff → 用户确认 → 应用（结构化字段走 ManageAgent、自由文件走 Read/Write）→ 回执，并支持版本回滚。价值在工具给不了的部分：diff 预览确认、两路径编排、回滚；结构化字段经 ManageAgent 白名单 + schema 校验，非法配置不落盘。

## L2：详细规范

### 更新类型与两条路径

结构化字段一律经 `ManageAgent(action='update')`（白名单 + 校验 + 合并语义）；记忆/技能/工具等自由格式文件用 Read/Write 直接编辑：

| 用户意图 | 手段 | 目标（风险） |
| --- | --- | --- |
| 改名（显示名称） | `ManageAgent(update, name=...)` | agent.json（中） |
| 改简介 | `ManageAgent(update, description=...)` | agent.json（低） |
| LLM 配置（模型/温度） | `ManageAgent(update, config={llm:{...}})` | agent.json（中） |
| 性格/风格 | `ManageAgent(update, persona=... 或 markdown)` | persona.md（中） |
| 行为规则 | `ManageAgent(update, principles=... 或 markdown)` | principles.md（高） |
| 安装/卸载技能 | Read/Write | `skills/`（低/中） |
| 添加记忆 | Read/Write | `memory/`（低） |
| 修改工具配置 | Read/Write | `tools/`（高，注意受保护路径） |

流程：意图识别 → 变更分析 → diff 生成 → 用户确认 → 应用 → 回执。

### 阶段 1：意图识别

触发（任一）：用户说"修改/更新/调整你的…"、"你以后要…/记住这个规则…"、"安装/卸载这个技能…"，或描述对当前行为的不满并期望改变。识别更新类型与目标范围。

### 阶段 2：变更分析

评估影响范围（哪些文件/行为）、依赖与冲突，并定风险等级 → 对应确认强度：

- 低（记忆条目等非核心）：简单确认
- 中（persona / 普通 principles）：展示 diff 后确认
- 高（核心 principles / 工具权限）：详细说明 + diff + 确认
- 受保护（触及受保护路径）：阻断，需 owner 权限

### 阶段 3：diff 生成

生成变更前后 diff 展示给用户（只展示实际改动），例如：

```diff
# persona.md → ## 沟通风格
- 友好、随和、轻松幽默
+ 专业、严谨、适度幽默
```

### 阶段 4：用户确认

展示 diff 预览（影响文件、风险等级、影响说明 + diff），请用户确认「应用 / 取消 / 修改」；选"修改"进入微调后再确认。（工具层对更新他人/核心体另有强制确认，见阶段 5。）

### 阶段 5：变更应用

不要调 HTTP API（实例鉴权后不可达），不要直接操作 git（后端自动提交）。按目标分两路：

**路径 A · 结构化字段 → ManageAgent（强制；禁止直接 Write `agent.json` / `persona.md` / `principles.md`）**

字段与约束：`name`（1–50 字符）、`description`（≤200）、`config.llm`（增量浅合并，**config 仅允许 llm**）、`persona` / `principles`（结构化对象 `{L0, L1:{...}, L2}` 或 markdown 字符串）。调用：

```
ManageAgent(action='update', id='<agent-id>', name='新名称')
ManageAgent(action='update', id='<agent-id>', persona={ L1: { personality: ["专业","严谨"] } })
ManageAgent(action='update', id='<agent-id>', principles='…完整 markdown…')
```

**合并语义**：结构化 persona/principles 为**字段级合并**（省略字段保留原值，如只传 `L1.personality` 不会清掉 L0/role）；markdown 字符串为**整体替换**（整篇重写）；`config.llm` 为**增量浅合并**。合并结果整体过 schema 校验，非法配置不落盘。

要点：

- **改前先读**：先 `ManageAgent(action='get', id)` 取现值，用于生成 diff、校对字段名。结构化字段名固定：persona 的 `L1.role` / `personality`（字符串数组）/ `communication_style`，principles 的 `L1.must_do` / `must_not`（字符串数组）/ `priority`，加顶层 `L0` / `L2`。
- **确认与边界**：更新自身免二次确认；更新其他智能体触发用户确认（与本技能 diff 确认叠加）；核心智能体（`desirecore` / `core`）拒绝更新。
- **config 白名单**：`config` 仅接受 `llm`；`mcp_servers` / `tool_permissions` / `version` / `id` 等会被拒并指明字段名——这类运行时配置不走 ManageAgent，向用户说明暂需经对应机制处理。
- **部分写入失败**：工具精确报告已生效/失败字段，仅重试失败字段，不整体重发。
- **改名一次调用完成**：用户要改显示名称时直接 `ManageAgent(action='update', id, name='Y')`（写 agent.json 并刷新列表），如需人格文档标题同步可同轮追加 persona 更新。**绝不在未实际调用 ManageAgent 时声称已改名。**

**路径 B · 自由格式文件 → Read/Write**（`memory/` / `skills/` / `tools/`，根 `${DESIRECORE_ROOT}/agents/<agentId>/`）：先 Read 现值，再 Write/Edit，写后重读确认。编辑前对照 `_protected-paths.yaml`，触及受保护路径应阻断并提示需 owner 权限。写入后后端文件监控自动 git 提交，无需手动 git。

### 阶段 6：回执

以用户友好方式呈现变更摘要（不暴露内部路径/技术细节），并告知可随时说"撤销刚才的修改"回滚。

### 版本回滚

触发：用户说"撤销/回滚/恢复原来的设置"。流程：

1. Agent 目录下 `git log --oneline -10` 看历史、`git show <commit>:<file>` 取目标版本内容，展示给用户确认。
2. 确认后按类型回写：结构化字段（persona/principles、agent.json 的 name/description/llm）→ `ManageAgent(action='update', ...)`（persona/principles 以 markdown 字符串**整体替换**为历史内容）；自由文件（memory/skills）→ Write 直接写回。
3. 展示 diff 确认回滚成功。

（git 仅用于**读**历史，回写一律走上述两路径，不要用 git 命令直接改工作区文件。）

### 背景与错误处理

- AgentFS 结构、受保护路径详见 `_agentfs-background.md` 与 `_protected-paths.yaml`。
- 工具报错时：config 非白名单字段 / schema 校验失败 / 核心体拒绝 → 按工具提示修正或告知用户；受保护路径 → 阻断并提示需 owner；回滚版本不存在 → 列出可用版本请用户重选。
