---
name: delete-agent
description: 安全删除指定的智能体及其关联数据。删除前会验证智能体状态，支持可选地删除所有会话历史。Use when 用户需要删除不再使用的智能体。
version: 2.5.0
type: meta
risk_level: high
status: enabled
disable-model-invocation: true
tags:
  - agent
  - deletion
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
      name: 删除智能体
      short_desc: 安全删除智能体及其关联数据，支持多重确认与可选历史清理
      description: 安全删除指定的智能体及其关联数据。删除前会验证智能体状态，支持可选地删除所有会话历史。Use when 用户需要删除不再使用的智能体。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:6b971559e1d4ccc0
      translated_by: human
    en-US:
      name: Delete Agent
      short_desc: Safely delete an Agent and its associated data, with multi-step confirmation and optional history cleanup
      description: Safely delete a specified Agent and its associated data. Verifies the Agent's state before deletion and optionally removes all session history. Use when the user needs to delete an Agent that is no longer in use.
      body: ./SKILL.md
      source_hash: sha256:6b971559e1d4ccc0
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-18'
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
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.90
---

# delete-agent Skill

## L0: One-line Summary

Safely delete a specified Agent and its associated data, including filesystem, in-memory state, and optionally session history.

## L1: Overview and Use Cases

### Capability Description

delete-agent is a **Meta-Skill** that empowers DesireCore to safely delete other Agents. It runs full pre-flight checks and state validation through the in-process builtin tool **ManageAgent**, and cleans up all associated data.

### Use Cases

- The user wants to clean up Agents that are no longer in use
- Delete temporary Agents created for testing or experimentation
- Free up storage space by deleting old Agents and their history
- The user explicitly asks to "delete" or "remove" a particular Agent

### Core Value

- **Safety**: multiple rejection rules at the tool layer ensure that core Agents, the caller itself, or active Agents are never deleted by mistake
- **Completeness**: cleans up filesystem, in-memory state, message subscriptions, and all associated data, and handles team cascading
- **Recoverability**: session history is preserved by default, with the option to delete it

## L2: Detailed Specification

### Execution Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  List target │ ──→ │   Confirm    │ ──→ │   Ask about  │
│    Agents    │     │ intent/target│     │   options    │
└──────────────┘     └──────────────┘     │ (delete runs?)│
                                          └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Return result│ ←── │   Execute    │ ←── │  Inform that │
│  and receipt │     │  ManageAgent │     │  a popup will│
│              │     │              │     │    appear    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Phase 1: List Deletable Agents

**Trigger condition**: the user expresses intent to delete but does not specify a particular Agent

**Operation**:

- Call `ManageAgent(action='list')` to fetch the list of all Agents
- Filter Agents whose status is `offline` or `error` (safe to delete)
- Annotate Agents whose status is `online`/`busy`/`recovery` (must be stopped first, otherwise the tool will reject them)
- To view detailed information about a specific Agent, call `ManageAgent(action='get', id='<agent-id>')`

**Output example**:

```
Deletable Agents:
1. Legal Advisor Assistant (legal-assistant) - status: offline
2. Test Bot (test-bot) - status: offline

Currently active Agents (must be stopped before deletion):
- Data Analyst (data-analyst) - status: online
```

### Phase 2: Confirm User Intent and Target

**Confirmation points**:

- The Agent name/ID specified by the user
- Explicitly inform that deletion is irreversible
- Display the Agent's basic info for the user to confirm

**Dialog example**:

```
You are about to delete the Agent "Legal Advisor Assistant" (legal-assistant).
⚠️ Warning: this operation is irreversible. All configuration, skills, and tools of this Agent will be permanently deleted.

Confirm deletion? (yes/no)
```

### Phase 3: Ask About Deletion Options

**Question content**:

```
Do you also want to delete all session history of this Agent?
- Yes: delete the Agent and all of its conversation records
- No: keep session history; delete only the Agent itself

Default option: No (keep history)
```

**Parameter mapping**:

