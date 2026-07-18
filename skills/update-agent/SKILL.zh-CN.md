<!-- locale: zh-CN -->

# update-agent 技能

## L0：一句话摘要

通过自然语言对话，安全地修改 Agent 的配置、人格、规则和技能。

## L1：概述与使用场景

### 能力描述

update-agent 是一个**元技能（Meta-Skill）**，允许用户通过对话方式修改 Agent 的各项配置。所有修改都会生成可审阅的 diff 补丁，经用户确认后才会应用，并支持版本回滚。

### 使用场景

- 用户想要调整 Agent 的沟通风格（"说话再正式一点"）
- 需要添加新的行为规则（"以后遇到敏感话题要先提醒我"）
- 安装或卸载技能包（"学会写合同吧"）
- 批量更新多项配置（"全面升级一下你的能力"）

### 核心价值

- **安全可控**：所有变更需用户确认，支持回滚
- **透明可见**：变更以 diff 形式展示，清晰明了
- **版本管理**：通过 Git 管理版本，可追溯历史
- **校验兜底**：结构化字段（name/description/llm/persona/principles）经 ManageAgent 内置工具的白名单 + schema 校验，非法配置不会落盘

## L2：详细规范

### 支持的更新类型

| 更新类型        | 目标            | 更新手段            | 风险等级 | 示例                 |
| --------------- | --------------- | ------------------- | -------- | -------------------- |
| 名称/描述       | `agent.json`    | ManageAgent update  | 低/中    | 改名、改简介         |
| LLM 配置        | `agent.json`（llm） | ManageAgent update | 中    | 换模型、调温度       |
| Persona 更新    | `persona.md`    | ManageAgent update  | 中       | 修改沟通风格、价值观 |
| Principles 更新 | `principles.md` | ManageAgent update  | 高       | 添加/修改行为规则    |
| Skills 安装     | `skills/`       | Read/Write          | 中       | 添加新技能包         |
| Skills 卸载     | `skills/`       | Read/Write          | 低       | 移除技能包           |
| Memory 更新     | `memory/`       | Read/Write          | 低       | 添加知识条目         |
| Tools 配置      | `tools/`        | Read/Write          | 高       | 修改工具权限         |

**两条更新路径**：结构化字段（name/description/llm/persona/principles）一律经进程内内置工具 **ManageAgent** 的 `update` 动作更新（白名单 + schema 校验 + 合并语义）；记忆、技能、工具等自由格式文件仍用 Read/Write 直接编辑。详见「阶段 5：变更应用」。

### 对话流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   意图识别    │ ──→ │   变更分析    │ ──→ │   Diff 生成   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   回执生成    │ ←── │   变更应用    │ ←── │   用户确认    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 阶段 1：意图识别

**触发条件**（任一满足）：

- 用户说"修改你的..."、"更新你的..."、"调整一下..."
- 用户说"你以后要..."、"记住这个规则..."
- 用户说"安装/卸载这个技能..."
- 用户描述对当前行为的不满并期望改变

**输出**：识别更新类型和目标范围。

### 阶段 2：变更分析

**分析维度**：

| 维度     | 说明                     |
| -------- | ------------------------ |
| 影响范围 | 影响哪些文件、哪些行为   |
| 风险等级 | 低/中/高（见风险分级表） |
| 依赖检查 | 是否影响其他配置         |
| 冲突检测 | 是否与现有规则冲突       |

**风险分级表**：

| 风险等级 | 条件                           | 确认要求               |
| -------- | ------------------------------ | ---------------------- |
| 低       | 仅影响非核心配置（如记忆条目） | 简单确认               |
| 中       | 影响 persona 或普通 principles | 展示 diff 后确认       |
| 高       | 影响核心 principles 或工具权限 | 详细说明 + diff + 确认 |
| 受保护   | 触及受保护路径                 | 阻断，需 owner 权限    |

### 阶段 3：Diff 生成

