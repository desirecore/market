# DesireCore SKILL.md 完整格式参考

## Frontmatter 完整字段表

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 技能用途描述，必须包含 "Use when" 触发提示 |

### 推荐字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `name` | string | 显示名称（中英文均可） | `"数据分析"` |
| `version` | string | 语义版本号 | `"1.0.0"` |
| `type` | enum | `procedural` / `conversational` / `meta` | `procedural` |
| `risk_level` | enum | `low` / `medium` / `high` | `low` |
| `status` | enum | `enabled` / `disabled` | `enabled` |
| `tags` | string[] | 标签列表 | `[analysis, data]` |
| `metadata.author` | string | 技能作者 | `"user"` |
| `metadata.updated_at` | string | 更新日期 | `"2026-04-03"` |

### 功能控制字段

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `disable-model-invocation` | boolean | `true` | `true`=仅显式调用触发；`false`=自动注入 system prompt |
| `user-invocable` | boolean | `true` | `false`=不出现在命令补全，仅作为背景知识 |
| `allowed-tools` | string[] | 全部 | 限制执行时可用的工具列表（如 `["Edit", "Read", "Bash"]`） |
| `model` | string | 继承 | 覆盖使用的模型 ID（如 `"claude-sonnet-4-20250514"`） |
| `context` | enum | `default` | `fork`=在独立子 Agent 中执行 |
| `agent` | string | — | `context=fork` 时子 Agent 的角色描述 |
| `argument-hint` | string | — | 参数提示，显示在自动补全中（如 `"<issue-number>"`） |

### 依赖声明

```yaml
requires:
  tools:
    - Bash
    - Read
  optional_tools:
    - Edit
  connections:
    - database-x
```

### 市场展示字段

发布到市场时需要填写：

```yaml
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" ...>...</svg>
  short_desc: 一句话简介，用于市场卡片展示
  category: productivity
  maintainer:
    name: Your Name
    verified: false
  compatible_agents: []
  required_client_version: "10.0.20"
  channel: latest
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `market.icon` | string | 内联 SVG 图标 |
| `market.short_desc` | string | 一句话简介 |
| `market.category` | string | 分类 slug（如 `productivity`、`knowledge`、`development`） |
| `market.maintainer.name` | string | 维护者名称 |
| `market.maintainer.verified` | boolean | 是否官方认证 |
| `market.compatible_agents` | string[] | 兼容的 Agent ID |
| `market.required_client_version` | string | 最低客户端版本（semver） |
| `market.channel` | enum | `latest` / `stable` |

### JSON 输出控制

```yaml
json_output:
  enabled: true
  shape: object
```

启用后，AI 的最终回复会被自动解析修复为合法 JSON。`shape` 指定顶层形状：`object`（默认）或 `array`。

### Claude Code 兼容字段

以下字段来自 Claude Code 规范，在 DesireCore 中同样合法（Schema 设置了 `additionalProperties: true`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `license` | string | 许可证声明 |
| `compatibility` | string | 环境兼容性说明 |

## type 类型详解

| 类型 | 含义 | 交互模式 | 典型示例 |
|------|------|---------|---------|
| `procedural` | 流程型 | 按步骤执行，较少交互 | 数据分析、文档处理、API 操作 |
| `conversational` | 对话型 | 多轮交互完成 | 需求收集、头脑风暴、方案评审 |
| `meta` | 元技能 | 管理其他系统资源 | 创建 Agent、管理技能、团队管理 |

## Body 分层详解

### L0：一句话摘要

- 不超过一句话（~50 字）
- 用于快速理解技能做什么
- 标题格式：`## L0：一句话摘要`

### L1：概述与使用场景

- 不超过 300 字
- 用于判断当前任务是否适用该技能
- 推荐子标题：`### 能力描述`、`### 使用场景`、`### 核心价值`
- 标题格式：`## L1：概述与使用场景`

### L2：详细规范

- 无长度限制（但 SKILL.md 整体建议 <500 行）
- 完整的执行指南、API 调用、错误处理、权限要求
- 标题格式：`## L2：详细规范`

### 分层加载机制

- `disable-model-invocation: false` 时：L0 + L1 自动注入 system prompt
- `disable-model-invocation: true` 时：显式调用时加载完整内容（L0 + L1 + L2）
- 不分层时：整段内容作为 fallback

## 完整示例

### procedural 类型（数据分析）

```yaml
---
name: 数据分析
description: >-
  对结构化数据进行深度分析和可视化。Use when 用户要求分析
  CSV/Excel 数据、生成统计报告、或创建数据图表。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags: [analysis, data, visualization]
metadata:
  author: user
  updated_at: '2026-04-03'
---

# data-analysis 技能

## L0：一句话摘要

对结构化数据进行深度分析、统计和可视化。

## L1：概述与使用场景

### 能力描述

支持 CSV、Excel、JSON 等格式数据的读取、清洗、统计分析和图表生成。

### 使用场景

- 分析销售数据并生成月度报告
- 数据清洗和格式转换
- 生成统计图表

## L2：详细规范

### 分析流程

1. 读取并检查数据格式
2. 数据清洗（缺失值、异常值）
3. 统计分析
4. 可视化输出
```

### meta 类型（资源管理）

```yaml
---
name: 知识库管理
description: >-
  管理 Agent 的知识库：导入文档、更新索引、清理过期内容。
  Use when 用户要求导入新文档到知识库、更新或删除已有内容。
version: 1.0.0
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags: [knowledge, management, meta]
metadata:
  author: user
  updated_at: '2026-04-03'
---
```

## 与 Claude Code 格式对比

| 维度 | Claude Code 格式 | DesireCore 格式 |
|------|-----------------|----------------|
| 必填 frontmatter | `name` + `description` | `description` |
| 可选 frontmatter | `license`、`compatibility`、`metadata` | 20+ 字段（全部可选） |
| Body 结构 | 自由 Markdown | L0/L1/L2 分层（推荐，非强制） |
| 分发方式 | `.skill` ZIP 包 | API 安装 / 文件系统 / 市场 |
| 兼容性 | — | DesireCore 是超集，完全向下兼容 |
