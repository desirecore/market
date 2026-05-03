---
name: 工作流编排
description: >-
  引导 Agent 设计、编辑、测试和执行 Workflow 工作流。Use when
  用户要求创建工作流、编排多步骤自动化流程、设计审批流水线、
  或将重复性多节点任务编排成可复用的 DSL。
version: 1.0.5
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - workflow
  - orchestration
  - automation
  - dsl
metadata:
  author: desirecore
  updated_at: '2026-05-04'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="wf-a" x1="2" y1="4" x2="22"
    y2="20" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#AF52DE"/></linearGradient></defs><circle cx="5"
    cy="5" r="2.5" fill="url(#wf-a)" fill-opacity="0.15" stroke="url(#wf-a)"
    stroke-width="1.5"/><circle cx="19" cy="5" r="2.5" fill="url(#wf-a)"
    fill-opacity="0.15" stroke="url(#wf-a)"
    stroke-width="1.5"/><circle cx="12" cy="12" r="2.5" fill="url(#wf-a)"
    fill-opacity="0.15" stroke="url(#wf-a)"
    stroke-width="1.5"/><circle cx="12" cy="20" r="2.5" fill="#34C759"
    fill-opacity="0.9"/><line x1="7" y1="6.5" x2="10" y2="10.5"
    stroke="url(#wf-a)" stroke-width="1.5" stroke-linecap="round"/><line
    x1="17" y1="6.5" x2="14" y2="10.5" stroke="url(#wf-a)"
    stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="14.5"
    x2="12" y2="17.5" stroke="url(#wf-a)" stroke-width="1.5"
    stroke-linecap="round"/></svg>
  short_desc: 引导设计、编辑、测试和执行多节点自动化工作流
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
requires:
  tools:
    - Write
    - Edit
    - Read
  optional_tools:
    - Bash
---

# workflow 技能

## L0：一句话摘要

引导 Agent 通过 DSL 设计、编辑、校验、测试和执行多节点自动化工作流。

## L1：概述与使用场景

### 能力描述

workflow 是一个**流程型技能（Procedural Skill）**，赋予 Agent 编排多步骤自动化工作流的能力。工作流以 YAML DSL 文件描述，由引擎按拓扑顺序自动执行。

**五种基座节点**：

| 基座 | 用途 | 典型场景 |
|------|------|---------|
| `trigger` | 工作流入口，声明输入参数 | 手动触发、webhook 触发 |
| `code` | 执行代码（JS/Python） | 数据获取、API 调用 |
| `llm` | 单次 LLM 调用（无状态） | 文本生成、数据分析、摘要 |
| `agent` | 调用完整 Agent（有状态） | 需要 Agent 记忆、工具、技能的复杂任务 |
| `human_gate` | 等待用户确认 | 敏感操作审批 |

### 使用场景

- 用户想把重复性多步骤工作编排成自动化流程
- 用户需要多个 Agent 协作完成一个复杂任务
- 用户需要在自动化流程中插入人工审批环节
- 用户想复用和分享已验证的工作流程

### 核心价值

- **可视化编排**：DSL 描述清晰直观，支持画布可视化
- **渐进式构建**：先写骨架再逐步丰富，降低出错概率
- **安全门控**：通过 human_gate 节点在关键环节保留人工决策权
- **可复用**：DSL 文件可存档、版本管理、跨 Agent 共享

## L2：详细规范

### 工作流程 SOP

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. 理解意图   │ ──→ │ 2a. 设计拓扑   │ ──→ │ 2b. 逐节点配置 │ ──→ │  3. 校验 DSL  │
└──────────────┘     │  （节点骨架）   │     │ （config/code）│     └──────────────┘
                     └──────────────┘     └──────────────┘           │
                                                                     ↓
                                           ┌──────────────┐     ┌──────────────┐
                                           │  5. 正式执行   │ ←── │  4. 干跑测试  │
                                           └──────────────┘     └──────────────┘
