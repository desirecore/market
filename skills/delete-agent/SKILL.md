---
name: 删除智能体
description: 安全删除指定的智能体及其关联数据。删除前会验证智能体状态，支持可选地删除所有会话历史。Use when 用户需要删除不再使用的智能体。
type: meta
risk_level: high
status: enabled
disable-model-invocation: true
metadata:
  author: desirecore
  updated_at: '2026-02-28'
version: 2.2.0
tags:
  - 智能体
  - 删除
  - 元技能
  - 清理
  - 安全
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="da2-a" x1="2" y1="7" x2="16"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#FF9500"/><stop
    offset="1" stop-color="#FF3B30"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#da2-a)" fill-opacity="0.15" stroke="url(#da2-a)"
    stroke-width="1.5"/><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
    fill="url(#da2-a)" fill-opacity="0.1" stroke="url(#da2-a)"
    stroke-width="1.5"/><circle cx="19" cy="11" r="4" fill="#FF3B30"
    fill-opacity="0.12"/><line x1="16.5" y1="11" x2="21.5" y2="11"
    stroke="#FF3B30" stroke-width="2" stroke-linecap="round"/></svg>
  short_desc: 安全删除智能体及其关联数据，支持多重确认与可选历史清理
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# delete-agent 技能

## L0：一句话摘要

安全删除指定的智能体及其关联数据，包括文件系统、内存状态和可选的会话历史。

## L1：概述与使用场景

### 能力描述

delete-agent 是一个**元技能（Meta-Skill）**，赋予 DesireCore 安全删除其他智能体的能力。它会执行完整的前置检查、状态验证，并清理所有关联数据。

### 使用场景

- 用户想要清理不再使用的智能体
- 删除测试或实验性质的临时智能体
- 释放存储空间，删除旧智能体及其历史记录
- 用户明确要求"删除"、"移除"某个智能体

### 核心价值

- **安全性**：多重检查确保不会误删活跃智能体
- **完整性**：清理文件系统、内存状态、消息订阅等所有关联数据
- **可恢复性**：默认保留会话历史，可选择是否删除

## L2：详细规范

### 执行流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   列出可选    │ ──→ │   确认意图    │ ──→ │   询问选项    │
│   智能体     │     │   与目标      │     │  (删除历史?)  │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   返回结果    │ ←── │   执行删除    │ ←── │   最终确认    │
│   与回执      │     │   API 调用    │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 阶段 1：列出可删除的智能体

**触发条件**：用户表达删除意图但未指定具体智能体

**操作**：
- 调用 `GET /api/agents` 获取所有智能体列表
- 筛选出状态为 `offline` 或 `error` 的智能体（可安全删除）
- 标注出 `online`/`busy`/`recovery` 状态的智能体（需先停止）

**输出示例**：
```
可删除的智能体：
1. 法律顾问助手 (legal-assistant) - 状态: offline
2. 测试机器人 (test-bot) - 状态: offline

当前活跃的智能体（需先停止才能删除）：
- 数据分析师 (data-analyst) - 状态: online
```

### 阶段 2：确认用户意图与目标

**确认要点**：
- 用户指定的智能体名称/ID
- 明确告知删除操作不可恢复
- 展示智能体基本信息供用户确认

**对话示例**：
```
您要删除智能体 "法律顾问助手" (legal-assistant)。
⚠️ 警告：此操作不可恢复，该智能体的所有配置、技能、工具将被永久删除。

确认删除？（是/否）
```

### 阶段 3：询问删除选项

**询问内容**：
```
是否同时删除该智能体的所有会话历史？
- 是：删除智能体及其所有对话记录
- 否：保留会话历史，仅删除智能体本身

默认选项：否（保留历史）
```

**参数映射**：
- 用户选择"是" → `deleteRuns=true`
- 用户选择"否" → `deleteRuns=false`（默认）

### 阶段 4：最终确认

**确认摘要**：
```
请确认删除操作：
- 目标智能体：法律顾问助手 (legal-assistant)
- 删除范围：智能体 + 会话历史（如用户选择）
- 风险等级：高（不可恢复）

确认执行删除？（是/否）
```

