---
name: 管理技能
description: >-
  管理 Agent 的技能生命周期：通过 HTTP API 导入、安装、更新、删除技能，
  或通过 AgentFS 文件系统直接编写符合规范的 SKILL.md。Use when 用户要求
  安装技能、从 URL/Git 导入技能、编写新技能、或管理已有技能。
version: 1.0.0
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - skill
  - import
  - management
  - meta
  - agentfs
metadata:
  author: desirecore
  updated_at: '2026-03-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ms-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="4" fill="url(#ms-a)"
    fill-opacity="0.12" stroke="url(#ms-a)"
    stroke-width="1.5"/><path d="M8 12h8M12 8v8" stroke="url(#ms-a)"
    stroke-width="2" stroke-linecap="round"/><circle cx="18" cy="6" r="3"
    fill="#34C759" fill-opacity="0.9"/><path d="M17 6h2M18 5v2"
    stroke="white" stroke-width="1.2" stroke-linecap="round"/></svg>
  short_desc: 导入、编写、安装与管理 Agent 技能的完整工具箱
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# manage-skills 技能

## L0：一句话摘要

管理技能的完整生命周期——导入、编写、安装、更新、删除。

## L1：概述与使用场景

### 能力描述

manage-skills 是一个**元技能（Meta-Skill）**，赋予 DesireCore 管理技能系统的能力。它涵盖 5 种核心操作：

1. **从 URL 导入技能** — 指定远程 SKILL.md 文件 URL，抓取内容并创建
2. **从 Git 仓库批量导入** — 克隆 Git 仓库，扫描所有 SKILL.md，选择性导入
3. **通过 API 管理已有技能** — 列出、读取、更新、删除、启用/禁用技能
4. **通过 AgentFS 直接编写 SKILL.md** — 使用 Write/Edit 工具在文件系统创建技能
5. **批量操作与跨 Agent 复制** — 批量启用/禁用/删除，以及复制技能到其他 Agent

### 使用场景

- 用户想从 GitHub 等平台导入社区分享的技能
- 用户想给某个 Agent 安装新技能、增强其能力
- 用户需要编写自定义技能教会 Agent 新的工作流程
- 用户想批量管理已有技能（启用/禁用/删除）
- 用户想把一个 Agent 的技能复制给另一个 Agent
- 用户需要查看或编辑某个技能的内容

### 核心价值

- **自我扩展**：Agent 可通过导入或编写技能，自主扩展能力边界
- **可治理**：所有技能变更通过 API 或文件系统操作，可追溯、可审计
- **灵活性**：支持 API 导入和文件系统直写两种方式，适应不同场景

## L2：详细规范

### 1. 从 URL 导入单个技能

适用于导入单个 SKILL.md 文件（如 GitHub raw 链接）。

**步骤 1：抓取远程内容**

```bash
POST /api/skills/fetch-url
Content-Type: application/json

{
  "url": "https://raw.githubusercontent.com/user/repo/main/my-skill/SKILL.md"
}
```

**成功响应**（`200 OK`）：

```json
{
  "content": "---\nname: 我的技能\ndescription: ...\n---\n\n# 技能内容..."
}
```

**安全限制**：
- 仅允许 HTTPS URL
- 文件大小上限 20MB
- 请求超时 30 秒

**步骤 2：创建技能**

抓取成功后，根据作用域选择创建端点：

**创建全局技能**（所有 Agent 可见）：

```bash
POST /api/skills
Content-Type: application/json

{
  "skillId": "my-skill",
  "content": "<上一步返回的 content>"
}
```

**创建 Agent 级技能**（仅指定 Agent 可见）：

```bash
POST /api/agents/{agentId}/skills
Content-Type: application/json

{
  "id": "my-skill",
  "fullContent": "<上一步返回的 content>"
}
```

**成功响应**（`201 Created`）：

```json
{
  "success": true,
  "skill": { "id": "my-skill", "name": "我的技能", "description": "..." }
}
```

### 2. 从 Git 仓库批量导入

适用于导入包含多个技能的 Git 仓库。

**步骤 1：扫描仓库**

```bash
POST /api/skills/fetch-git
Content-Type: application/json

{
  "url": "https://github.com/user/skill-collection.git"
}
```

**成功响应**（`200 OK`）：

```json
{
  "skills": [
    {
      "id": "data-analysis",
      "path": "data-analysis",
      "content": "---\nname: 数据分析\n...",
      "sidecarFiles": [
        { "name": "examples.md", "content": "..." }
      ]
    },
    {
      "id": "report-writing",
      "path": "report-writing",
      "content": "---\nname: 报告撰写\n..."
    }
  ]
}
```

API 会自动：
- 使用 `--depth=1` 浅克隆以减少下载量
- 递归扫描目录中的 SKILL.md 文件
- 从目录名推导 skillId（fallback 从 frontmatter name 生成 slug）
- 收集同目录的 sidecar 文件（如 examples.md, references/ 等）
- 完成后自动清理临时目录

**步骤 2：逐个导入选中的技能**

