---
name: discover-agent
description: 根据用户需求推荐最匹配的智能体，展示候选列表并引导选择。Use when 用户描述需求但不确定该找哪个智能体帮忙，或想浏览可用的智能体。
version: 2.5.2
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
  updated_at: '2026-02-28'
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
      source_hash: sha256:28ecd07724adda9a
      translated_by: human
    en-US:
      name: Discover Agent
      short_desc: Intelligently recommend the best-matching Agent based on the user's needs and guide a quick selection
      description: >-
        Recommend the best-matching Agent based on the user's needs, present a candidate list, and guide the user's selection. Use when the user describes a need but is unsure which Agent to ask, or wants to browse available Agents.
      body: ./SKILL.md
      source_hash: sha256:28ecd07724adda9a
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
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
---

# discover-agent skill

## L0: One-Sentence Summary

Match and recommend the most suitable registered Agent based on the user's described needs.

## L1: Overview and Use Cases

### Capability Description

discover-agent is a **Procedural Skill** that gives DesireCore the ability to discover and recommend a suitable Agent for the user. It understands the user's described needs, performs multi-dimensional matching across the registered Agent list, and presents a candidate list for the user to choose from.

### Use Cases

- The user describes a need but doesn't know which Agent to ask for help
- The user wants to browse currently available Agents and their capabilities
- The user needs to find the best specialist assistant for a specific task
- A new user trying the system for the first time needs to learn which Agents are available

### Core Value

- **Lower the barrier**: Users don't have to remember each Agent's name and capabilities
- **Precise matching**: Smart recommendations based on the semantics of the need, not simple keyword search
- **Smooth handoff**: When there's no match, automatically suggest creating a new Agent (handing off to the create-agent skill)

## L2: Detailed Specification

### Execution Flow

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

### Stage 1: Need Understanding

**Trigger conditions** (any one is sufficient):

- The user says "find me a...", "is there a...", "who can help me..."
- The user describes a task without specifying a particular Agent
- The user says "what Agents are there?", "show me who's available"
- The system detects that the user's need does not match the current Agent's capabilities

**Need parsing**:

Extract the following dimensions from the user's description:

| Dimension   | Description       | Examples                                |
| ----------- | ----------------- | --------------------------------------- |
| `domain`    | Specialty domain  | Legal, finance, technology, education   |
| `task_type` | Task type         | Consultation, review, analysis, writing |
| `keywords`  | Keywords          | Contract, report, code, paper           |
| `urgency`   | Urgency level     | Routine / urgent                        |

### Stage 2: Agent Retrieval

**Data source**: Call `GET /api/agents` to fetch the list of all registered Agents.

**API call**:

```bash
GET /api/agents
```

**Key fields in the returned data**:

- `id` — Unique Agent identifier
- `name` — Agent name
- `description` — Agent description
- `skills` — Skill list
- `status` — Current status (online/offline/busy)

**Filter rules**:

- By default, show only Agents with `status: online` or `status: offline`
- Exclude system-internal Agents (e.g. DesireCore itself, unless the user explicitly requests them)

### Stage 3: Match Evaluation

Comprehensively judge match degree based on the following dimensions (using LLM semantic understanding rather than formula-based computation):

| Dimension              | Description                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| Description relevance  | Semantic relevance between Agent description / persona and user's need   |
| Skill match            | Relevance of the Agent's skills to the task type                         |
| Domain fit             | Fit between the Agent's specialty domain and the user's need domain      |
| Status availability    | Agent's current status (online preferred over offline)                   |

**Display rules**:

- Highly matched (clearly suited to the task) → tag as "Recommended"
- Partial match (may help) → tag as "Possibly relevant"
- No clear relation → do not display

### Stage 4: Candidate Ranking

**Ranking rules**:

1. Sort by overall score in descending order
2. On ties, online status takes precedence
3. Show at most 5 candidates

### Stage 5: Result Display

**When matches are found**:

```
根据你的需求，我推荐以下智能体：

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

请选择一个智能体，或告诉我更具体的需求。
```

**When no matches are found**:

```
目前没有找到完全匹配你需求的智能体。

你可以：
1. 用更具体的描述再试一次
2. 创建一个新的专业智能体（我可以帮你）
3. 浏览所有可用的智能体

你想怎么做？
```

**Browse mode** (when the user asks to view all):

```
当前可用的智能体：

在线：
  - 法律顾问助手 — 合同审查和法律风险评估
  - AI 文书助手 — 专业文书撰写和格式优化

离线：
  - 数据分析师 — 数据分析和可视化报告
  - 翻译助手 — 多语言翻译和本地化

共 4 个智能体。需要了解某个智能体的详细信息吗？
```

### Stage 6: Guided Selection

**Actions after the user selects**:

| User Choice              | Follow-up Action                                                   |
| ------------------------ | ------------------------------------------------------------------ |
| Selected an Agent        | Switch to a conversation with that Agent and pass the need context |
| Asked to learn more      | Call `GET /api/agents/:id` for details and present structured info (see below) |
| Not satisfied with candidates | Guide the user to refine the need or suggest creating a new Agent |
| Chose "create new"       | Invoke the create-agent skill, passing the need info already collected |

**Implementation of "learn more"**:

Call `GET /api/agents/:id` for details, and optionally call structured endpoints for persona/principles:

```bash
# 获取基本信息
GET /api/agents/{agentId}
# 返回: { id, name, description, skillsCount, toolsCount, status, config, persona, principles }

# 获取结构化 persona（可选，用于展示更丰富的信息）
GET /api/agents/{agentId}/persona
# 返回: { L0, L1: { role, personality, communication_style }, L2 }
```

When presenting to the user, render key information in natural language / table form:

```
「法律顾问助手」详细信息

| 字段 | 内容 |
|------|------|
| 角色定位 | 专注合同审查和法律风险评估 |
| 性格特征 | 专业、严谨、审慎 |
| 技能数量 | 3 个 |
| 当前状态 | 在线 |

需要与这个智能体对话吗？
```

**Context handoff on switch**:

```yaml
context_handoff:
  source_agent: desirecore
  target_agent: legal-assistant
  user_intent: '帮我审查这份合同的风险点'
```

### Collaboration with Other Skills

| Collaborating Skill | How It Collaborates                                         |
| ------------------- | ----------------------------------------------------------- |
| create-agent        | When there's no match, suggest creating a new Agent and pass the user's need as initial info |
| task-management     | After a successful match, optionally auto-create a task and assign it to the target Agent |

### Error Handling

| Error Scenario               | Handling                                                  |
| ---------------------------- | --------------------------------------------------------- |
| API call fails               | Indicate a network error and suggest retrying later       |
| Agent list is empty          | Guide the user to create their first Agent                |
| User description too vague   | Ask follow-up questions and offer domain options to guide |
| Recommended Agent has bad status | Mark the status and suggest selecting another online Agent |

### Permission Requirements

- Prefer accessing the Agent Service HTTP API via the `Bash` tool with curl
- The API base URL is already injected into the "Local API" section of the system prompt; reference it directly
- Read-only operations; no risk

### Dependencies

- Agent Service HTTP API (`GET /api/agents`)
- The local API URL declaration in the system prompt