### 阶段 5：执行删除 API 调用

**API 端点**：`DELETE /api/agents/{agentId}`

**查询参数**：
- `deleteRuns`: `'true'` 或 `'false'`

**请求示例**：
```bash
curl -X DELETE "{agentServiceUrl}/api/agents/legal-assistant?deleteRuns=true"
```

> `{agentServiceUrl}` 取自 system prompt「本机 API」小节中的 Agent Service 地址。

### 阶段 6：返回操作结果

**成功响应处理**：
```json
{
  "deleted": true,
  "cleanedPaths": [
    "/Users/xxx/.desirecore/agents/legal-assistant",
    "/Users/xxx/.desirecore/users/xxx/agents/legal-assistant"
  ],
  "deletedRunsCount": 5,
  "memoryCleaned": {
    "scheduler": true,
    "queue": 0,
    "messaging": 3,
    "mcp": true
  }
}
```

**结果报告模板**：
```
✅ 智能体 "法律顾问助手" 已成功删除

清理详情：
- 文件系统：已删除 2 个目录
- 调度器：已停止所有定时任务
- 消息订阅：已取消 3 个订阅
- MCP 连接：已关闭
- 会话历史：已删除 5 条记录
```

## 前置检查

### 智能体状态验证

在调用删除 API 前，系统会自动检查：

| 状态 | 是否可删除 | 处理方式 |
|------|-----------|--------|
| `offline` | ✅ 是 | 直接删除 |
| `error` | ✅ 是 | 直接删除 |
| `online` | ❌ 否 | 返回 409 错误，提示先停止 |
| `busy` | ❌ 否 | 返回 409 错误，提示等待完成 |
| `recovery` | ❌ 否 | 返回 409 错误，提示等待恢复 |

**API 返回 409 时的处理**：
```
无法删除智能体 "xxx"：当前处于 online 状态。

请先停止该智能体，或等待其完成任务后再删除。
停止命令：...
```

## 错误处理

| 错误码 | 场景 | 处理方式 |
|--------|------|---------|
| 400 | Agent ID 格式无效 | 提示用户检查智能体名称 |
| 404 | 智能体不存在 | 告知用户智能体已被删除或 ID 错误 |
| 409 | 智能体处于活跃状态 | 提示先停止智能体或等待任务完成 |
| 500 | 服务器内部错误 | 记录错误，提示用户稍后再试 |

## 删除范围说明

### 始终删除的数据

以下数据无论 `deleteRuns` 参数如何都会被删除：

1. **AgentFS 目录**：`~/.desirecore/agents/{agentId}/`
   - agent.json（入口配置）
   - persona.md（人格定义）
   - principles.md（行为原则）
   - skills/（技能目录）
   - tools/（工具目录）
   - memory/（记忆目录）
   - heartbeat/（心跳配置）

2. **用户偏好数据**：`~/.desirecore/users/{userId}/agents/{agentId}/`
   - 工作目录配置
   - 用户特定设置

3. **内存状态**
   - 调度定时器（全部停止）
   - 队列中的请求（全部取消）
   - 消息订阅（全部取消）
   - MCP 连接（全部关闭）

4. **注册表条目**：从 AgentRegistry 中注销

### 可选删除的数据

仅当 `deleteRuns=true` 时删除：

- **会话历史**：`~/.desirecore/runs/` 中该智能体的所有记录
- **话题索引**：相关话题的索引和元数据

### 保留的数据

以下数据不会被删除：

- 其他智能体的数据
- 用户配置文件
- 全局设置
- 市场缓存数据

## 权限要求

- 建议优先通过 `Bash` 工具调用 curl 访问 Agent Service HTTP API 完成操作
- API 基础地址已注入到 system prompt 的「本机 API」小节，直接引用即可
- 删除操作需要用户显式确认（高风险操作）

## 依赖

- Agent Service HTTP API（`DELETE /api/agents/{agentId}`）
- System prompt 中的本机 API 地址声明
