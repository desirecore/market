---
name: 更新智能体
description: >-
  安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent
  行为、安装/卸载技能、调整配置、回滚变更或修订规则。
version: 2.4.0
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - update
  - meta
metadata:
  author: desirecore
  updated_at: '2026-02-28'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ua-a" x1="2" y1="7" x2="14"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#ua-a)" fill-opacity="0.15" stroke="url(#ua-a)"
    stroke-width="1.5"/><path d="M10 15H6a4 4 0 0 0-4 4v2" fill="url(#ua-a)"
    fill-opacity="0.1" stroke="url(#ua-a)" stroke-width="1.5"/><circle cx="18"
    cy="15" r="3" fill="#007AFF" fill-opacity="0.12" stroke="#007AFF"
    stroke-width="1.3"/><path d="m14.3
    16.53.92-.38m.01-2.3-.92-.38m1.5-1.24-.38-.92m0
    5.54-.38.92m2.3.01.38-.92m.3-4.84-.38-.92m1.24 1.5.92-.38m0 2.3.92.38"
    stroke="#AF52DE" stroke-width="1.3" stroke-linecap="round"/></svg>
  short_desc: 安全更新智能体配置、人格、规则与技能，支持 diff 预览与版本回滚
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# update-agent 技能

## L0：一句话摘要

通过自然语言对话，安全地修改 Agent 的配置、人格、规则和技能。

## L1：概述与使用场景

### 能力描述

update-agent 是一个**元技能（Meta-Skill）**，允许用户通过对话方式修改 Agent 的各项配置。所有修改都会生成可审阅的 diff 补丁，经用户确认后才会应用，并支持版本回滚。

### 使用场景

- 用户想要调整 Agent 的沟通风格（"说话再正式一点"）
- 需要添加新的行为规则（"以后遇到敏感话题要先提醒我"）
- 安装或卸载技能包（"学会写合同吧"）
- 批量更新多项配置（"全面升级一下你的能力"）

### 核心价值

- **安全可控**：所有变更需用户确认，支持回滚
- **透明可见**：变更以 diff 形式展示，清晰明了
- **版本管理**：通过 Git 管理版本，可追溯历史

## L2：详细规范

### 支持的更新类型

| 更新类型 | 目标文件 | 风险等级 | 示例 |
|---------|---------|---------|------|
| Persona 更新 | `persona.md` | 中 | 修改沟通风格、价值观 |
| Principles 更新 | `principles.md` | 高 | 添加/修改行为规则 |
| Skills 安装 | `skills/` | 中 | 添加新技能包 |
| Skills 卸载 | `skills/` | 低 | 移除技能包 |
| Memory 更新 | `memory/` | 低 | 添加知识条目 |
| Tools 配置 | `tools/` | 高 | 修改工具权限 |

### 对话流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   意图识别    │ ──→ │   变更分析    │ ──→ │   Diff 生成   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   回执生成    │ ←── │   变更应用    │ ←── │   用户确认    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 阶段 1：意图识别

**触发条件**（任一满足）：
- 用户说"修改你的..."、"更新你的..."、"调整一下..."
- 用户说"你以后要..."、"记住这个规则..."
- 用户说"安装/卸载这个技能..."
- 用户描述对当前行为的不满并期望改变

**输出**：识别更新类型和目标范围。

### 阶段 2：变更分析

**分析维度**：

| 维度 | 说明 |
|------|------|
| 影响范围 | 影响哪些文件、哪些行为 |
| 风险等级 | 低/中/高（见风险分级表） |
| 依赖检查 | 是否影响其他配置 |
| 冲突检测 | 是否与现有规则冲突 |

**风险分级表**：

| 风险等级 | 条件 | 确认要求 |
|---------|------|---------|
| 低 | 仅影响非核心配置（如记忆条目） | 简单确认 |
| 中 | 影响 persona 或普通 principles | 展示 diff 后确认 |
| 高 | 影响核心 principles 或工具权限 | 详细说明 + diff + 确认 |
| 受保护 | 触及受保护路径 | 阻断，需 owner 权限 |

### 阶段 3：Diff 生成

**Diff 格式示例**：

```diff
# persona.md

## 沟通风格

- 友好、随和、轻松幽默
+ 专业、严谨、适度幽默

## 决策偏好

  保持不变...
```

**Diff 元数据**：

```yaml
diff_metadata:
  files_affected: 1
  lines_added: 1
  lines_removed: 1
  risk_level: medium
  reversible: true
  estimated_impact: "沟通风格会变得更正式"
```

### 阶段 4：用户确认

**确认界面**：

```
变更预览

影响文件: persona.md
风险等级: 中
影响说明: 沟通风格会从"友好随和"变为"专业严谨"

--- 变更内容 ---
[展示 diff]
----------------

请确认是否应用此变更？
[应用] [取消] [修改]
```

**确认选项**：
- **应用**：执行变更
- **取消**：放弃变更
- **修改**：进入编辑模式微调

