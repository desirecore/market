---
name: discover-agent
description: 根据用户需求推荐最匹配的智能体，展示候选列表并引导选择。Use when 用户描述需求但不确定该找哪个智能体帮忙，或想浏览可用的智能体。
version: 2.6.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - discovery
  - recommendation
metadata:
  author: desirecore
  updated_at: '2026-07-18'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 发现智能体
      short_desc: 根据需求描述智能推荐最匹配的智能体，引导快速选择
      description: 根据用户需求推荐最匹配的智能体，展示候选列表并引导选择。Use when 用户描述需求但不确定该找哪个智能体帮忙，或想浏览可用的智能体。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:99bddbbaea15b194
      translated_by: human
    en-US:
      name: Discover Agent
      short_desc: Intelligently recommend the best-matching Agent based on the user’s need description, and guide quick selection
      description: >-
        Recommend the best-matching Agent based on the user’s needs, show a candidate list, and guide selection. Use when the user describes a need but is unsure which Agent to ask for help, or wants to browse available Agents.
      body: ./SKILL.md
      source_hash: sha256:99bddbbaea15b194
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-18'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="da-a" x1="2" y1="2" x2="22"
    y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"
    stop-opacity="0.12"/><stop offset="1" stop-color="#007AFF"
    stop-opacity="0.06"/></linearGradient></defs><circle cx="12" cy="12" r="10"
    fill="url(#da-a)" stroke="#AF52DE" stroke-width="1.5"/><path d="M16.24
    7.76l-1.8 5.41a2 2 0 0 1-1.27 1.27L7.76 16.24" fill="#FF9500"
    fill-opacity="0.85"/><path d="M7.76 16.24l1.8-5.41a2 2 0 0 1 1.27-1.27L16.24
    7.76" fill="#AF52DE" fill-opacity="0.7"/><circle cx="12" cy="12" r="1.5"
    fill="white" stroke="#AF52DE" stroke-width="0.8"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.90
---

# discover-agent Skill

## L0: One-sentence summary

Match and recommend the most suitable Agent from the registered Agents based on the user’s needs.

## L1: Overview and use cases

### Capability description

discover-agent is a **procedural Skill** that gives DesireCore the ability to discover and recommend suitable Agents for users. By understanding the user’s needs, it performs multi-dimensional matching across the registered Agent list and shows a candidate list for the user to choose from.

### Use cases

- The user describes a need but does not know which Agent to ask for help
- The user wants to browse the currently available Agents and their capabilities
- The user needs to find the most suitable specialist assistant for a specific task
- A new user is using the system for the first time and needs to know which Agents are available
- The user is unhappy with the current Agent’s performance and wants a better alternative

### Core value

- **Lower the barrier**: Users do not need to remember each Agent’s name and capabilities
- **Precise matching**: Intelligent recommendations based on semantic needs, not simple keyword search
- **Smooth handoff**: If no match is found, automatically suggest creating a new Agent (handoff to the create-agent Skill)

## L2: Detailed specification

### Execution flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   需求理解    │ ──→ │   Agent 检索  │ ──→ │   匹配评分    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   引导选择    │ ←── │   结果展示    │ ←── │   候选排序    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Stage 1: Needs understanding

**Trigger conditions** (any one of the following):

- The user says "帮我找一个...", "有没有...", or "谁能帮我..."
- The user describes a task but does not specify a particular Agent
- The user says "有哪些智能体" or "看看都有谁"
- The system detects that the user’s need does not match the current Agent’s capabilities

**Need parsing**:

Extract the following dimensions from the user’s description:

| Dimension | Description | Example |
| --------- | ----------- | ------- |
| `domain`    | Professional domain | law, finance, technology, education |
| `task_type` | Task type | consultation, review, analysis, creation |
| `keywords`  | Keywords | contract, report, code, paper |
| `urgency`   | Urgency | routine / urgent |

### Stage 2: Agent retrieval

**Data source**: Call `ManageAgent(action='list')` to get the list of all registered Agents.

**Tool call**:

```
ManageAgent(action='list')
```

**Returned content**: a compact list where each line contains the following key fields:

- `name` — Agent name
- `id` — unique Agent identifier
- `status` — current status (online/busy/idle/offline)
- `description` — Agent description

> `list` is a read-only query; no user confirmation is required and it is approval-free.

**Filtering rules**:

- By default, show Agents other than offline ones; offline Agents are shown only as a supplement when no better candidate is available
- Exclude internal system Agents (such as DesireCore itself, unless explicitly requested by the user)

### Stage 3: Matching evaluation

Evaluate the match score based on the following dimensions (using LLM semantic understanding, not formula-based calculation):