**Diff 格式示例**：

```diff
# persona.md

## 沟通风格

- 友好、随和、轻松幽默
+ 专业、严谨、适度幽默

## 决策偏好

  保持不变...
```

**Diff 元数据**：

```yaml
diff_metadata:
  files_affected: 1
  lines_added: 1
  lines_removed: 1
  risk_level: medium
  reversible: true
  estimated_impact: '沟通风格会变得更正式'
```

### 阶段 4：用户确认

**确认界面**：

```
变更预览

影响文件: persona.md
风险等级: 中
影响说明: 沟通风格会从"友好随和"变为"专业严谨"

--- 变更内容 ---
[展示 diff]
----------------

请确认是否应用此变更？
[应用] [取消] [修改]
```

**确认选项**：

- **应用**：执行变更
- **取消**：放弃变更
- **修改**：进入编辑模式微调

### 阶段 5：变更应用

变更应用分两条路径，取决于目标是**结构化字段**还是**自由格式文件**。**不要调用 HTTP API**（实例鉴权后 Agent 无法访问本机 HTTP API），**不要直接操作 Git**（版本管理由后端自动处理）。

#### 路径 A：结构化字段 → ManageAgent 内置工具（强制）

以下字段**必须**通过进程内内置工具 `ManageAgent` 的 `update` 动作更新，**禁止**直接 Write `agent.json` / `persona.md` / `principles.md`：

| 字段          | 约束                                   | 落地位置          |
| ------------- | -------------------------------------- | ----------------- |
| `name`        | 1–50 字符                              | `agent.json`      |
| `description` | ≤200 字符                              | `agent.json`      |
| `config.llm`  | 增量浅合并；**config 只允许 `llm`**    | `agent.json`      |
| `persona`     | 结构化对象 `{L0, L1:{...}, L2}` 或 markdown 字符串 | `persona.md`    |
| `principles`  | 结构化对象 `{L0, L1:{...}, L2}` 或 markdown 字符串 | `principles.md` |

**调用形式**：

```
ManageAgent(action='update', id='<agent-id>', name='新名称')
ManageAgent(action='update', id='<agent-id>', description='一句话简介')
ManageAgent(action='update', id='<agent-id>', config={ llm: { model: 'xxx', temperature: 0.7 } })
ManageAgent(action='update', id='<agent-id>', persona={ L1: { personality: ["专业", "严谨"] } })
ManageAgent(action='update', id='<agent-id>', principles='...（完整 markdown）...')
```

**合并语义（重要）**：

- 结构化 `persona` / `principles` 是**字段级合并**：省略的字段保留原值（如只传 `L1.personality` 不会清掉 L0 / role）
- markdown 字符串是**整体替换**（用于整篇重写）
- `config.llm` 是**增量浅合并**：只覆盖你传入的 key
- 合并后的 `agent.json` 会整体过 schema 校验，非法配置不落盘

**确认行为**：

- 更新**自身**免二次确认
- 更新**其他智能体**会触发用户确认（与本技能的 diff 确认叠加）
- 核心智能体（`desirecore` / `core`）拒绝更新

**改前先读**：改之前先用 `ManageAgent(action='get', id='<agent-id>')` 读取现值，用于生成 diff、校对字段名（persona / principles 的实际字段名以 `get` 返回的结构为准）。

**config 白名单**：`config` 仅接受 `llm`。传入 `mcp_servers` / `tool_permissions` / `version` / `id` 等会被拒绝并指明字段名——`llm` 以外的运行时配置不走 ManageAgent，见「阶段 5 · 路径 B」与错误处理。

**部分写入失败**：工具会精确报告"哪些字段已生效、哪个失败"，重试时**只提交失败字段**，不要整体重发。

