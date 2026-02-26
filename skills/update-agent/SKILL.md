---
name: update-agent
description: 安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent 行为、安装/卸载技能、调整配置、回滚变更或修订规则。
version: "2.1.0"
type: meta
risk_level: high
status: enabled
disable-model-invocation: true
tags: [agent, update, meta]
metadata:
  author: desirecore
  version: "2.1.0"
  updated_at: "2026-02-26"
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

**应用步骤**：

1. **备份当前版本**：
```bash
git stash push -m "backup before update-agent"
```

2. **应用变更**：
```bash
# 写入修改后的文件
```

3. **Git 提交**：
```bash
git add <affected_files>
git commit -m "refactor(persona): 调整沟通风格为专业严谨

- 修改 persona.md 中的沟通风格描述
- 从'友好随和'调整为'专业严谨'

Updated by: update-agent skill
Risk level: medium
User confirmed: true
"
```

4. **验证变更**：
```bash
# 检查文件语法
# 验证配置完整性
```

### 阶段 6：回执生成

**回执内容**：

```yaml
# ~/.desirecore/runs/<run_id>/receipts/update-<timestamp>.yaml
receipt:
  type: agent-update
  timestamp: "2024-01-15T10:30:00Z"

  request:
    user_intent: "说话正式一点"
    update_type: persona
    target_files:
      - persona.md

  changes:
    files_modified: 1
    diff_summary: "沟通风格从'友好随和'改为'专业严谨'"
    git_commit: "def456..."
    previous_commit: "abc123..."

  metadata:
    risk_level: medium
    user_confirmed: true
    rollback_available: true
```

### 特殊操作：版本回滚

**触发条件**：
- 用户说"撤销刚才的修改"
- 用户说"回滚到之前的版本"
- 用户说"恢复原来的设置"

**回滚流程**：

1. **列出可回滚版本**：
```
可回滚的版本

1. [2小时前] 调整沟通风格为专业严谨
2. [1天前] 添加合同审查技能
3. [3天前] 初始化仓库

请选择要回滚到的版本：
```

2. **确认回滚**：
```
回滚确认

将回滚到版本 #2（1天前）
以下变更将被撤销：
- 沟通风格调整

确认回滚？ [确认] [取消]
```

3. **执行回滚**：
```bash
git revert <commit_hash> --no-edit
# 或
git reset --soft <commit_hash>
```

### 受保护路径

变更应用前**必须**检查是否触及受保护路径。完整定义见共享配置文件 [`_protected-paths.yaml`](../_protected-paths.yaml)。

**关键规则摘要**：
- `persona.md` L0 section → **block**（核心身份不可自动修改）
- `principles.md` "绝不做" section → **block**（安全红线不可自动修改）
- `agent.json` access_control / privacy → **owner_only**（需 owner 确认）
- `tools/` permissions / credentials → **owner_only / block**

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 尝试修改受保护路径 | 阻断操作，提示需要 owner 权限 |
| Diff 应用冲突 | 展示冲突内容，请用户手动解决 |
| Git 操作失败 | 保留修改文件，提示用户手动提交 |
| 回滚版本不存在 | 列出可用版本，请用户重新选择 |

### API 端点

建议优先通过 HTTP API 完成操作，也可直接通过 Read/Write/Edit 工具编辑 AgentFS 文件：

- `PUT /api/agents/:id/files/*` — 更新指定文件内容

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

## 附录：Principles 更新示例

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
