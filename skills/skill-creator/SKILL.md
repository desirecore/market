---
name: 技能创建器
description: >-
  引导用户创建和编辑符合规范的 SKILL.md 技能包。支持 DesireCore 完整格式
  （frontmatter 元数据 + L0/L1/L2 分层内容 + 脚本/参考/资产）和 Claude Code
  基础格式。Use when 用户要求创建新技能、更新已有技能、或将经验封装为可复用
  的技能包。
version: 1.0.0
type: meta
risk_level: low
status: enabled
disable-model-invocation: false
tags:
  - skill
  - creation
  - meta
  - template
  - authoring
metadata:
  author: desirecore
  updated_at: '2026-04-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="sc" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><rect x="4" y="4"
    width="16" height="16" rx="3.5" fill="url(#sc)" fill-opacity="0.12"
    stroke="url(#sc)" stroke-width="1.5"/><path d="M8 8h8M8 12h5"
    stroke="url(#sc)" stroke-width="1.8" stroke-linecap="round"/><path d="M15
    14l2 2-2 2" stroke="#34C759" stroke-width="2" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  short_desc: 引导创建符合规范的 SKILL.md 技能包，支持完整元数据与分层内容
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# skill-creator 技能

## L0：一句话摘要

引导用户将需求、经验和工作流封装为结构化的 SKILL.md 技能包。

## L1：概述与使用场景

### 能力描述

skill-creator 是一个**元技能（Meta-Skill）**，赋予 Agent 创建和编辑技能的能力。技能是模块化、自包含的能力包，通过 SKILL.md 为 Agent 提供专业知识、工作流和工具集成——将 Agent 从通用助手转变为领域专家。

### 使用场景

- 用户想把反复执行的工作流封装为可复用技能
- 用户想创建新技能教会 Agent 新的能力
- 用户想更新已有技能、优化其效果
- 用户分享了参考资料，需要组织为结构化的技能包

### 核心价值

- **沉淀经验**：将个人知识和工作流固化为可复用的 Skill
- **自我扩展**：创建的技能让 Agent 能力持续增长
- **规范化**：生成符合标准的 SKILL.md，确保技能系统正确解析和分发

## L2：详细规范

### 关于技能

技能是模块化、自包含的能力包，为 Agent 提供：

1. **专业工作流** — 特定领域的多步骤流程
2. **工具集成** — 处理特定文件格式或 API 的指南
3. **领域知识** — 公司规范、业务逻辑、专业 Schema
4. **捆绑资源** — 脚本、参考文档和资产文件

### 核心原则

#### 简洁优先

上下文窗口是公共资源。技能与系统提示、对话历史、其他技能元数据和用户请求共享上下文窗口。

**默认假设：AI 已经非常聪明。** 只添加 AI 不知道的内容。对每条信息问自己："AI 真的需要这个解释吗？" "这段话值得它的 Token 成本吗？"

优先使用简洁的例子而非冗长的解释。

#### 设置适当的自由度

根据任务的脆弱性和可变性匹配指令的具体程度：

- **高自由度（文本指引）**：多种方案都可行时，决策依赖上下文
- **中自由度（伪代码或带参脚本）**：存在首选模式，允许一定变化
- **低自由度（固定脚本，少量参数）**：操作脆弱易错，一致性至关重要

#### 渐进式披露

技能使用三层加载系统高效管理上下文：

1. **元数据（name + description）** — 始终在上下文中（~100 词）
2. **SKILL.md body** — 技能触发时加载（<5k 词）
3. **捆绑资源** — Agent 按需加载（无限制，脚本可直接执行无需读入上下文）

### 技能结构

```
skill-name/
├── SKILL.md          （必须：技能定义文件）
├── scripts/          （可选：可执行脚本）
├── references/       （可选：参考文档）
└── assets/           （可选：输出用资源文件）
```

#### SKILL.md 格式

SKILL.md 由两部分组成：**Frontmatter（YAML 元数据）** 和 **Body（Markdown 指令）**。

##### Frontmatter 字段

**必填**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 技能用途描述。**必须包含 "Use when" 触发提示**——AI 据此判断何时使用该技能 |

**推荐**：

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `name` | string | 技能显示名称 | 目录名 |
| `version` | string | 语义版本号（如 `1.0.0`） | — |
| `type` | enum | `procedural` / `conversational` / `meta` | — |
| `risk_level` | enum | `low` / `medium` / `high` | — |
| `status` | enum | `enabled` / `disabled` | `enabled` |
| `tags` | string[] | 标签列表 | — |
| `metadata` | object | `author`、`updated_at` | — |

