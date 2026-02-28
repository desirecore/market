---
name: 创建智能体
description: >-
  通过多轮对话收集需求，调用 HTTP API 创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when
  用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
version: 2.2.0
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - creation
  - meta
metadata:
  author: desirecore
  updated_at: '2026-02-28'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ca-a" x1="2" y1="7" x2="16"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#ca-a)" fill-opacity="0.15" stroke="url(#ca-a)"
    stroke-width="1.5"/><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
    fill="url(#ca-a)" fill-opacity="0.1" stroke="url(#ca-a)"
    stroke-width="1.5"/><circle cx="19" cy="11" r="4" fill="#34C759"
    fill-opacity="0.15"/><line x1="19" y1="8.5" x2="19" y2="13.5"
    stroke="#34C759" stroke-width="2" stroke-linecap="round"/><line x1="16.5"
    y1="11" x2="21.5" y2="11" stroke="#34C759" stroke-width="2"
    stroke-linecap="round"/></svg>
  short_desc: 通过自然语言对话收集需求，一键创建专业化数字智能体
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
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

根据收集的需求，组装结构化的 persona 和 principles 数据。**不要输出原始 markdown**，而是按字段整理后向用户展示。

**Persona 字段**（所有字段均可选，未收集到的由系统自动补全）：

| 层级 | 字段 | 说明 |
|------|------|------|
| L0 | — | 一句话核心身份 |
| L1 | `role` | 角色定位 |
| L1 | `personality` | 性格特征标签 |
| L1 | `communication_style` | 沟通风格 |
| L2 | — | 专业领域、核心价值观、决策偏好等（free-form） |

**Principles 字段**（同样全部可选）：

| 层级 | 字段 | 说明 |
|------|------|------|
| L0 | — | 一句话最高原则 |
| L1 | `must_do` | 必须做的事项 |
| L1 | `must_not` | 绝不做的事项（安全红线） |
| L1 | `priority` | 优先级排序 |
| L2 | — | 治理原则、升级规则等（free-form） |

**领域匹配参考**：

| 领域关键词 | 推荐 personality | 默认 must_not |
|-----------|-----------------|--------------|
| 法律、合同、法务 | 专业、严谨、审慎 | 不提供诉讼代理、不替代正式法律意见 |
| 财务、会计、投资 | 精确、分析性、保守 | 不提供投资建议、不处理真实交易 |
| 代码、开发、架构 | 逻辑、务实、直接 | 不直接访问生产环境、不存储凭证 |
| 通用/其他 | 友好、有帮助 | 通用安全规范 |

### 阶段 4：用户确认

向用户展示预览时，以自然语言/表格形式呈现各字段，**不要展示原始 markdown 源码**：

> 即将创建智能体：
>
> **名称**：法律顾问小助手
> **描述**：专注于合同审查和法律风险评估的数字智能体
>
> ---
>
> **人格设定**
>
> | 字段 | 内容 |
> |------|------|
> | 核心身份 | 你是法律顾问小助手，专注于合同审查和法律风险评估 |
> | 角色定位 | 专注于合同审查和法律风险评估的数字法律顾问 |
> | 性格特征 | 专业、严谨、审慎 |
> | 沟通风格 | 准确使用法律术语，同时提供通俗解释 |
>
> **行为原则**
>
> | 字段 | 内容 |
> |------|------|
> | 最高原则 | 以用户利益为最高优先级，不替代正式法律意见 |
> | 必须做 | 准确引用法律条文、标注不确定性、建议咨询专业律师 |
> | 绝不做 | 提供诉讼代理、替代正式法律意见、泄露用户咨询内容 |
> | 优先级 | 用户安全 > 准确性 > 效率 |
>
> ---
>
> 确认创建？（确认 / 修改 / 取消）

### 阶段 5：调用 API 创建

**API 端点**：`POST /api/agents`

**请求体**（结构化格式）：

```json
{
  "name": "法律顾问小助手",
  "description": "专注于合同审查和法律风险评估的数字智能体",
  "persona": {
    "L0": "你是法律顾问小助手，专注于合同审查和法律风险评估的数字智能体。",
    "L1": {
      "role": "专注于合同审查和法律风险评估的数字法律顾问",
      "personality": ["专业", "严谨", "审慎"],
      "communication_style": "准确使用法律术语，同时提供通俗解释"
    }
  },
  "principles": {
    "L0": "以用户利益为最高优先级，不替代正式法律意见。",
    "L1": {
      "must_do": ["准确引用法律条文", "标注不确定性", "建议咨询专业律师"],
      "must_not": ["提供诉讼代理", "替代正式法律意见", "泄露用户法律咨询内容"],
      "priority": "用户安全 > 准确性 > 效率"
    }
  }
}
```

**最简创建**（只需 name，其余全部自动生成）：

```json
{ "name": "我的助手" }
```

**基础创建**（name + description，description 自动填充 persona L0）：

```json
{ "name": "法律顾问", "description": "专注合同审查" }
```

所有未提供的字段由系统自动补全为合理默认值。`persona` 和 `principles` 也支持传入原始 markdown 字符串（向后兼容）。

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

创建成功后，以用户友好的方式呈现回执（不要暴露内部路径或技术细节）：

> 智能体「法律顾问小助手」已创建成功！
>
> **下一步你可以**：
> - 直接开始对话
> - 为它添加技能，让它更强大
> - 调整它的性格或行为规则

### 背景知识：AgentFS 仓库结构

> 以下信息仅供 Agent 内部理解，**不要向用户展示**。
> 用于创建后的验证、排查问题、以及后续精细化维护。

创建后的 Agent 仓库遵循 AgentFS v2 扁平结构：

```
<agent_id>/
├── agent.json        # 元数据与运行时配置
├── persona.md        # 人格定义（L0/L1/L2）
├── principles.md     # 行为原则（L0/L1/L2）
├── memory/           # 记忆目录
├── skills/           # 技能目录
├── tools/            # 工具目录
└── heartbeat/        # 心跳配置
```

**排查要点**：

| 文件 | 验证方式 | 常见问题 |
|------|---------|---------|
| `agent.json` | `GET /api/agents/:id` 返回完整配置 | engine 字段缺失导致无法启动 |
| `persona.md` | `GET /api/agents/:id/persona` 返回结构化数据 | L0 为空则 Agent 无身份摘要 |
| `principles.md` | `GET /api/agents/:id/principles` 返回结构化数据 | must_not 为空则无安全红线 |
| `memory/` | 目录存在即可 | `_policy.json` 缺失会使用默认策略 |

**受保护路径**（不可自动修改）：
- `persona.md` L0 section — 核心身份
- `principles.md` "绝不做" section — 安全红线

### 错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| 400 | 缺少 name 或 ID 格式无效 | 提示用户检查输入 |
| 409 | Agent ID 已存在 | 建议使用其他名称 |
| 500 | 服务器内部错误 | 提示用户稍后再试 |

### 权限要求

- 建议优先通过 `Bash` 工具调用 curl 访问 Agent Service HTTP API 完成操作
- API 基础地址已注入到 system prompt 的「本机 API」小节，直接引用即可
- 创建操作需要用户确认

### 依赖

- Agent Service HTTP API（`POST /api/agents`）
- System prompt 中的本机 API 地址声明