| Dimension | Description |
| --------- | ----------- |
| Description relevance | Semantic relevance between the Agent’s description / persona and the user’s need |
| Skill match | Correlation between the Agent’s skills and the task type |
| Domain fit | Degree of fit between the Agent’s professional domain and the user’s domain |
| Status availability | The Agent’s current status (online takes priority over offline) |

**Display rules**:

- High match (clearly suitable for the task) → mark as "推荐"
- Partial match (may be helpful) → mark as "可能相关"
- No obvious relevance → do not display

### Stage 4: Candidate ranking

**Ranking rules**:

1. Sort by overall score in descending order
2. If scores are tied, prefer online status
3. Show at most 5 candidates

### Stage 5: Result display

**When there are matching results**:

```
Based on your needs, I recommend the following Agents:

┌─────────────────────────────────────────────────────┐
│ 1. 法律顾问助手                          匹配度: 92% │
│    专注合同审查和法律风险评估                          │
│    技能：合同审查、风险评估、法律研究                   │
│    状态：在线                                        │
├─────────────────────────────────────────────────────┤
│ 2. AI 文书助手                           匹配度: 71% │
│    专业文书撰写和格式优化                              │
│    技能：文书撰写、格式排版、合规检查                   │
│    状态：在线                                        │
├─────────────────────────────────────────────────────┤
│ 3. 数据分析师                            匹配度: 45% │
│    数据分析和可视化报告                                │
│    技能：数据分析、报表生成、趋势预测                   │
│    状态：离线                                        │
└─────────────────────────────────────────────────────┘

Please choose an Agent, or tell me more specific requirements.
```

**When there are no matching results**:

```
No fully matching Agent was found for your needs at the moment.

You can:
1. Try again with a more specific description
2. Create a new specialist Agent (I can help you)
3. Browse all available Agents

What would you like to do?
```

**Browse mode** (when the user asks to view all):

```
Currently available Agents:

Online:
  - 法律顾问助手 — 合同审查和法律风险评估
  - AI 文书助手 — 专业文书撰写和格式优化

Offline:
  - 数据分析师 — 数据分析和可视化报告
  - 翻译助手 — 多语言翻译和本地化

A total of 4 Agents. Do you need detailed information about any one Agent?
```

### Stage 6: Guidance and selection

**Actions after the user makes a choice**:

| User choice | Follow-up action |
| ----------- | ---------------- |
| Chose an Agent | Switch to that Agent’s conversation and pass the user need context |
| Asked for more details | Call `ManageAgent(action='get', id='<agent-id>')` to get details, then show structured information (see below) |
| Unsatisfied with candidates | Guide the user to refine the need or suggest creating a new Agent |
| Chose "create a new one" | Call the create-agent Skill and pass the collected need information |

**Implementation of "learn more"**:

Call `ManageAgent(action='get', id='<agent-id>')` to get details of the specified Agent:

```
ManageAgent(action='get', id='legal-assistant')
```

**Key fields in the returned content**:

- name, description, status
- version
- skill count / tool count
- Git repository status

> `get` is a read-only query; no user confirmation is required and it is approval-free. If the target does not exist, it returns the error "智能体不存在: <id>".

When presenting to the user, show key information in natural language/table format:

```
「法律顾问助手」详细信息

| 字段 | 内容 |
|------|------|
| 描述 | 专注合同审查和法律风险评估 |
| 当前状态 | 在线 |
| 版本 | 1.2.0 |
| 技能 / 工具 | 3 个技能，5 个工具 |
| Git 仓库 | 干净（无未提交变更） |

Need to talk with this Agent?
```

**Context handoff**:

```yaml
context_handoff:
  source_agent: desirecore
  target_agent: legal-assistant
  user_intent: '帮我审查这份合同的风险点'
```

### Collaboration with other Skills

| Collaboration Skill | Collaboration method |
| ------------------- | -------------------- |
| create-agent    | When there is no match, suggest creating a new Agent and pass the user need as initial information |
| task-management | After a successful match, tasks can be created automatically and assigned to the target Agent |

### Error handling

| Error scenario | Handling method |
| -------------- | --------------- |
| Tool call failure | Prompt the error message and suggest trying again later |
| Agent list is empty | Guide the user to create the first Agent |
| User description is too vague | Ask follow-up questions and provide domain options as guidance |
| Target Agent does not exist | When `get` returns "智能体不存在: <id>", fall back to `list` to re-confirm available Agents |
| Recommended Agent has an abnormal status | Mark the status and suggest choosing another online Agent |

### Permission requirements

- Complete Agent retrieval and detail lookup via the built-in tool `ManageAgent`
- Both `list` and `get` are read-only queries; no user confirmation is required, they are approval-free, and carry no risk

### Dependencies

- Built-in tool `ManageAgent` (`action='list'` to retrieve the list, `action='get'` to query details)