**功能控制**：

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `disable-model-invocation` | boolean | `true` | `true`=仅显式调用触发；`false`=自动注入 system prompt |
| `user-invocable` | boolean | `true` | `false`=不出现在命令补全，仅作为背景知识 |
| `allowed-tools` | string[] | — | 限制执行时可用的工具列表 |
| `requires` | object | — | 依赖声明：`tools`、`optional_tools`、`connections` |

完整字段表（含市场发布、JSON 输出、fork 执行等高级字段）见 [references/desirecore-format.md](references/desirecore-format.md)。

> **Claude Code 兼容说明**：Claude Code 仅使用 `name` + `description`（+ 可选 `license`、`compatibility`）。这些字段在 DesireCore 中完全合法——DesireCore 格式是 Claude Code 的超集。

##### Body 结构

**推荐使用 L0/L1/L2 分层**：

```markdown
# skill-id 技能

## L0：一句话摘要
用一句话描述这个技能做什么。

## L1：概述与使用场景
### 能力描述 / ### 使用场景 / ### 核心价值

## L2：详细规范
### 具体操作步骤 / ### 错误处理
```

分层加载机制：
- **L0**（~50 字）：快速理解技能做什么
- **L1**（~300 字）：判断是否适用于当前任务
- **L2**（不限）：完整的执行指南

> 分层不是强制的。如果技能内容简短（<100 行），可以不分层——解析器会以整段内容作为 fallback。Claude Code 的无分层格式在 DesireCore 中同样正常工作。

#### Bundled Resources

##### Scripts（`scripts/`）

可执行代码（Python/Bash 等），用于需要确定性可靠性或被反复编写的任务。

- **何时使用**：相同代码被反复编写，或需要确定性可靠性
- **示例**：`scripts/rotate_pdf.py`（PDF 旋转）、`scripts/fill_form.py`（表单填充）
- **优势**：Token 高效，确定性，可直接执行无需读入上下文
- **注意**：脚本可能仍需被 AI 读取以做环境适配

##### References（`references/`）

文档和参考资料，按需加载到上下文中。

- **何时使用**：AI 工作时需要参考的详细文档
- **示例**：API 文档、数据库 Schema、领域知识、公司政策
- **最佳实践**：大文件（>10k 词）在 SKILL.md 中提供 grep 搜索模式
- **避免重复**：信息只放 SKILL.md 或 references 中的一处

##### Assets（`assets/`）

不加载到上下文、而是用于输出的文件。

- **何时使用**：技能需要在最终输出中使用的文件
- **示例**：PPT 模板、HTML 骨架、logo 图片、字体文件
- **优势**：将输出资源与文档分离

#### 不应包含的内容

技能应只包含 AI 执行任务所需的文件。**不要**创建：README.md、INSTALLATION_GUIDE.md、CHANGELOG.md 等辅助文档。

### 渐进式披露模式

保持 SKILL.md body 在 500 行以内。接近限制时拆分到 references。

**模式 1：高层指南 + 参考文件**

```markdown
# PDF Processing

## Quick start
[核心代码示例]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**模式 2：按领域组织**

```
bigquery-skill/
├── SKILL.md (overview)
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

用户问销售指标时，AI 只读 sales.md。

**模式 3：基本内容 + 条件高级内容**

```markdown
## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

**重要**：避免深层嵌套引用——references 只从 SKILL.md 直接链接一层。长 reference 文件（>100 行）在顶部加目录。

### 创建流程

1. 用具体例子理解技能需求
2. 规划可复用资源（脚本、参考、资产）
3. 初始化技能（运行 init_skill.py）
4. 编辑技能（实现资源，编写 SKILL.md）
5. 验证技能（运行 quick_validate.py）
6. 安装技能
7. 迭代优化

#### 步骤 1：理解技能需求

跳过此步仅当技能的使用模式已经完全清晰。即使处理已有技能时，此步仍有价值。

通过具体例子理解技能将如何被使用。例如构建 image-editor 技能时：

- "这个技能应支持哪些功能？编辑、旋转、其他？"
- "能举几个使用场景吗？"
- "什么操作应该触发这个技能？"

避免一次问太多问题——从最重要的开始，按需跟进。当对技能应支持的功能有清晰认知时，结束此步。

#### 步骤 2：规划资源

分析每个例子：

1. 考虑如何从零执行
2. 识别哪些脚本、参考、资产在反复执行时有帮助

示例分析：

- `pdf-editor` 处理"旋转 PDF"→ 每次都要写相同代码 → `scripts/rotate_pdf.py`
- `frontend-webapp-builder` 处理"创建 todo app"→ 每次都要写样板代码 → `assets/hello-world/`
- `big-query` 处理"今天多少用户登录"→ 每次都要查 Schema → `references/schema.md`

#### 步骤 3：初始化

使用 init_skill.py 创建模板：

```bash
# DesireCore 完整格式（默认，推荐）
scripts/init_skill.py <skill-name> --path <output-directory>