- User chooses "Yes" → `deleteRuns=true`
- User chooses "No" → `deleteRuns=false` (default, can be omitted)

### Phase 4: Inform About the Tool-level Confirmation

The delete action of `ManageAgent` **always triggers a user confirmation popup at the tool layer**, so there is no need to repeat a second confirmation prompt at the skill layer. However, before the call you should inform the user:

```
About to delete the Agent "Legal Advisor Assistant" (legal-assistant), with a scope of the Agent + session history (if chosen by the user).
The system will show a confirmation window; please confirm the execution in the popup.
```

### Phase 5: Execute the Deletion (ManageAgent tool)

**Tool call**:

```
ManageAgent(action='delete', id='legal-assistant', deleteRuns=true)
```

**Parameters**:

- `id`: the target Agent ID (required)
- `deleteRuns`: `true` to also delete all session history; `false` (default) to keep history, can be omitted

The tool shows a user confirmation popup before executing; once confirmed, it completes the deletion, including team cascading: a team where the target is the leader is automatically disbanded, and a target that is a member is automatically removed.

### Phase 6: Return the Operation Result

**Successful receipt handling**: the tool returns the deletion result, including fields such as the cleaned paths, the number of deleted sessions, and in-memory state cleanup details. Generate the report from these.

**Result report template**:

```
✅ Agent "Legal Advisor Assistant" successfully deleted

Cleanup details:
- Filesystem: 2 directories deleted
- Scheduler: all scheduled tasks stopped
- Message subscriptions: 3 subscriptions canceled
- MCP connection: closed
- Session history: 5 records deleted
- Team cascading: the target's team has been disbanded / the target has been removed from its team (if applicable)
```

## State Validation and Error Handling

### Pre-deletion State Check

When listing Agents in Phase 1, filter by the status returned from `ManageAgent(action='list')`:

| Status                         | Deletable?  | Phase 1 Display                |
| ------------------------------ | ----------- | ------------------------------ |
| `offline` / `error`            | ✅ Yes      | Listed under "Deletable"       |
| `online` / `busy` / `recovery` | ❌ Stop first | Annotated "must be stopped"; not entered into the subsequent flow |

> Agents in an active state (online/busy/recovery) are directly rejected by the delete action of `ManageAgent`. Prompt the user to stop the Agent manually in the UI, or wait until it finishes its current task before deleting.

### Error Semantics Returned by the Tool

`ManageAgent(action='delete', ...)` returns a clear error in the following cases; use them to explain the situation to the user and suggest next steps:

| Rejection Scenario | Trigger Condition                                              | Handling                              |
| ------------------ | ------------------------------------------------------------- | ------------------------------------- |
| Core Agent rejected | The target is a core Agent (desirecore/core/bound UUID)       | Inform the user that core Agents cannot be deleted |
| Self-deletion rejected | The target is the caller itself                            | Inform the user that an Agent cannot delete itself |
| Active state rejected | The target is in `online`/`busy`/`recovery` state          | Prompt the user to stop the Agent in the UI first |
| Not found          | No Agent exists for the target ID                             | Inform the user the Agent has already been deleted or the ID is wrong |

## Deletion Scope

| Category         | Content Deleted                                                                                                                   | Condition              |
| ------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| **Always deleted** | AgentFS directory (config, persona, rules, skills, tools, memory), user preference data, in-memory state (scheduler, queue, message subscriptions, MCP connection), registry entries | Unconditional |
| **Optionally deleted** | Session history, topic index                                                                                         | `deleteRuns=true` |
| **Team cascading** | Target is the leader → its team is disbanded; target is a member → removed from the team                          | Automatic |
| **Preserved** | Data of other Agents, user configuration, global settings, market cache                                                                                               | —                 |

## Permission Requirements

- Uses the in-process builtin tool `ManageAgent` to list, query, and delete Agents
- The delete action is a high-risk operation; the tool layer will force a user confirmation popup

## Dependencies

- The in-process builtin tool `ManageAgent` (`action='list' | 'get' | 'delete'`)