```

### 阶段 1：理解意图

**触发条件**（任一满足）：
- 用户明确说"创建一个工作流"或"帮我编排一个流程"
- 用户描述一个需要多步骤、多角色协作的任务
- 用户想把手动重复的操作自动化

**收集信息**：

| 信息 | 说明 | 引导问题 |
|------|------|---------|
| 目标 | 工作流要完成什么 | "这个流程最终要产出什么？" |
| 步骤 | 大致有哪些环节 | "你通常是怎么做的？分几步？" |
| 审批 | 哪些环节需要人工确认 | "有哪些步骤需要你亲自过目确认？" |
| Agent | 是否需要调用特定 Agent | "有没有已有的 Agent 可以参与？" |

### 阶段 2：渐进式构建 DSL

**DSL 文件位置**：

```
~/.desirecore/workflows/<wf_id>/workflow.dsl.yaml
```

其中 `wf_id` 使用 `wf_` 前缀 + snake_case，如 `wf_legal_review`、`wf_daily_report`。

**构建策略**：严格分两步——先设计节点拓扑，再逐节点填充配置。**禁止在骨架阶段编写节点的 config 和 code 细节。**

#### 步骤 2a：设计节点拓扑（骨架）

先与用户对齐整体流程设计，确认后使用 Write 工具一次性创建骨架 DSL 文件。骨架用于对齐拓扑，不要求立即通过 `WorkflowValidate`；最终完整 DSL 写入时优先使用 `WorkflowCreate`。

**骨架只包含**：
- 根字段（version、id、name、description、creator）
- 每个节点的 `id`、`base`、`display.name`
- 每个节点的 `outputs`（声明变量名和描述）
- `flow`（start、edges、end）

**骨架不包含**：config 内容（code / system_prompt / task / prompt 等）、inputs 引用。

```yaml
# 骨架示例——只有结构，没有实现细节
version: "1.0"
id: wf_daily_report
name: 每日报告生成
description: 从多个数据源获取数据，生成日报并审批发送
creator: desirecore

nodes:
  - id: trigger
    base: trigger
    display:
      name: 手动触发
    config:
      type: manual
    outputs:
      date:
        type: string
        description: "报告日期"
        required: true

  - id: fetch_data
    base: code
    display:
      name: 获取数据
    config: {}                    # 待步骤 2b 填充
    outputs:
      raw_data: "原始数据"

  - id: analyze
    base: llm
    display:
      name: AI 分析
    config: {}                    # 待步骤 2b 填充
    outputs:
      report: "分析报告"

  - id: review
    base: human_gate
    display:
      name: 人工审阅
    config: {}                    # 待步骤 2b 填充
    outputs:
      decision: "审批决定"
      comment: "审批备注"

  - id: send
    base: code
    display:
      name: 发送报告
    config: {}                    # 待步骤 2b 填充
    outputs:
      status: "发送状态"

flow:
  start: trigger
  edges:
    - { from: trigger, to: fetch_data }
    - { from: fetch_data, to: analyze }
    - { from: analyze, to: review }
    - { from: review, to: send }
  end: [send]
```

骨架创建后，向用户确认节点设计和流程是否正确，再进入步骤 2b。

#### 步骤 2b：逐节点填充配置

按拓扑顺序（从 trigger 开始，沿 edges 方向）逐个节点填充 config 和 inputs。每完成一个节点使用 Edit 工具写入，**不要一次性填充所有节点**。

**每个节点填充内容**：
1. `inputs` — 引用上游节点的输出（`{{nodeId.outputKey}}`）
2. `config` — 该基座类型的具体配置：
   - **code 节点**：编写 `runtime` 和 `code`（完整的可执行代码）
   - **llm 节点**：编写 `system_prompt`、选择 `model` / `provider`、设置 `temperature` 等参数
   - **agent 节点**：指定 `agent_id` 和编写 `task` 描述
   - **human_gate 节点**：编写审批 `prompt`（含 `{{}}` 插值）

**逐节点填充顺序示例**（以上方骨架为例）：

```
1. fetch_data  — 编写获取数据的 JS/Python 代码
2. analyze     — 编写 system_prompt，选择模型，配置 inputs 引用 fetch_data 输出
3. review      — 编写审批提示词，配置 inputs 引用 analyze 输出
4. send        — 编写发送逻辑的代码，配置 inputs 引用 review 输出
```

填充完所有节点后进入阶段 3 校验。

### DSL 编写规范

#### 根结构

```yaml
version: "1.0"                    # 固定值
id: wf_<snake_case_name>          # 必须以 wf_ 前缀开头
name: 工作流显示名称               # 人类可读名称
description: 工作流用途描述         # 可选，说明适用场景
creator: <agent_id>               # 创建此工作流的 Agent ID

nodes:                            # 节点列表（至少 1 个）
  - id: ...
    base: ...
    ...

flow:                             # 流程控制
  start: <起始节点 id>
  edges:
    - { from: <节点 id>, to: <节点 id> }
  end: [<终止节点 id>]