# Claude Code 基础格式
scripts/init_skill.py <skill-name> --path <output-directory> --format basic
```

默认生成 DesireCore 格式（含完整 frontmatter + L0/L1/L2 结构）。`--format basic` 生成 Claude Code 兼容的最小格式。

初始化后，根据需要定制或删除生成的示例文件。

#### 步骤 4：编辑技能

##### 学习设计模式

根据技能需求查阅参考：

- **多步骤流程**：见 [references/workflows.md](references/workflows.md)
- **输出格式标准**：见 [references/output-patterns.md](references/output-patterns.md)

##### 从资源开始

先实现步骤 2 识别的资源文件（scripts/、references/、assets/）。此步骤可能需要用户输入，如品牌资产需要用户提供 logo。

添加的脚本必须实际运行测试，确保无 bug 且输出符合预期。不需要的示例文件应删除。

##### 编写 SKILL.md

**Frontmatter 编写要点**：

- `description` 是最关键的字段——AI 据此判断何时触发技能
- 在 description 中包含 "Use when" 触发提示和典型使用场景
- 所有 "when to use" 信息放 description 中，不放 body 里（body 只在触发后加载）

**Body 编写要点**：

- 始终使用祈使句/不定式形式
- L0 不超过一句话
- L1 用于判断适用性，不超过 300 字
- L2 放完整的操作步骤、API 调用、错误处理

#### 步骤 5：验证

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

验证 SKILL.md 格式、frontmatter 字段合法性和目录结构。

#### 步骤 6：安装

**方式 A：通过 API 安装（推荐，需 Agent Service 运行中）**

```bash
PORT=$(cat ~/.desirecore/agent-service.port 2>/dev/null)

# 安装为全局技能（所有 Agent 可见）
curl -k -X POST "https://127.0.0.1:${PORT}/api/skills" \
  -H "Content-Type: application/json" \
  -d "{\"skillId\": \"<skill-name>\", \"content\": \"$(cat path/to/SKILL.md | jq -Rsa .)\"}"

# 安装为 Agent 级技能（仅指定 Agent 可见）
curl -k -X POST "https://127.0.0.1:${PORT}/api/agents/<agentId>/skills" \
  -H "Content-Type: application/json" \
  -d "{\"id\": \"<skill-name>\", \"fullContent\": \"$(cat path/to/SKILL.md | jq -Rsa .)\"}"
```

**方式 B：文件系统直写**

```bash
# 全局技能
cp -r path/to/skill-name ~/.desirecore/skills/

# Agent 级技能
cp -r path/to/skill-name ~/.desirecore/agents/<agentId>/skills/
```

**方式 C：打包为 .skill 文件（Claude Code 兼容）**

```bash
scripts/package_skill.py <path/to/skill-folder>
```

生成 `skill-name.skill` 文件（ZIP 格式），可在 Claude Code 中使用。

**安装完成后，必须向用户报告**：
- 技能已安装到的完整路径
- 安装的作用域（Global / Agent / Project）
- 如何在后续对话中触发该技能

#### 步骤 7：迭代

1. 在真实任务中使用技能
2. 观察不足或低效之处
3. 确定 SKILL.md 或资源需要如何改进
4. 实施修改并再次测试

### 作用域说明

技能存在三个作用域层级，按优先级从高到低：

| 优先级 | 作用域 | 路径 | 可见范围 |
|--------|--------|------|---------|
| 最高 | Project | `.claude/skills/` | 当前项目所有 Agent |
| 中 | Agent | `~/.desirecore/agents/{agentId}/skills/` | 仅该 Agent |
| 最低 | Global | `~/.desirecore/skills/` | 所有 Agent |

同名技能按优先级覆盖——高优先级的技能会遮蔽低优先级的同名技能。
