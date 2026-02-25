---
name: create-agent
description: 通过多轮对话收集需求，调用 HTTP API 创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when 用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
version: "2.0.0"
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags: [agent, creation, meta]
metadata:
  author: desirecore
  version: "2.0.0"
  updated_at: "2026-02-21"
---

# create-agent 技能

## L0：一句话摘要

通过自然语言对话收集需求，调用 HTTP API 创建专业化的数字智能体。

## L1：概述与使用场景

### 能力描述

create-agent 是一个**元技能（Meta-Skill）**，赋予 DesireCore 创建其他 Agent 的能力。它通过多轮对话收集用户需求，生成 persona 和 principles 内容，调用 `POST /api/agents` 完成创建。

### 使用场景

- 用户想要一个专业领域的数字助手（如法律顾问、财务分析师）
- 企业需要快速部署定制化的业务 Agent
- 开发者需要基于模板快速创建 Agent 原型

### 核心价值

- **降低门槛**：无需编程知识，用对话就能创建 Agent
- **专业化**：根据领域模板生成合适的 persona 和 principles
- **可治理**：创建的仓库符合 AgentFS v2 规范，支持版本管理

## L2：详细规范

### 对话流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   意图识别    │ ──→ │   需求收集    │ ──→ │   内容生成    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   回执生成    │ ←── │   API 创建   │ ←── │   用户确认    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 阶段 1：意图识别

**触发条件**（任一满足）：
- 用户明确说"创建一个 Agent"或"帮我做一个助手"
- 用户描述需要某领域的专业帮助，且当前 Agent 不具备该能力
- 用户询问"能不能帮我培养一个..."

**输出**：确认用户的创建意图，进入需求收集阶段。

### 阶段 2：需求收集

**必填信息**：

| 字段 | 说明 | 引导问题示例 |
|------|------|------------|
| `name` | 智能体名称 | "你想给这个智能体起什么名字？" |
| `role` | 核心职责 | "它主要负责什么工作？" |
| `target_users` | 目标用户 | "谁会使用这个智能体？" |
| `domain` | 专业领域 | "它需要哪些专业知识？" |

**选填信息**：

| 字段 | 说明 | 默认值 |
|------|------|-------|
| `style` | 沟通风格 | 根据领域模板决定 |
| `boundaries` | 禁区/红线 | 根据领域模板决定 |
| `language` | 主要语言 | 中文 |

**收集策略**：
- 优先通过用户的自然描述推断信息
- 仅追问用户未提及的必填项
- 每轮最多追问 2 个问题

### 阶段 3：内容生成

根据收集的需求，为新 Agent 生成以下内容：

**persona.md 生成规范**：

```markdown
# L0 — 核心身份

你是 {name}，{一句话角色定位}。

# L1 — 行为风格

- {风格特征 1}
- {风格特征 2}
- {风格特征 3}

# L2 — 深层动机

{2-3 句话描述深层价值观和驱动力}
```

**principles.md 生成规范**：

```markdown
# L0 — 基础约束

- {安全红线 1}
- {安全红线 2}

# L1 — 行为边界

- {行为规则 1}
- {行为规则 2}
- {行为规则 3}

# L2 — 治理原则

{2-3 句话描述最高治理原则}
```

**领域匹配参考**：

| 领域关键词 | 推荐风格 | 默认边界 |
|-----------|---------|---------|
| 法律、合同、法务 | 专业、严谨、审慎 | 不提供诉讼代理、不替代正式法律意见 |
| 财务、会计、投资 | 精确、分析性、保守 | 不提供投资建议、不处理真实交易 |
| 代码、开发、架构 | 逻辑、务实、直接 | 不直接访问生产环境、不存储凭证 |
| 通用/其他 | 友好、有帮助 | 通用安全规范 |

### 阶段 4：用户确认

**展示预览**：

```
即将创建智能体：

名称：法律顾问小助手
描述：专注于合同审查和法律风险评估的数字智能体

--- persona.md 预览 ---
# L0 — 核心身份
你是法律顾问小助手，专注于合同审查和法律风险评估...
[完整内容]

--- principles.md 预览 ---
# L0 — 基础约束
- 不提供诉讼代理
[完整内容]
---

确认创建？
[确认] [修改] [取消]
```

### 阶段 5：调用 API 创建

**API 端点**：`POST /api/agents`

**请求体**：

```json
{
  "name": "法律顾问小助手",
  "description": "专注于合同审查和法律风险评估的数字智能体",
  "persona": "# L0 — 核心身份\n\n你是法律顾问小助手...",
  "principles": "# L0 — 基础约束\n\n- 不提供诉讼代理..."
}
```

**可选**：如需指定 slug ID，可根据 name 生成合理的 kebab-case slug（如 "法律顾问" → "legal-advisor"），在请求体中附带 `"id": "<slug>"`。不指定时系统会自动从 name 生成。

**成功响应** (`201 Created`)：

```json
{
  "agentId": "fa-lv-gu-wen-xiao-zhu-shou"
}
```

**验证创建结果**：创建成功后可调用 `GET /api/agents/{agentId}` 确认（agentId 为 slug）。

### 阶段 6：回执生成

**回执报告**：

```
✅ 智能体 "法律顾问小助手" 创建成功

详情：
- Agent Slug: fa-lv-gu-wen-xiao-zhu-shou
- 仓库路径: ~/.desirecore/agents/fa-lv-gu-wen-xiao-zhu-shou
- 已生成文件: agent.json, persona.md, principles.md
- AgentFS 规范: v2（扁平结构）

下一步建议：
- 为它添加技能（通过 update-agent 技能）
- 直接开始对话
```

### AgentFS 知识（创建后的仓库结构）

DesireCore 应理解创建后的 Agent 仓库遵循 AgentFS v2 扁平结构：

```
<agent_id>/
├── agent.json          # 入口配置（name, version, description, engine, skills, tools, mcp_servers）
├── persona.md          # 人格定义（L0 核心身份 / L1 行为风格 / L2 深层动机）
├── principles.md       # 行为原则（L0 基础约束 / L1 行为边界 / L2 治理原则）
├── memory/             # 记忆目录（timeline/topics/pinned/product/lessons）
│   └── _index.md
├── skills/             # 技能目录
│   └── _index.md
├── tools/              # 工具目录
│   └── _index.md
└── heartbeat/          # 心跳配置
    └── HEARTBEAT.md
```

**关键文件职责**：

| 文件 | 职责 | AI Agent 关注点 |
|------|------|----------------|
| `agent.json` | Agent 元数据与运行时配置 | engine 字段决定使用哪个推理引擎 |
| `persona.md` | 人格与沟通风格定义 | L0 不可自动修改（受保护路径） |
| `principles.md` | 行为规则与安全红线 | "绝不做" section 不可自动修改 |
| `memory/` | 对话记忆、知识积累 | 随交互自动积累 |
| `skills/` | Agent 拥有的技能 | 可通过 update-agent 添加 |
| `tools/` | Agent 可用的工具 | MCP Server、脚本工具等 |

### 错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| 400 | 缺少 name 或 ID 格式无效 | 提示用户检查输入 |
| 409 | Agent ID 已存在 | 建议使用其他名称 |
| 500 | 服务器内部错误 | 提示用户稍后再试 |

### 权限要求

- 需要调用 `fetch_api` 工具访问创建 API
- 创建操作需要用户确认

### 依赖

- Agent Service HTTP API（`POST /api/agents`）
