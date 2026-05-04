---
name: update-agent
description: >-
  安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent
  行为、安装/卸载技能、调整配置、回滚变更或修订规则。
version: 3.0.2
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
  updated_at: '2026-03-17'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 更新智能体
      short_desc: 安全更新智能体配置、人格、规则与技能，支持 diff 预览与版本回滚
      description: >-
        安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent 行为、安装/卸载技能、调整配置、回滚变更或修订规则。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:a0fecd84f92204bd
      translated_by: human
    en-US:
      name: Update Agent
      short_desc: Safely update Agent config, persona, principles, and skills, with diff preview and version rollback
      description: >-
        Safely update an existing Agent's config, persona, principles, skills, and memory, producing reviewable diffs that are applied and committed only after confirmation. Use when the user asks to modify Agent behavior, install/uninstall skills, adjust config, roll back changes, or revise rules.
      body: ./SKILL.md
      source_hash: sha256:a0fecd84f92204bd
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
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
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# update-agent skill

## L0: One-Sentence Summary

Safely modify an Agent's config, persona, rules, and skills through natural-language conversation.

## L1: Overview and Use Cases

### Capability Description

update-agent is a **Meta-Skill** that lets users modify various Agent configurations through conversation. All modifications produce reviewable diff patches that are applied only after user confirmation, with rollback support.

### Use Cases

- The user wants to adjust the Agent's communication style ("speak more formally")
- Add new behavioral rules ("from now on, warn me before discussing sensitive topics")
- Install or uninstall skill packages ("learn how to write contracts")
- Batch-update multiple settings ("upgrade all your capabilities")

### Core Value

- **Safe and controllable**: All changes require user confirmation, with rollback support
- **Transparent and visible**: Changes are presented as diffs, clear and obvious
- **Version management**: Versions are managed via Git, with traceable history

## L2: Detailed Specification

### Supported Update Types

| Update Type        | Target File     | Risk Level | Example                                |
| ------------------ | --------------- | ---------- | -------------------------------------- |
| Persona update     | `persona.md`    | Medium     | Modify communication style, values     |
| Principles update  | `principles.md` | High       | Add/modify behavioral rules            |
| Skills install     | `skills/`       | Medium     | Add new skill package                  |
| Skills uninstall   | `skills/`       | Low        | Remove skill package                   |
| Memory update      | `memory/`       | Low        | Add knowledge entry                    |
| Tools config       | `tools/`        | High       | Modify tool permissions                |

### Conversation Flow

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

### Stage 1: Intent Recognition

**Trigger conditions** (any one is sufficient):

- The user says "modify your...", "update your...", "adjust the..."
- The user says "from now on you should...", "remember this rule..."
- The user says "install/uninstall this skill..."
- The user describes dissatisfaction with current behavior and expects a change

**Output**: Identify the update type and target scope.

### Stage 2: Change Analysis

**Analysis dimensions**:

| Dimension           | Description                                  |
| ------------------- | -------------------------------------------- |
| Scope of impact     | Which files and behaviors are affected       |
| Risk level          | Low/Medium/High (see risk classification)    |
| Dependency check    | Whether other configs are affected           |
| Conflict detection  | Whether it conflicts with existing rules     |

**Risk classification table**:

| Risk Level  | Conditions                                       | Confirmation Requirement              |
| ----------- | ------------------------------------------------ | ------------------------------------- |
| Low         | Affects only non-core config (e.g. memory entry) | Simple confirmation                   |
| Medium      | Affects persona or normal principles             | Show diff, then confirm               |
| High        | Affects core principles or tool permissions      | Detailed explanation + diff + confirm |
| Protected   | Touches a protected path                         | Block; requires owner permission      |

### Stage 3: Diff Generation

**Diff format example**:

```diff
# persona.md

## 沟通风格

- 友好、随和、轻松幽默
+ 专业、严谨、适度幽默

## 决策偏好

  保持不变...
```

**Diff metadata**:

```yaml
diff_metadata:
  files_affected: 1
  lines_added: 1
  lines_removed: 1
  risk_level: medium
  reversible: true
  estimated_impact: '沟通风格会变得更正式'
```

### Stage 4: User Confirmation

**Confirmation interface**:

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

**Confirmation options**:

- **Apply**: Execute the change
- **Cancel**: Discard the change
- **Modify**: Enter edit mode for fine-tuning

### Stage 5: Apply Changes

Apply the change by reading and writing files directly through AgentFS. **Do not call HTTP APIs, and do not operate Git directly** (version management is handled automatically by the backend).