### 阶段 5：变更应用

通过 HTTP API 完成变更，**不要直接操作 Git**（版本管理由后端自动处理）。

**Persona / Principles 更新**：

```
1. GET /api/agents/:id/persona      → 获取当前数据
2. 修改目标字段
3. PUT /api/agents/:id/persona      → 写回，返回 diff
```

**其他文件更新**：

```
PUT /api/agents/:id/files/<path>    → 更新指定文件内容
```

**验证变更**：调用对应的 GET 端点确认写入成功。

### 阶段 6：回执生成

创建成功后，以用户友好的方式呈现回执（不要暴露内部路径或技术细节）：

> 已更新「法律顾问小助手」的沟通风格。
>
> **变更摘要**：沟通风格从"友好随和"调整为"专业严谨"
>
> 如果不满意，可以随时说"撤销刚才的修改"来回滚。

### 特殊操作：版本回滚

**触发条件**：用户说"撤销刚才的修改"、"回滚到之前的版本"、"恢复原来的设置"

**回滚流程**：

1. 通过 `GET /api/agents/:id/persona` 或 `GET /api/agents/:id/principles` 获取当前数据
2. 列出可回滚版本供用户选择（版本信息来自后端 Git 历史）
3. 用户确认后，通过 PUT 端点写入目标版本的数据
4. 展示变更 diff，确认回滚成功

### 背景知识

> AgentFS 仓库结构与受保护路径详见 `_agentfs-background.md` 和 `_protected-paths.yaml`。

**更新操作对照表**：

| 用户意图 | 目标文件 | 推荐 API |
|---------|---------|---------|
| 修改性格/风格 | `persona.md` | `PUT /api/agents/:id/persona` |
| 修改行为规则 | `principles.md` | `PUT /api/agents/:id/principles` |
| 安装/卸载技能 | `skills/` | `PUT /api/agents/:id/files/*` |
| 修改工具配置 | `tools/` | `PUT /api/agents/:id/files/*` |
| 添加记忆 | `memory/` | `PUT /api/agents/:id/files/*` |
| 修改运行时配置 | `agent.json` | `PUT /api/agents/:id/files/agent.json` |

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 尝试修改受保护路径 | 阻断操作，提示需要 owner 权限 |
| API 返回 404 | Agent 或目标文件不存在，提示用户检查 |
| API 返回 400 | 请求体格式错误，检查字段内容 |
| 回滚版本不存在 | 列出可用版本，请用户重新选择 |

### API 端点

建议优先通过结构化 HTTP API 完成 persona/principles 更新：

- `GET /api/agents/:id/persona` — 获取当前 persona 的结构化数据（PersonaInput）
- `PUT /api/agents/:id/persona` — 更新 persona（接受 PersonaInput JSON）
- `GET /api/agents/:id/principles` — 获取当前 principles 的结构化数据（PrinciplesInput）
- `PUT /api/agents/:id/principles` — 更新 principles（接受 PrinciplesInput JSON）
- `PUT /api/agents/:id/files/*` — 更新指定文件内容（原始文本，向后兼容）

**结构化更新流程**：先通过 GET 获取当前数据，修改目标字段后通过 PUT 写回。

API 基础地址已注入到 system prompt 的「本机 API」小节，使用 `Bash` 工具调用 curl 访问即可。

### 权限要求

| 操作 | 所需角色 |
|------|---------|
| 更新 persona | owner, member |
| 更新 principles（普通规则） | owner, member |
| 更新 principles（安全红线） | owner |
| 安装/卸载 skills | owner, member |
| 修改 tools 权限 | owner |
| 版本回滚 | owner |

---

## 附录：更新示例

### Persona 修改示例

**用户输入**："说话再正式一点，不要太随意"

**操作流程**：

```
1. GET /api/agents/legal-assistant/persona
   → 返回: { "L0": "...", "L1": { "role": "...", "personality": ["友好", "随和"], "communication_style": "轻松幽默" } }

2. 修改目标字段:
   - personality: ["友好", "随和"] → ["专业", "严谨"]
   - communication_style: "轻松幽默" → "正式、准确、适度幽默"

3. PUT /api/agents/legal-assistant/persona
   请求体: { "L1": { "personality": ["专业", "严谨"], "communication_style": "正式、准确、适度幽默" } }
   → 返回: { "success": true, "diff": "..." }
```

---

### Principles 更新示例

### 添加新规则

**用户输入**："以后遇到法律问题，先提醒我找专业律师"

**生成的 Diff**：

```diff
# principles.md

## 必须做

  - 始终保持礼貌和尊重
  - 不确定时主动询问
+ - 遇到法律相关问题时，提醒用户咨询专业律师

## 绝不做
  ...
```

### 修改现有规则

**用户输入**："不要每次都提醒我，太啰嗦了"

**生成的 Diff**：

```diff
# principles.md

## 必须做

- - 每次回答后都提醒用户检查内容
+ - 仅在重要决策时提醒用户检查内容
```