```

#### code 节点配置

code 节点执行**内联代码**（JS 或 Python），通过 `inputs` 对象访问上游数据，通过 `return` 返回结果。

```yaml
- id: format_data
  base: code
  display:
    name: 格式化数据
  config:
    runtime: nodejs                  # nodejs 或 python
    timeout_ms: 30000                # 超时毫秒数（可选，默认 30000）
    code: |
      // inputs 对象包含所有上游传入的数据
      const data = JSON.parse(inputs.raw_data)
      const formatted = data.map(item => ({
        title: item.title.trim(),
        date: new Date(item.pubDate).toISOString().slice(0, 10),
      }))
      return { formatted: JSON.stringify(formatted) }
  inputs:
    raw_data: "{{fetch_node.result}}"   # 引用上游节点 fetch_node 的 result 输出
  outputs:
    formatted: "格式化后的数据"
```

**config 字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `runtime` | 是 | `nodejs` 或 `python` |
| `code` | 是 | 内联代码。JS 通过 `inputs` 对象访问输入，`return` 返回输出对象。Python 同理。 |
| `timeout_ms` | 否 | 执行超时（默认 30000ms） |

**JS 代码注意事项**：
- 代码在 `new Function('inputs', ...)` 中执行，支持 `async/await` 和 `fetch`
- **不支持 `require()`**，不能导入 Node.js 模块
- 通过 `inputs.xxx` 访问输入数据
- 必须 `return` 一个对象，其 key 对应 `outputs` 中声明的变量名

**Python 代码注意事项**：
- 通过 `inputs['xxx']` 访问输入数据
- 必须 `return` 一个字典

#### llm 节点配置

llm 节点执行**单次无状态 LLM 调用**，适用于文本生成、数据分析、摘要等场景。与 agent 节点的区别是不涉及 Agent 的记忆、工具和技能。

```yaml
- id: summarize
  base: llm
  display:
    name: AI 摘要
  config:
    provider: anthropic              # 供应商名称（可选，精确匹配）
    model: claude-sonnet-4-6         # 模型（可选，不填使用默认）
    system_prompt: "你是摘要助手"     # 系统提示词
    max_tokens: 2048                 # 最大 token
    temperature: 0.3                 # 温度（可选）
    reasoning: medium                # 思维链级别（可选）
  inputs:
    data: "{{fetch_data.result}}"
  outputs:
    summary: "摘要文本"
```

**config 字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `system_prompt` | 是 | 系统提示词，定义 LLM 的角色和行为 |
| `provider` | 否 | 供应商名称（如 `anthropic`、`openai`），精确匹配已配置的供应商。不填则由系统自动匹配 |
| `model` | 否 | 指定模型，不填使用默认模型 |
| `max_tokens` | 否 | 最大输出 token 数 |
| `temperature` | 否 | 温度参数（0-2），控制输出随机性 |
| `reasoning` | 否 | 思维链级别：`low` / `medium` / `high`。开启后模型先推理再回答，适合复杂分析任务 |
| `output_schema` | 否 | JSON Schema 对象。设置后 LLM 将尝试返回符合 Schema 的结构化 JSON |

#### agent 节点配置

agent 节点调用**完整的 Agent**（有状态），适用于需要 Agent 的专业知识、记忆、工具或技能的复杂任务。

```yaml
- id: legal_review
  base: agent
  display:
    name: 法律审核
  config:
    agent_id: legal-advisor          # 必填：目标 Agent ID
    task: "审核以下内容：{{summarize.summary}}"  # 任务描述
  inputs:
    content: "{{summarize.summary}}"
  outputs:
    review: "审核意见"
```

**config 字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `agent_id` | 是 | 目标 Agent 的 ID |
| `task` | 是 | 交给 Agent 的任务描述，支持 `{{nodeId.outputKey}}`、`{{trigger.key}}`、`{{secrets.keyName}}` 插值 |

#### human_gate 节点配置

```yaml
- id: approval
  base: human_gate
  display:
    name: 人工审批
  config:
    prompt: |
      请审阅以下内容并决定是否通过：
      审阅意见：{{draft_review.review_result}}
      风险等级：{{draft_review.risk_level}}
    options:
      - { label: "批准", value: approve }
      - { label: "拒绝", value: reject }
      - { label: "修改后通过", value: modify }
  inputs:
    review_result: "{{draft_review.review_result}}"
    risk_level: "{{draft_review.risk_level}}"
  outputs:
    decision: "审批决定（approve/reject/modify）"
    comment: "审批备注"