> **改名一次调用完成。** 用户要改**显示名称**（如"把 X 改名为 Y"）时，直接 `ManageAgent(action='update', id='<agent-id>', name='Y')` 即可——`name` 写入 `agent.json` 并触发智能体列表刷新，无需再手动编辑任何文件。若用户希望人格文档标题也同步，可在同一轮追加一次 `persona` 更新。**绝不要在没有实际调用 ManageAgent 的情况下声称已改名。**

#### 路径 B：自由格式文件 → Read/Write 直接编辑

记忆、技能、工具等**自由格式文件**不在 ManageAgent 范围，仍用 Read/Write 工具直接编辑：

| 目标     | AgentFS 路径 |
| -------- | ------------ |
| 记忆条目 | `memory/`    |
| 技能包   | `skills/`    |
| 工具配置 | `tools/`     |

**AgentFS 根目录**：`${DESIRECORE_ROOT}/agents/<agentId>/`

**读取文件**：使用 Read 工具读取目标文件当前内容。

**写入文件**：使用 Write / Edit 工具直接写入目标文件。写入后重新读取文件确认内容正确。

**受保护路径**：编辑前对照 `_protected-paths.yaml`，触及受保护路径应阻断并提示需 owner 权限。

**注意**：直接写入自由格式文件后，后端文件监控会自动检测变更并触发 Git 提交，无需手动执行 git 命令。

### 阶段 6：回执生成

创建成功后，以用户友好的方式呈现回执（不要暴露内部路径或技术细节）：

> 已更新「法律顾问小助手」的沟通风格。
>
> **变更摘要**：沟通风格从"友好随和"调整为"专业严谨"
>
> 如果不满意，可以随时说"撤销刚才的修改"来回滚。

### 特殊操作：版本回滚

**触发条件**：用户说"撤销刚才的修改"、"回滚到之前的版本"、"恢复原来的设置"

**回滚流程**：

1. 在 Agent 目录下执行 `git log --oneline -10` 查看最近的版本历史
2. 使用 `git show <commit>:<file>` 获取目标版本的文件内容，展示给用户确认
3. 用户确认后，按目标文件类型应用：
   - **结构化字段**（`persona.md` / `principles.md` / `agent.json` 的 name/description/llm）→ 用 `ManageAgent(action='update', ...)` 写回（persona / principles 以 markdown 字符串**整体替换**为该历史内容）
   - **自由格式文件**（`memory/` / `skills/`）→ 用 Write 工具直接写回
4. 展示变更 diff，确认回滚成功

（`git log` / `git show` 仅用于**读取**历史，回写一律走上述两条路径，不要用 git 命令直接改写工作区文件。）

```bash
# 查看版本历史
cd ${DESIRECORE_ROOT}/agents/<agentId>
git log --oneline -10

# 查看某个版本的文件内容
git show <commit>:persona.md
```

### 背景知识

> AgentFS 仓库结构与受保护路径详见 `_agentfs-background.md` 和 `_protected-paths.yaml`。

**更新操作对照表**：

| 用户意图              | 更新手段                                                                 |
| --------------------- | ------------------------------------------------------------------------ |
| **改名（显示名称）**  | `ManageAgent(action='update', id, name='...')`                           |
| 改简介                | `ManageAgent(action='update', id, description='...')`                    |
| 修改 LLM 配置（模型/温度等） | `ManageAgent(action='update', id, config={ llm: {...} })`         |
| 修改性格/风格         | `ManageAgent(action='update', id, persona={...} 或 markdown)`           |
| 修改行为规则          | `ManageAgent(action='update', id, principles={...} 或 markdown)`        |
| 安装/卸载技能         | Read/Write `skills/`（`${DESIRECORE_ROOT}/agents/<agentId>/skills/`）    |
| 添加记忆              | Read/Write `memory/`（`${DESIRECORE_ROOT}/agents/<agentId>/memory/`）    |
| 修改工具配置          | Read/Write `tools/`（`${DESIRECORE_ROOT}/agents/<agentId>/tools/`，注意受保护路径） |

