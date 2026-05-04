---
name: delete-agent
description: 安全删除指定的智能体及其关联数据。删除前会验证智能体状态，支持可选地删除所有会话历史。Use when 用户需要删除不再使用的智能体。
version: 2.4.2
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
  updated_at: '2026-02-28'
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
      source_hash: sha256:148cd72a6808741e
      translated_by: human
    en-US:
      name: Delete Agent
      short_desc: Safely delete an Agent and its associated data, with multi-step confirmation and optional history cleanup
      description: Safely delete a specified Agent and its associated data. Verifies the Agent's state before deletion and optionally removes all session history. Use when the user needs to delete an Agent that is no longer in use.
      body: ./SKILL.md
      source_hash: sha256:148cd72a6808741e
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
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
---

# delete-agent Skill

## L0: One-line Summary

Safely delete a specified Agent and its associated data, including filesystem, in-memory state, and optionally session history.

## L1: Overview and Use Cases

### Capability Description

delete-agent is a **Meta-Skill** that empowers DesireCore to safely delete other Agents. It performs full pre-flight checks and state validation, and cleans up all associated data.

### Use Cases

- The user wants to clean up Agents that are no longer in use
- Delete temporary Agents created for testing or experimentation
- Free up storage space by deleting old Agents and their history
- The user explicitly asks to "delete" or "remove" a particular Agent

### Core Value

- **Safety**: multiple checks ensure that active Agents are not accidentally deleted
- **Completeness**: cleans up filesystem, in-memory state, message subscriptions, and all associated data
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
│ Return result│ ←── │ Execute the  │ ←── │     Final    │
│  and receipt │     │  delete API  │     │ confirmation │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Phase 1: List Deletable Agents

**Trigger condition**: the user expresses intent to delete but does not specify a particular Agent

**Operation**:

- Call `GET /api/agents` to fetch the list of all Agents
- Filter Agents whose status is `offline` or `error` (safe to delete)
- Annotate Agents whose status is `online`/`busy`/`recovery` (must be stopped first)

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
- User chooses "No" → `deleteRuns=false` (default)

### Phase 4: Final Confirmation

**Confirmation summary**:

```
Please confirm the deletion:
- Target Agent: Legal Advisor Assistant (legal-assistant)
- Scope: Agent + session history (if chosen by the user)
- Risk level: High (irreversible)

Confirm and execute deletion? (yes/no)
```

### Phase 5: Execute the Delete API Call

**API endpoint**: `DELETE /api/agents/{agentId}`

**Query parameters**:

- `deleteRuns`: `'true'` or `'false'`

**Request example**:

```bash
curl -X DELETE "{agentServiceUrl}/api/agents/legal-assistant?deleteRuns=true"
```

> `{agentServiceUrl}` is taken from the Agent Service address in the "Local API" section of the system prompt.

### Phase 6: Return the Operation Result

**Successful response handling**:

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

**Result report template**:

```
✅ Agent "Legal Advisor Assistant" successfully deleted

Cleanup details:
- Filesystem: 2 directories deleted
- Scheduler: all scheduled tasks stopped
- Message subscriptions: 3 subscriptions canceled
- MCP connection: closed
- Session history: 5 records deleted
```

## State Validation and Error Handling

### Pre-deletion State Check

When listing Agents in Phase 1, filter status via `GET /api/agents`:

| Status                         | Deletable?  | Phase 1 Display                |
| ------------------------------ | ----------- | ------------------------------ |
| `offline` / `error`            | ✅ Yes      | Listed under "Deletable"       |
| `online` / `busy` / `recovery` | ❌ Stop first | Annotated "must be stopped"; not entered into the subsequent flow |

**How to stop an active Agent**: send the `agent:shutdown` event via Socket.IO:

```yaml
event: agent:shutdown
data: { 'agentId': '<agent_id>' }
effect: abort all active sessions → stop scheduled tasks → status becomes offline
```

> The Agent cannot directly send Socket.IO events. If the target Agent is active, prompt the user to stop it manually in the UI, or wait until it finishes its current task before deleting.

### API Error Codes

| Code   | Scenario                                                                     | Handling                          |
| ------ | ---------------------------------------------------------------------------- | --------------------------------- |
| 400    | Invalid Agent ID format                                                      | Ask the user to check the Agent name |
| 404    | Agent does not exist                                                         | Inform the user the Agent has already been deleted or the ID is wrong |
| 409    | Agent is currently active (API returns `Cannot delete agent "xxx": currently online`) | Ask the user to stop the Agent in the UI first |
| 500    | Internal server error                                                        | Ask the user to try again later   |

## Deletion Scope

| Category         | Content Deleted                                                                                                                   | Condition              |
| ------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| **Always deleted** | AgentFS directory (config, persona, rules, skills, tools, memory), user preference data, in-memory state (scheduler, queue, message subscriptions, MCP connection), registry entries | Unconditional |
| **Optionally deleted** | Session history, topic index                                                                                         | `deleteRuns=true` |
| **Preserved** | Data of other Agents, user configuration, global settings, market cache                                                                                               | —                 |

## Permission Requirements

- Prefer using the `Bash` tool to call curl against the Agent Service HTTP API to perform the operation
- The API base address is injected into the "Local API" section of the system prompt; reference it directly
- The delete operation requires explicit user confirmation (high-risk operation)

## Dependencies

- Agent Service HTTP API (`DELETE /api/agents/{agentId}`)
- The Local API address declaration in the system prompt