```

#### llm vs agent 选择指南

| 场景 | 推荐基座 | 理由 |
|------|---------|------|
| 文本摘要、翻译、格式转换 | `llm` | 单次调用，不需要 Agent 上下文 |
| 数据分析、信息提取 | `llm` | 无状态处理即可完成 |
| 需要专业知识的审核 | `agent` | 需要 Agent 的领域知识和记忆 |
| 需要调用外部工具 | `agent` | 需要 Agent 的工具能力 |
| 多轮推理、复杂决策 | `agent` | 需要 Agent 的完整推理链 |

**简单判断**：如果任务可以用一段 system prompt + 一次输入完成，用 `llm`；如果任务需要 Agent 的记忆、工具或技能，用 `agent`。

#### trigger 节点

每个工作流**必须有且仅有一个** trigger 节点，作为工作流入口。`flow.start` 必须指向 trigger 节点。

**规则**：
- trigger 节点**无 inputs**
- trigger 节点的 outputs 使用结构化格式（`type` / `description` / `required` / `default`），声明工作流接受的输入参数
- `config.type` 指定触发方式：`manual`（手动触发）或 `webhook`（外部触发）

```yaml
- id: trigger
  base: trigger
  display:
    name: 手动触发
    icon: ▶️
  config:
    type: manual                        # manual | webhook
  outputs:
    param_name:
      type: string                      # 参数类型：string / number / boolean / object / array
      description: "参数描述"
      required: true                    # 是否必填
      default: "默认值"                  # 可选，未传入时的默认值
```

**示例**——带多个参数的 trigger：

```yaml
- id: trigger
  base: trigger
  display:
    name: 文档摘要触发
    icon: ▶️
  config:
    type: manual
  outputs:
    filePath:
      type: string
      description: "要摘要的文档路径"
      required: true
    language:
      type: string
      description: "摘要输出语言"
      required: false
      default: "zh-CN"
```

下游节点通过 `{{trigger.paramName}}` 引用 trigger 输出的参数值。

#### inputs 格式规范

inputs 使用**对象映射格式**——key 为本节点的变量名，value 为数据来源引用：

```yaml
# 引用其他节点的输出
inputs:
  varName: "{{nodeId.outputKey}}"

# 引用触发参数
inputs:
  query: "{{trigger.userQuery}}"

# 引用用户级 secret
inputs:
  api_key: "{{secrets.email_api_key}}"

# 多个输入
inputs:
  title: "{{extract.title}}"
  body: "{{extract.body}}"
  metadata: "{{trigger.metadata}}"
```

**禁止使用数组格式**：

```yaml
# 错误！不要用数组
inputs:
  - name: varName
    source: nodeId.outputKey
```

#### outputs 格式规范

outputs 使用**对象映射格式**——key 为输出变量名，value 为描述文本：

```yaml
outputs:
  result: "处理后的结果数据"
  summary: "结果摘要"
```

#### flow 定义

```yaml
flow:
  start: first_node              # 起始节点 ID
  edges:                         # 边列表（定义执行顺序）
    - { from: first_node, to: second_node }
    - { from: second_node, to: third_node }
    - from: third_node           # 条件分支（可选）
      to: branch_a
      condition: "risk_level == 'high'"
  end: [final_node]              # 终止节点列表
```

#### 变量引用体系

DSL 中所有动态值统一使用 `{{}}` 模板语法引用：

| 语法 | 来源 | 示例 |
|------|------|------|
| `{{nodeId.outputKey}}` | 前置节点输出 | `{{summarize.summary}}` |
| `{{trigger.key}}` | 触发时传入的参数 | `{{trigger.filePath}}` |
| `{{secrets.keyName}}` | 用户级 secret | `{{secrets.dingtalk_token}}` |

**适用位置**：`inputs` 的值、`config.prompt` 中的插值均使用此语法。

#### Secrets 引用

工作流可通过 `{{secrets.keyName}}` 引用用户预配置的密钥，用于 API 调用等场景。

- Secrets 由用户在 `~/.desirecore/config/secrets.json` 中预配置
- 引擎在运行时自动解析 `{{secrets.*}}`，将其替换为实际值
- Secrets 仅在执行阶段解析，校验和干跑阶段不会暴露实际值

```yaml
# 在 inputs 中引用 secret
inputs:
  api_key: "{{secrets.email_api_key}}"
  webhook_url: "{{secrets.dingtalk_webhook}}"