> `agent.json` 中 `llm` 以外的运行时配置（`mcp_servers` / `tool_permissions` 等）当前不在 ManageAgent 白名单，也不应直接 Write `agent.json` 绕过校验。遇到此类需求，向用户说明暂需通过对应机制处理。

### 错误处理

| 错误场景                     | 处理方式                                                     |
| ---------------------------- | ---------------------------------------------------------- |
| `config` 含非白名单字段      | ManageAgent 拒绝并指明字段名；改走对应机制或告知用户暂不支持 |
| schema 校验失败              | 非法配置不落盘；按工具返回修正字段后重试                    |
| 更新核心智能体（desirecore/core） | ManageAgent 拒绝更新；告知用户核心智能体不可修改       |
| 部分字段写入失败             | 工具报告已生效/失败字段；仅重试失败字段，不整体重发         |
| 尝试修改受保护路径（自由文件） | 阻断操作，提示需要 owner 权限                             |
| 文件不存在                   | Agent 或目标文件不存在，提示用户检查                       |
| 权限不足                     | 文件系统权限错误，提示用户检查目录权限                     |
| 回滚版本不存在               | 列出可用版本，请用户重新选择                               |

### 权限要求

| 操作                        | 所需角色      |
| --------------------------- | ------------- |
| 更新 persona                | owner, member |
| 更新 principles（普通规则） | owner, member |
| 更新 principles（安全红线） | owner         |
| 安装/卸载 skills            | owner, member |
| 修改 tools 权限             | owner         |
| 版本回滚                    | owner         |

---

## 附录：更新示例

### Persona 修改示例

**用户输入**："说话再正式一点，不要太随意"

**操作流程**：

```
# 1. 读取当前 persona，定位要改的字段（字段名以返回结构为准）
ManageAgent(action='get', id='legal-assistant')

# 返回中的 "## persona.md" 段落即当前 persona 原文（L0/L1/L2 分层 markdown），例如:
# ## persona.md
# # L0
# 专业的法律咨询助手
# # L1
# ## role
# 法律顾问
# ## personality
# - 友好
# - 随和
# ## communication_style
# 轻松幽默

# 2. 分析需要修改的部分，生成 diff 展示给用户确认

# 3. 用户确认后，用 ManageAgent 字段级合并更新（只改这两个字段，L0/role 保留）
ManageAgent(action='update', id='legal-assistant', persona={
  L1: { personality: ["专业", "严谨"], communication_style: '正式、克制' }
})

# 4. 复核结果
ManageAgent(action='get', id='legal-assistant')
```

---

### Principles 更新示例

### 添加新规则

**用户输入**："以后遇到法律问题，先提醒我找专业律师"

**生成的 Diff**：

```diff
# principles.md

## 必须做

  - 始终保持礼貌和尊重
  - 不确定时主动询问
+ - 遇到法律相关问题时，提醒用户咨询专业律师

## 绝不做
  ...
```

**用户确认后应用**：先 `ManageAgent(action='get', id)` 取当前 principles，把整篇内容（含新增规则）以 markdown 字符串整体替换：

```
ManageAgent(action='update', id='legal-assistant', principles='...（整篇 markdown，含新增规则）...')
```

（若只改结构化对象的某个字段，也可用字段级合并传 `principles={ L1: { must_do: [...] } }`。结构化字段名固定为：persona 的 `L1.role` / `L1.personality`（字符串数组）/ `L1.communication_style`，principles 的 `L1.must_do` / `L1.must_not`（均为字符串数组）/ `L1.priority`，另有顶层 `L0` / `L2` 字符串。）

### 修改现有规则

**用户输入**："不要每次都提醒我，太啰嗦了"

**生成的 Diff**：

```diff
# principles.md

## 必须做

- - 每次回答后都提醒用户检查内容
+ - 仅在重要决策时提醒用户检查内容
```

**用户确认后应用**：同上，用 `ManageAgent(action='update', id, principles=...)` 写回修改后的内容。