向用户展示扫描结果列表，让用户选择要导入的技能，然后逐个调用创建 API：

```bash
# 全局技能
POST /api/skills
{ "skillId": "data-analysis", "content": "<content>" }

# 或 Agent 级技能
POST /api/agents/{agentId}/skills
{ "id": "data-analysis", "fullContent": "<content>" }
```

**sidecarFiles 处理**：如果扫描结果包含 sidecarFiles，需要在创建技能后将它们写入对应目录：

```bash
# 全局技能的 sidecar 文件路径
~/.desirecore/skills/{skillId}/{filename}

# Agent 级技能的 sidecar 文件路径
~/.desirecore/agents/{agentId}/skills/{skillId}/{filename}
```

### 3. 通过 API 管理已有技能

#### 列出所有技能

```bash
GET /api/skills/list
GET /api/skills/list?agentId={agentId}
GET /api/skills/list?includeDisabled=true
```

返回包含 project、agent、global 三级作用域的技能列表。

#### 列出指定 Agent 的技能

```bash
GET /api/agents/{agentId}/skills
```

#### 读取技能内容

```bash
# 按作用域优先级自动解析
GET /api/skills/{skillId}/content
GET /api/skills/{skillId}/content?agentId={agentId}

# 读取指定 Agent 的技能
GET /api/agents/{agentId}/skills/{skillId}
```

#### 更新技能内容

**更新全局技能**：

```bash
PUT /api/skills/{skillId}/content
Content-Type: application/json

{
  "content": "---\nname: 更新后的技能\n...\n---\n\n# 新内容..."
}
```

**更新 Agent 级技能**：

```bash
PUT /api/agents/{agentId}/skills/{skillId}
Content-Type: application/json

{
  "content": "---\nname: 更新后的技能\n...\n---\n\n# 新内容...",
  "bumpVersion": "minor"
}
```

`bumpVersion` 可选值：`major` | `minor` | `patch`，指定后自动递增版本号。内容变化时系统会自动更新 `metadata.updated_at`。

#### 删除技能

```bash
# 删除全局技能
DELETE /api/skills/{skillId}

# 删除 Agent 级技能
DELETE /api/agents/{agentId}/skills/{skillId}
```

#### 启用/禁用技能

```bash
# 全局技能
PATCH /api/skills/{skillId}/status
Content-Type: application/json
{ "enabled": false }

# Agent 级技能
PATCH /api/agents/{agentId}/skills/{skillId}/status
Content-Type: application/json
{ "enabled": true }
```

#### 批量操作

```bash
POST /api/agents/{agentId}/skills/batch
Content-Type: application/json

{
  "action": "enable",
  "ids": ["skill-a", "skill-b", "skill-c"]
}
```

`action` 可选值：`enable` | `disable` | `delete`

#### 复制技能到其他 Agent

```bash
POST /api/agents/{targetAgentId}/skills/copy
Content-Type: application/json

{
  "sourceSkillId": "data-analysis",
  "sourceAgentId": "analyst",
  "targetSkillId": "data-analysis-v2"
}
```

可选参数：
- `sourceAgentId` — 源 Agent ID（从 agent 级复制时必填）
- `sourceSource` — 源作用域：`project` | `agent` | `global`
- `sourceWorkDir` — 源 project workDir（从 project 级复制时使用）
- `targetSkillId` — 目标技能 ID（不填则沿用 sourceSkillId）

### 4. 通过 AgentFS 直接编写 SKILL.md

当需要从零创建技能，或 API 方式不够灵活时，可直接在文件系统编写 SKILL.md。

#### 目录结构

**全局技能**（所有 Agent 可见）：

```
~/.desirecore/skills/
└── my-new-skill/
    ├── SKILL.md          # 必须：技能定义文件
    ├── examples/          # 可选：示例文件
    ├── scripts/           # 可选：辅助脚本
    └── references/        # 可选：参考资料
```

**Agent 级技能**（仅指定 Agent 可见）：

```
~/.desirecore/agents/{agentId}/
└── skills/
    └── my-new-skill/
        ├── SKILL.md
        └── ...
```

#### SKILL.md 完整格式

```markdown
---
# === 必填字段 ===
description: >-
  技能用途的完整描述。应包含 "Use when" 触发提示，
  帮助 AI 判断何时使用该技能。

# === 推荐字段 ===
name: 技能显示名称
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - tag1
  - tag2
metadata:
  author: your-name
  updated_at: '2026-03-03'

# === 可选字段 ===
disable-model-invocation: false
requires:
  tools:
    - Bash
    - Read
  optional_tools:
    - Edit
---

# skill-id 技能

## L0：一句话摘要

用一句话描述这个技能做什么。

## L1：概述与使用场景

### 能力描述

详细描述技能的核心能力。

### 使用场景

- 场景 1
- 场景 2

### 核心价值

- 价值 1
- 价值 2

## L2：详细规范

### 具体操作步骤

按阶段/步骤详细描述执行流程、API 调用、输入输出格式等。

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| ... | ... |
```

