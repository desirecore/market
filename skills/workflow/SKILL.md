---
name: workflow
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
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 工作流编排
      short_desc: 引导设计、编辑、测试和执行多节点自动化工作流
      description: >-
        引导 Agent 设计、编辑、测试和执行 Workflow 工作流。Use when 用户要求创建工作流、编排多步骤自动化流程、设计审批流水线、 或将重复性多节点任务编排成可复用的 DSL。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:aa197c62ae8a33d7
      translated_by: human
    en-US:
      name: Workflow Orchestration
      short_desc: Guide the design, editing, testing, and execution of multi-node automated workflows
      description: >-
        Guides the Agent to design, edit, test, and execute Workflow workflows. Use when the user asks to create a workflow, orchestrate multi-step automation, design an approval pipeline, or turn repetitive multi-node tasks into a reusable DSL.
      body: ./SKILL.md
      source_hash: sha256:aa197c62ae8a33d7
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-04'
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

# workflow Skill

## L0: One-line Summary

Guides the Agent to design, edit, validate, test, and execute multi-node automated workflows via a DSL.

## L1: Overview and Use Cases

### Capability Description

workflow is a **Procedural Skill** that empowers the Agent to orchestrate multi-step automated workflows. Workflows are described by a YAML DSL file and are automatically executed by the engine in topological order.

**Five base node types**:

| Base | Purpose | Typical Scenario |
|------|---------|------------------|
| `trigger` | Workflow entry point, declares input parameters | Manual trigger, webhook trigger |
| `code` | Executes code (JS/Python) | Data fetching, API calls |
| `llm` | Single LLM call (stateless) | Text generation, data analysis, summarization |
| `agent` | Invokes a full Agent (stateful) | Complex tasks requiring Agent memory, tools, and skills |
| `human_gate` | Waits for user confirmation | Approval of sensitive operations |

### Use Cases

- The user wants to orchestrate repetitive multi-step work into an automated process
- The user needs multiple Agents to collaborate on a complex task
- The user needs to insert manual approval steps into an automated process
- The user wants to reuse and share validated workflows

### Core Value

- **Visual orchestration**: The DSL description is clear and intuitive, with canvas visualization support
- **Progressive construction**: Write the skeleton first and gradually enrich it, reducing the chance of errors
- **Safety gating**: Use human_gate nodes to retain human decision-making authority at critical steps
- **Reusability**: DSL files can be archived, version-controlled, and shared across Agents

## L2: Detailed Specification

### Workflow SOP

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Understand│ ──→ │ 2a. Design    │ ──→ │ 2b. Configure │ ──→ │ 3. Validate  │
│    intent    │     │    topology   │     │    each node  │     │    DSL       │
└──────────────┘     │  (skeleton)   │     │ (config/code) │     └──────────────┘
                     └──────────────┘     └──────────────┘           │
                                                                     ↓
                                           ┌──────────────┐     ┌──────────────┐
                                           │ 5. Real run  │ ←── │ 4. Dry-run   │
                                           └──────────────┘     │    testing   │
                                                                └──────────────┘
```

### Phase 1: Understand Intent

**Trigger conditions** (any one is sufficient):
- The user explicitly says "create a workflow" or "help me orchestrate a process"
- The user describes a task that requires multi-step, multi-role collaboration
- The user wants to automate manual repetitive operations

**Information to collect**:

| Information | Description | Guiding Question |
|-------------|-------------|------------------|
| Goal | What the workflow should accomplish | "What is the final output of this process?" |
| Steps | Roughly which stages are involved | "How do you usually do it? How many steps?" |
| Approval | Which steps require manual confirmation | "Which steps require you to personally review and confirm?" |
| Agent | Whether a specific Agent needs to be invoked | "Are there existing Agents that can participate?" |

### Phase 2: Progressive DSL Construction

**DSL file location**:

```
${DESIRECORE_ROOT}/workflows/<wf_id>/workflow.dsl.yaml
```

Where `wf_id` uses a `wf_` prefix + snake_case, e.g. `wf_legal_review`, `wf_daily_report`.

**Construction strategy**: Strictly two steps — first design the node topology, then fill in the configuration node by node. **Do not write node config or code details during the skeleton phase.**

#### Step 2a: Design Node Topology (Skeleton)

First align with the user on the overall process design. After confirmation, use the Write tool to create the skeleton DSL file in one shot. The skeleton is for aligning topology and is not required to immediately pass `WorkflowValidate`; when writing the final complete DSL, prefer using `WorkflowCreate`.

**The skeleton contains only**:
- Root fields (version, id, name, description, creator)
- Each node's `id`, `base`, `display.name`
- Each node's `outputs` (declaring variable names and descriptions)
- `flow` (start, edges, end)

**The skeleton does not contain**: config content (code / system_prompt / task / prompt, etc.), inputs references.

```yaml
# Skeleton example — only structure, no implementation details
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
    config: {}                    # To be filled in step 2b
    outputs:
      raw_data: "原始数据"

  - id: analyze
    base: llm
    display:
      name: AI 分析
    config: {}                    # To be filled in step 2b
    outputs:
      report: "分析报告"

  - id: review
    base: human_gate
    display:
      name: 人工审阅
    config: {}                    # To be filled in step 2b
    outputs:
      decision: "审批决定"
      comment: "审批备注"

  - id: send
    base: code
    display:
      name: 发送报告
    config: {}                    # To be filled in step 2b
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