**AgentFS root directory**: `~/.desirecore/agents/<agentId>/`

**Read file**: Use the `cat` command to read the current contents of the target file.

**Write file**: Use a text-editing tool to write directly to the target file. After writing, re-read the file to verify the contents are correct.

**Note**: After writing the file directly, the backend file watcher automatically detects the change and triggers a Git commit; no manual git command is required.

### Stage 6: Receipt Generation

After a successful change, present a user-friendly receipt (do not expose internal paths or technical details):

> Updated the communication style of "Legal Advisor Assistant".
>
> **Change summary**: Communication style adjusted from "friendly and casual" to "professional and rigorous"
>
> If you're not satisfied, you can say "undo the previous change" anytime to roll back.

### Special Operation: Version Rollback

**Trigger conditions**: The user says "undo the previous change", "roll back to the previous version", "restore the original settings"

**Rollback flow**:

1. Run `git log --oneline -10` in the Agent directory to view recent version history
2. Use `git show <commit>:<file>` to fetch the file contents of the target version, and present them to the user for confirmation
3. After user confirmation, write the target version's contents to the corresponding file
4. Show the change diff and confirm rollback success

```bash
# 查看版本历史
cd ~/.desirecore/agents/<agentId>
git log --oneline -10

# 查看某个版本的文件内容
git show <commit>:persona.md
```

### Background Knowledge

> AgentFS repository structure and protected paths are detailed in `_agentfs-background.md` and `_protected-paths.yaml`.

**Update operation reference table**:

| User Intent                  | Target File     | AgentFS Path                                   |
| ---------------------------- | --------------- | ---------------------------------------------- |
| Modify personality/style     | `persona.md`    | `~/.desirecore/agents/<agentId>/persona.md`    |
| Modify behavioral rules      | `principles.md` | `~/.desirecore/agents/<agentId>/principles.md` |
| Install/uninstall skills     | `skills/`       | `~/.desirecore/agents/<agentId>/skills/`       |
| Modify tools config          | `tools/`        | `~/.desirecore/agents/<agentId>/tools/`        |
| Add memory                   | `memory/`       | `~/.desirecore/agents/<agentId>/memory/`       |
| Modify runtime config        | `agent.json`    | `~/.desirecore/agents/<agentId>/agent.json`    |

### Error Handling

| Error Scenario                      | Handling                                                 |
| ----------------------------------- | -------------------------------------------------------- |
| Attempt to modify a protected path  | Block the operation; prompt that owner permission is required |
| File does not exist                 | The Agent or target file does not exist; ask user to check |
| Insufficient permission             | Filesystem permission error; ask user to check directory permissions |
| Rollback target version not found   | List available versions and ask the user to reselect     |

### Permission Requirements

| Operation                              | Required Role  |
| -------------------------------------- | -------------- |
| Update persona                         | owner, member  |
| Update principles (normal rules)       | owner, member  |
| Update principles (safety red lines)   | owner          |
| Install/uninstall skills               | owner, member  |
| Modify tools permissions               | owner          |
| Version rollback                       | owner          |

---

## Appendix: Update Examples

### Persona Modification Example

**User input**: "Speak a bit more formally, not too casual"

**Operation flow**:

```bash
# 1. 读取当前 persona.md
cat ~/.desirecore/agents/legal-assistant/persona.md

# 输出示例:
# # 法律顾问小助手
# ## L0
# 专业的法律咨询助手
# ## L1
# ### Role
# 法律顾问
# ### Personality
# 友好、随和
# ### Communication Style
# 轻松幽默

# 2. 分析需要修改的部分，生成 diff 展示给用户确认

# 3. 用户确认后，直接编辑文件，将 Personality 和 Communication Style 修改为目标值

# 4. 验证写入结果
cat ~/.desirecore/agents/legal-assistant/persona.md
```

---

### Principles Update Example

### Add New Rule

**User input**: "From now on, when there's a legal issue, remind me to consult a professional lawyer"

**Generated diff**:

```diff
# principles.md

## 必须做

  - 始终保持礼貌和尊重
  - 不确定时主动询问
+ - 遇到法律相关问题时，提醒用户咨询专业律师

## 绝不做
  ...
```

### Modify Existing Rule

**User input**: "Don't remind me every time, it's too verbose"

**Generated diff**:

```diff
# principles.md

## 必须做

- - 每次回答后都提醒用户检查内容
+ - 仅在重要决策时提醒用户检查内容
```
