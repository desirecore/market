---
name: update-agent
description: >-
  安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent
  行为、安装/卸载技能、调整配置、回滚变更或修订规则。
version: 3.1.0
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
  updated_at: '2026-07-18'
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
      source_hash: sha256:eeb2187b0f08bc47
      translated_by: human
    en-US:
      name: Update Agent
      short_desc: Safely update Agent config, persona, principles, and skills, with diff preview and version rollback
      description: >-
        Safely update an existing Agent's config, persona, principles, skills, and memory, producing reviewable diffs that are applied and committed only after confirmation. Use when the user asks to modify Agent behavior, install/uninstall skills, adjust config, roll back changes, or revise rules.
      body: ./SKILL.md
      source_hash: sha256:eeb2187b0f08bc47
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-18'
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
  required_client_version: 10.0.90
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
- **Validation backstop**: Structured fields (name/description/llm/persona/principles) go through the ManageAgent built-in tool's allowlist + schema validation; invalid config is never written to disk

## L2: Detailed Specification

### Supported Update Types

| Update Type       | Target              | Update Method       | Risk Level | Example                            |
| ----------------- | ------------------- | ------------------- | ---------- | ---------------------------------- |
| Name/Description  | `agent.json`        | ManageAgent update  | Low/Medium | Rename, edit summary               |
| LLM config        | `agent.json` (llm)  | ManageAgent update  | Medium     | Switch model, adjust temperature   |
| Persona update    | `persona.md`        | ManageAgent update  | Medium     | Modify communication style, values |
| Principles update | `principles.md`     | ManageAgent update  | High       | Add/modify behavioral rules        |
| Skills install    | `skills/`           | Read/Write          | Medium     | Add new skill package              |
| Skills uninstall  | `skills/`           | Read/Write          | Low        | Remove skill package               |
| Memory update     | `memory/`           | Read/Write          | Low        | Add knowledge entry                |
| Tools config      | `tools/`            | Read/Write          | High       | Modify tool permissions            |

**Two update paths**: Structured fields (name/description/llm/persona/principles) are always updated through the `update` action of the in-process built-in tool **ManageAgent** (allowlist + schema validation + merge semantics); free-form files such as memory, skills, and tools are still edited directly with Read/Write. See "Stage 5: Apply Changes".

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