After creating the skeleton, confirm with the user that the node design and process are correct, then proceed to step 2b.

#### Step 2b: Fill Node Configurations One by One

In topological order (starting from trigger and following the edges direction), fill in `config` and `inputs` for each node one at a time. Use the Edit tool to write each completed node — **do not fill in all nodes at once**.

**Content to fill in for each node**:
1. `inputs` — references to upstream node outputs (`{{nodeId.outputKey}}`)
2. `config` — the specific configuration for that base type:
   - **code node**: write `runtime` and `code` (complete executable code)
   - **llm node**: write `system_prompt`, choose `model` / `provider`, set parameters such as `temperature`
   - **agent node**: specify `agent_id` and write the `task` description
   - **human_gate node**: write the approval `prompt` (with `{{}}` interpolation)

**Example fill order, node by node** (using the skeleton above):

```
1. fetch_data  — write JS/Python code to fetch data
2. analyze     — write system_prompt, choose model, configure inputs to reference fetch_data outputs
3. review      — write the approval prompt, configure inputs to reference analyze outputs
4. send        — write the sending logic code, configure inputs to reference review outputs
```

After all nodes are filled in, proceed to phase 3 validation.

### DSL Authoring Specification

#### Root Structure

```yaml
version: "1.0"                    # Fixed value
id: wf_<snake_case_name>          # Must start with the wf_ prefix
name: 工作流显示名称               # Human-readable name
description: 工作流用途描述         # Optional, describing the applicable scenario
creator: <agent_id>               # ID of the Agent that created this workflow

nodes:                            # Node list (at least 1)
  - id: ...
    base: ...
    ...

flow:                             # Flow control
  start: <starting node id>
  edges:
    - { from: <node id>, to: <node id> }
  end: [<ending node id>]
```

#### code Node Configuration

A code node executes **inline code** (JS or Python), accesses upstream data via the `inputs` object, and returns results via `return`.

```yaml
- id: format_data
  base: code
  display:
    name: 格式化数据
  config:
    runtime: nodejs                  # nodejs or python
    timeout_ms: 30000                # Timeout in milliseconds (optional, default 30000)
    code: |
      // The inputs object contains all data passed in from upstream
      const data = JSON.parse(inputs.raw_data)
      const formatted = data.map(item => ({
        title: item.title.trim(),
        date: new Date(item.pubDate).toISOString().slice(0, 10),
      }))
      return { formatted: JSON.stringify(formatted) }
  inputs:
    raw_data: "{{fetch_node.result}}"   # Reference the result output of the upstream fetch_node
  outputs:
    formatted: "格式化后的数据"
```

**config field descriptions**:

| Field | Required | Description |
|-------|----------|-------------|
| `runtime` | Yes | `nodejs` or `python` |
| `code` | Yes | Inline code. JS accesses inputs via the `inputs` object and returns the output object via `return`. Python is the same. |
| `timeout_ms` | No | Execution timeout (default 30000ms) |

**Notes for JS code**:
- The code is executed inside `new Function('inputs', ...)`, supporting `async/await` and `fetch`
- **`require()` is not supported**; you cannot import Node.js modules
- Access input data via `inputs.xxx`
- Must `return` an object whose keys match the variable names declared in `outputs`

**Notes for Python code**:
- Access input data via `inputs['xxx']`
- Must `return` a dictionary

#### llm Node Configuration

An llm node performs a **single stateless LLM call**, suitable for text generation, data analysis, summarization, and similar scenarios. The difference from an agent node is that it does not involve the Agent's memory, tools, or skills.

```yaml
- id: summarize
  base: llm
  display:
    name: AI 摘要
  config:
    provider: anthropic              # Provider name (optional, exact match)
    model: claude-sonnet-4-6         # Model (optional, default is used if not set)
    system_prompt: "你是摘要助手"     # System prompt
    max_tokens: 2048                 # Max tokens
    temperature: 0.3                 # Temperature (optional)
    reasoning: medium                # Reasoning level (optional)
  inputs:
    data: "{{fetch_data.result}}"
  outputs:
    summary: "摘要文本"
```

**config field descriptions**:

| Field | Required | Description |
|-------|----------|-------------|
| `system_prompt` | Yes | System prompt that defines the LLM's role and behavior |
| `provider` | No | Provider name (e.g. `anthropic`, `openai`), exact match against configured providers. If not set, the system matches automatically |
| `model` | No | Specifies the model; defaults to the system default if not set |
| `max_tokens` | No | Max number of output tokens |
| `temperature` | No | Temperature parameter (0-2), controls output randomness |
| `reasoning` | No | Reasoning level: `low` / `medium` / `high`. When enabled, the model reasons before answering, suitable for complex analytical tasks |
| `output_schema` | No | A JSON Schema object. When set, the LLM tries to return structured JSON conforming to the schema |

#### agent Node Configuration

An agent node invokes a **full Agent** (stateful), suitable for complex tasks that require the Agent's domain knowledge, memory, tools, or skills.

```yaml
- id: legal_review
  base: agent
  display:
    name: 法律审核
  config:
    agent_id: legal-advisor          # Required: target Agent ID
    task: "审核以下内容：{{summarize.summary}}"  # Task description
  inputs:
    content: "{{summarize.summary}}"
  outputs:
    review: "审核意见"
```

**config field descriptions**:

| Field | Required | Description |
|-------|----------|-------------|
| `agent_id` | Yes | ID of the target Agent |
| `task` | Yes | Task description handed to the Agent. Supports `{{nodeId.outputKey}}`, `{{trigger.key}}`, and `{{secrets.keyName}}` interpolation |

#### human_gate Node Configuration

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

#### llm vs agent Selection Guide

| Scenario | Recommended Base | Reason |
|----------|------------------|--------|
| Text summarization, translation, format conversion | `llm` | Single call, no Agent context required |
| Data analysis, information extraction | `llm` | Stateless processing is sufficient |
| Review requiring domain expertise | `agent` | Requires the Agent's domain knowledge and memory |
| Calling external tools | `agent` | Requires the Agent's tool capability |
| Multi-turn reasoning, complex decisions | `agent` | Requires the Agent's full reasoning chain |

**Quick rule**: If the task can be completed with a single system prompt + one input, use `llm`; if the task requires the Agent's memory, tools, or skills, use `agent`.

#### trigger Node

Each workflow **must have exactly one** trigger node, serving as the workflow entry point. `flow.start` must point to the trigger node.

**Rules**:
- A trigger node **has no inputs**
- A trigger node's outputs use the structured format (`type` / `description` / `required` / `default`) to declare the input parameters the workflow accepts
- `config.type` specifies the trigger method: `manual` (manual trigger) or `webhook` (external trigger)

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
      type: string                      # Parameter type: string / number / boolean / object / array
      description: "参数描述"
      required: true                    # Whether required
      default: "默认值"                  # Optional, default value when not provided
```

**Example** — a trigger with multiple parameters:

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

Downstream nodes reference the parameter values output by the trigger via `{{trigger.paramName}}`.

#### inputs Format Specification

inputs uses an **object map format** — keys are the variable names within this node, and values are references to data sources:

```yaml
# Reference outputs of other nodes
inputs:
  varName: "{{nodeId.outputKey}}"

# Reference trigger parameters
inputs:
  query: "{{trigger.userQuery}}"

# Reference user-level secrets
inputs:
  api_key: "{{secrets.email_api_key}}"

# Multiple inputs
inputs:
  title: "{{extract.title}}"
  body: "{{extract.body}}"
  metadata: "{{trigger.metadata}}"
```

**Array format is forbidden**:

```yaml
# Wrong! Do not use arrays
inputs:
  - name: varName
    source: nodeId.outputKey
```

#### outputs Format Specification

outputs uses an **object map format** — keys are output variable names, and values are description text:

```yaml
outputs:
  result: "处理后的结果数据"
  summary: "结果摘要"
```

#### flow Definition

```yaml
flow:
  start: first_node              # Starting node ID
  edges:                         # Edge list (defines execution order)
    - { from: first_node, to: second_node }
    - { from: second_node, to: third_node }
    - from: third_node           # Conditional branch (optional)
      to: branch_a
      condition: "risk_level == 'high'"
  end: [final_node]              # List of terminal nodes
```

#### Variable Reference System

All dynamic values in the DSL are uniformly referenced using the `{{}}` template syntax:

| Syntax | Source | Example |
|--------|--------|---------|
| `{{nodeId.outputKey}}` | Output of a preceding node | `{{summarize.summary}}` |
| `{{trigger.key}}` | Parameters passed in at trigger time | `{{trigger.filePath}}` |
| `{{secrets.keyName}}` | User-level secret | `{{secrets.dingtalk_token}}` |

**Applicable locations**: This syntax is used both in `inputs` values and in interpolations within `config.prompt`.

#### Secrets References

A workflow can reference user-preconfigured secrets via `{{secrets.keyName}}` for scenarios such as API calls.

- Secrets are preconfigured by the user in `${DESIRECORE_ROOT}/config/secrets.json`
- The engine automatically resolves `{{secrets.*}}` at runtime, replacing them with the actual values
- Secrets are resolved only during the execution phase; their actual values are not exposed during validation or dry-run

```yaml
# Reference a secret in inputs
inputs:
  api_key: "{{secrets.email_api_key}}"
  webhook_url: "{{secrets.dingtalk_webhook}}"