# 在 config.prompt 中引用 secret（不推荐，仅特殊场景）
config:
  prompt: "使用 token {{secrets.github_token}} 访问仓库"
```

### 阶段 3：校验 DSL

使用 `WorkflowValidate` 工具校验 DSL 文件的结构和引用完整性。

**调用方式**：

```
工具：WorkflowValidate
参数：
  path: ~/.desirecore/workflows/<wf_id>/workflow.dsl.yaml
```

**校验内容**：
- YAML 语法正确性
- JSON Schema 合规性（必填字段、类型、格式）
- 节点 ID 唯一性
- 边的引用有效性（from/to 均指向已存在的节点）
- 起始节点和终止节点存在
- 无环检测（DAG 校验）
- inputs 引用的上游节点和输出字段存在

**校验通过** → 进入阶段 4
**校验失败** → 根据错误信息用 Edit 工具修复，重新校验

### 阶段 4：干跑测试

使用 `WorkflowTest` 工具进行模拟执行（dry-run），不实际调用 Agent 或执行代码。

**调用方式**：

```
工具：WorkflowTest
参数：
  path: ~/.desirecore/workflows/<wf_id>/workflow.dsl.yaml
  params:                      # 可选，用于模拟 trigger 参数
    filePath: /path/to/input.md
```

**测试内容**：
- 验证拓扑排序是否成功
- 模拟数据在节点间的流转路径
- 检查所有 inputs 引用在运行时是否可解析
- 输出执行计划预览（节点执行顺序）

**测试通过** → 向用户确认是否正式执行
**测试失败** → 根据错误信息修复，重新测试

### 阶段 5：正式执行

使用 `WorkflowRun` 工具启动工作流。

**调用方式**：

```
工具：WorkflowRun
参数：
  path: ~/.desirecore/workflows/<wf_id>/workflow.dsl.yaml
  params:                      # 可选，作为 {{trigger.key}} 上下文传入
    filePath: /path/to/input.md
```

**执行过程**：
- 引擎按拓扑顺序逐节点执行
- 实时通过 SSE 推送节点状态变更事件
- 遇到 human_gate 节点时暂停，等待用户审批
- 所有终止节点完成后，返回最终结果

**执行完成后**：
- 向用户展示执行结果摘要
- 如有失败节点，说明失败原因和建议修复方式

### 注意事项

1. **workflow_id 命名**：必须以 `wf_` 前缀开头，使用 snake_case，如 `wf_contract_review`
2. **严格分步构建**：步骤 2a 只写节点拓扑骨架（不含 config/code），确认后步骤 2b 按拓扑顺序逐节点填充配置，禁止一次性写完所有细节
3. **输入输出格式**：inputs 和 outputs 必须使用对象映射格式（`{ key: value }`），不要用数组
4. **变量插值**：inputs、llm/agent/human_gate 的 prompt / system_prompt / task 支持 `{{nodeId.outputKey}}`、`{{trigger.key}}`、`{{secrets.keyName}}`
5. **校验先行**：正式执行前务必先校验再干跑测试，减少运行时错误
6. **人工门控**：涉及重要决策（如发布、付款、删除）的步骤，建议使用 human_gate 节点

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| YAML 语法错误 | 检查缩进和格式，用 Edit 工具修正 |
| 校验失败 | 根据 WorkflowValidate 的错误详情逐项修复 |
| 节点引用不存在 | 检查 inputs 中引用的 nodeId.outputKey 是否拼写正确 |
| 干跑测试失败 | 检查拓扑排序和数据流转路径 |
| 执行超时 | 检查是否有 agent 节点 prompt 过于复杂 |
| human_gate 被拒绝 | 工作流中止，向用户说明中止原因和已完成的步骤 |

### 背景知识

> AgentFS 仓库结构、排查要点与受保护路径详见 `_agentfs-background.md` 和 `_protected-paths.yaml`。

### 依赖

- `WorkflowValidate` 内置工具 — 校验 DSL 结构
- `WorkflowTest` 内置工具 — 干跑测试
- `WorkflowCreate` 内置工具 — 校验并写入全局工作流目录
- `WorkflowRun` 内置工具 — 正式执行工作流
- Write / Edit / Read 工具 — 创建和编辑 DSL 文件
- Agent Service Workflow 引擎（`lib/workflow-service/`）