#### 使用 Write 工具创建技能示例

以下示例展示如何使用 Write 工具创建一个全局技能：

```
目标路径：~/.desirecore/skills/daily-summary/SKILL.md
```

写入内容：

```markdown
---
name: 每日摘要
description: >-
  汇总当天对话记录，生成结构化的每日工作摘要。
  Use when 用户要求总结今天的工作、生成日报、或回顾对话内容。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - summary
  - daily
  - productivity
metadata:
  author: user
  updated_at: '2026-03-03'
---

# daily-summary 技能

## L0：一句话摘要

汇总当天对话记录，自动生成结构化的工作摘要。

## L1：概述与使用场景

### 能力描述

从对话历史中提取关键信息，按项目/主题分类整理，生成包含完成事项、
待办事项和重要决策的每日摘要。

### 使用场景

- 用户在一天工作结束时要求总结
- 用户需要生成日报或周报素材
- 用户想回顾某天的对话和决策

## L2：详细规范

### 摘要结构

1. 今日完成事项
2. 进行中事项
3. 重要决策和结论
4. 明日待办建议
```

### 5. SKILL.md 格式参考

#### Frontmatter 字段表

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `description` | **必填** | string | 技能用途描述，建议包含 "Use when" 触发提示 |
| `name` | 推荐 | string | 技能显示名称 |
| `version` | 推荐 | string | 语义版本号（如 `1.0.0`） |
| `type` | 推荐 | enum | `procedural` / `conversational` / `meta` |
| `risk_level` | 推荐 | enum | `low` / `medium` / `high` |
| `status` | 推荐 | enum | `enabled` / `disabled` |
| `tags` | 可选 | string[] | 标签列表，用于搜索和分类 |
| `disable-model-invocation` | 可选 | boolean | `true` 时仅允许显式调用，默认 `false` |
| `requires` | 可选 | object | 依赖声明：`tools`、`optional_tools`、`connections` |
| `metadata` | 可选 | object | 元信息：`author`、`updated_at` |
| `market` | 可选 | object | 市场展示元数据（仅市场发布的技能需要） |

#### type 说明

| 类型 | 含义 | 示例 |
|------|------|------|
| `procedural` | 流程型，按步骤执行 | 数据分析流程、审批流程 |
| `conversational` | 对话型，通过多轮对话完成 | 需求收集、头脑风暴 |
| `meta` | 元技能，管理其他资源 | 创建 Agent、管理技能 |

#### Markdown Body 结构（L0 / L1 / L2）

| 层级 | 内容 | 用途 |
|------|------|------|
| L0 | 一句话摘要 | 快速理解技能做什么 |
| L1 | 能力描述 + 使用场景 + 核心价值 | 判断是否适用 |
| L2 | 详细规范：步骤、API、格式、错误处理 | 具体执行指南 |

### 6. 作用域说明

技能存在三个作用域层级，按优先级从高到低：

| 优先级 | 作用域 | 路径 | 可见范围 |
|--------|--------|------|---------|
| 最高 | Project 级 | `.claude/skills/` (项目根目录) | 当前项目所有 Agent |
| 中 | Agent 级 | `~/.desirecore/agents/{agentId}/skills/` | 仅该 Agent |
| 最低 | Global 级 | `~/.desirecore/skills/` | 所有 Agent |

**同名覆盖规则**：高优先级作用域的同名技能会覆盖低优先级的。例如 Agent 级有一个 `data-analysis` 技能，会覆盖全局同名技能。

### 7. 错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| 400 | 缺少必填字段或格式无效 | 提示用户检查输入，说明哪个字段有问题 |
| 400 | SKILL.md frontmatter 校验失败 | 展示校验错误详情，引导用户修正 |
| 404 | 技能不存在 | 提示技能 ID 可能拼写错误，列出可用技能 |
| 404 | Git 仓库中无 SKILL.md | 提示仓库格式不符合技能规范 |
| 409 | 技能已存在（冲突写入） | 建议使用 PUT 更新而非 POST 创建 |
| 413 | 远程文件超过 20MB | 提示文件过大，建议精简内容 |
| 504 | URL 抓取超时 | 提示网络超时，建议检查 URL 或稍后重试 |
| 500 | 服务器内部错误 | 提示用户稍后再试 |

### 8. 权限说明

- 建议优先通过 `Bash` 工具调用 curl 访问 Agent Service HTTP API 完成操作
- API 基础地址已注入到 system prompt 的「本机 API」小节，直接引用即可
- 导入和创建操作建议先向用户展示预览，获得确认后再执行
- 删除操作需要用户明确确认
- 通过 AgentFS 编写技能时，使用 Write 工具创建文件即可

### 背景知识

> AgentFS 仓库结构、排查要点与受保护路径详见 `_agentfs-background.md` 和 `_protected-paths.yaml`。

### 依赖

- Agent Service HTTP API（Skills 路由组）
- System prompt 中的本机 API 地址声明
- Write / Edit 工具（AgentFS 直写场景）