# Reference a secret in config.prompt (not recommended, only for special cases)
config:
  prompt: "使用 token {{secrets.github_token}} 访问仓库"
```

### Phase 3: Validate the DSL

Use the `WorkflowValidate` tool to validate the structure and reference integrity of the DSL file.

**How to call**:

```
Tool: WorkflowValidate
Parameters:
  path: ${DESIRECORE_ROOT}/workflows/<wf_id>/workflow.dsl.yaml
```

**What is validated**:
- YAML syntax correctness
- JSON Schema compliance (required fields, types, formats)
- Uniqueness of node IDs
- Validity of edge references (from/to both point to existing nodes)
- The starting and terminal nodes exist
- Cycle detection (DAG validation)
- The upstream nodes and output fields referenced by inputs exist

**Validation passes** → Proceed to phase 4
**Validation fails** → Fix using the Edit tool based on the error information, then re-validate

### Phase 4: Dry-run Testing

Use the `WorkflowTest` tool to perform a simulated execution (dry-run) without actually invoking Agents or executing code.

**How to call**:

```
Tool: WorkflowTest
Parameters:
  path: ${DESIRECORE_ROOT}/workflows/<wf_id>/workflow.dsl.yaml
  params:                      # Optional, used to simulate trigger parameters
    filePath: /path/to/input.md
```

**What is tested**:
- Verifies whether topological sorting succeeds
- Simulates the data flow path between nodes
- Checks whether all inputs references can be resolved at runtime
- Outputs an execution plan preview (node execution order)

**Test passes** → Confirm with the user whether to perform a real run
**Test fails** → Fix based on the error information, then retest

### Phase 5: Real Execution

Use the `WorkflowRun` tool to start the workflow.

**How to call**:

```
Tool: WorkflowRun
Parameters:
  path: ${DESIRECORE_ROOT}/workflows/<wf_id>/workflow.dsl.yaml
  params:                      # Optional, passed in as the {{trigger.key}} context
    filePath: /path/to/input.md
```

**Execution process**:
- The engine executes nodes one by one in topological order
- Node status change events are pushed in real time via SSE
- When a human_gate node is encountered, execution pauses and waits for user approval
- After all terminal nodes complete, the final result is returned

**After execution completes**:
- Show the user a summary of the execution result
- If there are failed nodes, explain the cause of failure and recommended fixes

### Notes

1. **workflow_id naming**: Must start with the `wf_` prefix and use snake_case, e.g. `wf_contract_review`
2. **Strict step-by-step construction**: Step 2a writes only the node topology skeleton (without config/code); after confirmation, step 2b fills in configurations node by node in topological order. Do not write all details in one go
3. **Input/output format**: inputs and outputs must use the object map format (`{ key: value }`); do not use arrays
4. **Variable interpolation**: inputs and the prompt / system_prompt / task fields of llm/agent/human_gate support `{{nodeId.outputKey}}`, `{{trigger.key}}`, and `{{secrets.keyName}}`
5. **Validate first**: Always validate before performing a real run, then dry-run, to reduce runtime errors
6. **Human gating**: For steps involving important decisions (such as release, payment, or deletion), it is recommended to use a human_gate node

### Error Handling

| Error Scenario | Handling |
|----------------|----------|
| YAML syntax error | Check indentation and format, fix using the Edit tool |
| Validation failure | Fix item by item based on WorkflowValidate's error details |
| Referenced node does not exist | Check whether nodeId.outputKey referenced in inputs is spelled correctly |
| Dry-run failure | Check topological sorting and the data flow path |
| Execution timeout | Check whether any agent node prompt is overly complex |
| human_gate rejected | The workflow aborts; explain to the user the reason for the abort and the steps already completed |

### Background Knowledge

> For the AgentFS repository structure, troubleshooting points, and protected paths, see `_agentfs-background.md` and `_protected-paths.yaml`.

### Dependencies

- `WorkflowValidate` built-in tool — validates DSL structure
- `WorkflowTest` built-in tool — dry-run testing
- `WorkflowCreate` built-in tool — validates and writes to the global workflow directory
- `WorkflowRun` built-in tool — performs real workflow execution
- Write / Edit / Read tools — create and edit DSL files
- Agent Service Workflow engine (`lib/workflow-service/`)