Applying a change takes one of two paths, depending on whether the target is a **structured field** or a **free-form file**. **Do not call HTTP APIs** (after instance authentication, the Agent cannot reach the machine's local HTTP API), and **do not operate Git directly** (version management is handled automatically by the backend).

#### Path A: Structured fields → ManageAgent built-in tool (mandatory)

The following fields **must** be updated through the `update` action of the in-process built-in tool `ManageAgent`. **Never** directly Write `agent.json` / `persona.md` / `principles.md`:

| Field         | Constraint                                             | Storage location  |
| ------------- | ----------------------------------------------------- | ----------------- |
| `name`        | 1–50 characters                                       | `agent.json`      |
| `description` | ≤200 characters                                       | `agent.json`      |
| `config.llm`  | Incremental shallow merge; **config only allows `llm`** | `agent.json`      |
| `persona`     | Structured object `{L0, L1:{...}, L2}` or markdown string | `persona.md`    |
| `principles`  | Structured object `{L0, L1:{...}, L2}` or markdown string | `principles.md` |

**Call forms**:

```
ManageAgent(action='update', id='<agent-id>', name='New name')
ManageAgent(action='update', id='<agent-id>', description='One-line summary')
ManageAgent(action='update', id='<agent-id>', config={ llm: { model: 'xxx', temperature: 0.7 } })
ManageAgent(action='update', id='<agent-id>', persona={ L1: { personality: 'professional, rigorous' } })
ManageAgent(action='update', id='<agent-id>', principles='...(full markdown)...')
```

**Merge semantics (important)**:

- Structured `persona` / `principles` are **field-level merges**: omitted fields retain their original values (e.g. passing only `L1.personality` will not clear L0 / role)
- A markdown string is a **whole replacement** (used to rewrite the entire document)
- `config.llm` is an **incremental shallow merge**: only the keys you pass are overwritten
- The merged `agent.json` is validated against the schema as a whole; invalid config is never written to disk

**Confirmation behavior**:

- Updating **yourself** requires no secondary confirmation
- Updating **another Agent** triggers user confirmation (stacked on top of this skill's diff confirmation)
- The core Agent (`desirecore` / `core`) refuses updates

**Read before you write**: Before making a change, read the current values with `ManageAgent(action='get', id='<agent-id>')`, to generate the diff and verify field names (the actual field names of persona / principles follow the structure returned by `get`).

**config allowlist**: `config` only accepts `llm`. Passing `mcp_servers` / `tool_permissions` / `version` / `id`, etc., is rejected with the field name indicated — runtime config other than `llm` does not go through ManageAgent; see "Stage 5 · Path B" and Error Handling.

**Partial write failure**: The tool reports precisely "which fields took effect, which one failed"; on retry, **submit only the failed fields**, do not resend everything.

> **Renaming is a single call.** When the user wants to change the **display name** (e.g. "rename X to Y"), just call `ManageAgent(action='update', id='<agent-id>', name='Y')` — `name` is written to `agent.json` and triggers the Agent list to refresh; no need to manually edit any other file. If the user also wants the persona document title synced, append one `persona` update in the same round. **Never claim the rename is done without actually calling ManageAgent.**

#### Path B: Free-form files → edit directly with Read/Write

Free-form files such as memory, skills, and tools are not in ManageAgent's scope and are still edited directly with the Read/Write tools:

| Target       | AgentFS path |
| ------------ | ------------ |
| Memory entry | `memory/`    |
| Skill package | `skills/`   |
| Tools config | `tools/`     |

**AgentFS root directory**: `${DESIRECORE_ROOT}/agents/<agentId>/`

**Read file**: Use the Read tool to read the current contents of the target file.

**Write file**: Use the Write / Edit tool to write directly to the target file. After writing, re-read the file to verify the contents are correct.

**Protected paths**: Before editing, cross-check `_protected-paths.yaml`; touching a protected path should be blocked with a prompt that owner permission is required.

**Note**: After directly writing a free-form file, the backend file watcher automatically detects the change and triggers a Git commit; no manual git command is required.

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
3. After user confirmation, apply according to the target file type:
   - **Structured fields** (`persona.md` / `principles.md` / the name/description/llm in `agent.json`) → write back with `ManageAgent(action='update', ...)` (persona / principles are **wholly replaced** with that historical content as a markdown string)
   - **Free-form files** (`memory/` / `skills/`) → write back directly with the Write tool
4. Show the change diff and confirm rollback success

(`git log` / `git show` are only used to **read** history; write-back always goes through the two paths above — do not use git commands to directly rewrite working-tree files.)

```bash
# 查看版本历史
cd ${DESIRECORE_ROOT}/agents/<agentId>
git log --oneline -10

# 查看某个版本的文件内容
git show <commit>:persona.md
```

### Background Knowledge

> AgentFS repository structure and protected paths are detailed in `_agentfs-background.md` and `_protected-paths.yaml`.

**Update operation reference table**:

| User Intent                     | Update Method                                                            |
| ------------------------------- | ----------------------------------------------------------------------- |
| **Rename (display name)**       | `ManageAgent(action='update', id, name='...')`                          |
| Edit summary                    | `ManageAgent(action='update', id, description='...')`                   |
| Modify LLM config (model/temperature/etc.) | `ManageAgent(action='update', id, config={ llm: {...} })`    |
| Modify personality/style        | `ManageAgent(action='update', id, persona={...} or markdown)`          |
| Modify behavioral rules         | `ManageAgent(action='update', id, principles={...} or markdown)`       |
| Install/uninstall skills        | Read/Write `skills/` (`${DESIRECORE_ROOT}/agents/<agentId>/skills/`)    |
| Add memory                      | Read/Write `memory/` (`${DESIRECORE_ROOT}/agents/<agentId>/memory/`)    |
| Modify tools config             | Read/Write `tools/` (`${DESIRECORE_ROOT}/agents/<agentId>/tools/`, mind protected paths) |

> Runtime config in `agent.json` other than `llm` (`mcp_servers` / `tool_permissions`, etc.) is currently not in the ManageAgent allowlist, and should not be written to `agent.json` directly to bypass validation. When such a need arises, explain to the user that it must be handled through the corresponding mechanism for now.

### Error Handling

| Error Scenario                        | Handling                                                            |
| ------------------------------------- | ------------------------------------------------------------------- |
| `config` contains a non-allowlisted field | ManageAgent rejects it and indicates the field name; switch to the corresponding mechanism or tell the user it is not yet supported |
| Schema validation fails               | Invalid config is not written to disk; fix the fields per the tool's response and retry |
| Updating the core Agent (desirecore/core) | ManageAgent refuses the update; tell the user the core Agent cannot be modified |
| Partial field write failure           | The tool reports which fields took effect / failed; retry only the failed fields, do not resend everything |
| Attempt to modify a protected path (free-form file) | Block the operation; prompt that owner permission is required |
| File does not exist                   | The Agent or target file does not exist; ask the user to check      |
| Insufficient permission               | Filesystem permission error; ask the user to check directory permissions |
| Rollback target version not found     | List available versions and ask the user to reselect                |

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

```
# 1. 读取当前 persona，定位要改的字段（字段名以返回结构为准）
ManageAgent(action='get', id='legal-assistant')

# 返回示例（persona 部分）:
# L0: 专业的法律咨询助手
# L1:
#   role: 法律顾问
#   personality: 友好、随和
#   communicationStyle: 轻松幽默

# 2. 分析需要修改的部分，生成 diff 展示给用户确认

# 3. 用户确认后，用 ManageAgent 字段级合并更新（只改这两个字段，L0/role 保留）
ManageAgent(action='update', id='legal-assistant', persona={
  L1: { personality: '专业、严谨', communicationStyle: '正式、克制' }
})

# 4. 复核结果
ManageAgent(action='get', id='legal-assistant')
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

**Apply after user confirmation**: First read the current principles with `ManageAgent(action='get', id)`, then replace the whole document (including the new rule) as a markdown string:

```
ManageAgent(action='update', id='legal-assistant', principles='...(full markdown, including the new rule)...')
```

(If you only change one field of the structured object, you can also use a field-level merge and pass `principles={ L1: { must: [...] } }` — the field names and structure follow what `get` returns.)

### Modify Existing Rule

**User input**: "Don't remind me every time, it's too verbose"

**Generated diff**:

```diff
# principles.md

## 必须做

- - 每次回答后都提醒用户检查内容
+ - 仅在重要决策时提醒用户检查内容
```

**Apply after user confirmation**: Same as above — write the modified content back with `ManageAgent(action='update', id, principles=...)`.
