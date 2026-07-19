---
name: delete-agent
description: 安全删除指定的智能体及其关联数据。删除前会验证智能体状态，支持可选地删除所有会话历史。Use when 用户需要删除不再使用的智能体。
version: 2.5.1
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
  updated_at: '2026-07-19'
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
      source_hash: sha256:7037971bb67e0953
      translated_by: human
    en-US:
      name: Delete Agent
      short_desc: Safely delete an Agent and its associated data, with multi-step confirmation and optional history cleanup
      description: Safely delete a specified Agent and its associated data. Verifies the Agent's state before deletion and optionally removes all session history. Use when the user needs to delete an Agent that is no longer in use.
      body: ./SKILL.md
      source_hash: sha256:7037971bb67e0953
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-19'
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

# delete-agent skill

## L0: One-Sentence Summary

Safely delete a specified Agent and its associated data (filesystem, in-memory state, optional conversation history).

## L1: Overview

Meta-skill: list candidates → confirm intent (irreversible) → ask whether to delete history → execute via `ManageAgent(action='delete')`. Its value is what the tool can't give: candidate filtering with status guidance, and intent confirmation before deletion. The tool guarantees the multi-way refusals (core agent / self / active state) and team cascading.

## L2: Detailed Spec

Flow: list deletable Agents → confirm intent and target → ask whether to delete history → execute → receipt.

### Stage 1: List Candidates

When the user hasn't named a specific Agent, fetch the list with `ManageAgent(action='list')` and group by status: `offline` / `error` are safe to delete; `online` / `busy` / `recovery` are marked "stop first" (the tool will refuse them) and excluded from the rest of the flow. For details, use `ManageAgent(action='get', id)`. E.g.:

```
Deletable: Legal Advisor (legal-assistant, offline), Test Bot (test-bot, offline)
Stop first: Data Analyst (data-analyst, online)
```

### Stage 2: Confirm Intent

Confirm the target Agent (name/ID) with the user, **explicitly state it is irreversible** (config, skills, tools will be permanently deleted), show basic info, and wait for confirmation.

### Stage 3: Ask About Deletion Options

Ask whether to also delete all of the Agent's conversation history: yes → `deleteRuns=true`; no → `deleteRuns=false` (default, omittable, keeps history).

### Stage 4: Execute Deletion

Before the call, tell the user "the system will pop up a confirmation window; please confirm there" (delete is force-confirmed at the tool layer). Execute:

```
ManageAgent(action='delete', id='legal-assistant', deleteRuns=true)
```

After confirmation the deletion completes, including team cascading: a team whose supervisor is the target is disbanded; membership is removed where the target is a member.

### Stage 5: Receipt

From the tool's return (cleaned paths, deleted run count, memory-cleanup details), produce a user-friendly report (no internal paths), e.g. "✅ Deleted XXX; cleaned filesystem / scheduler / subscriptions / MCP / N conversation records / team cascade".

### Deletion Scope and Boundaries

- **Always deleted**: AgentFS directory (config/persona/rules/skills/tools/memory), user preference data, in-memory state (scheduler/queue/message subscriptions/MCP connections), registry entry. **Optionally deleted** (`deleteRuns=true`): conversation history and topic index. **Team cascade** (automatic): supervisor → disband team, member → remove. **Kept**: other Agents, user config, global settings, market cache.
- Explain tool refusals to the user with a next step: the core agent (desirecore / core / bound UUID) cannot be deleted; the caller can't delete itself; active state (online/busy/recovery) needs stopping in the UI first or waiting until idle; a non-existent ID means the Agent is already gone or the ID is wrong.
- Always done via `ManageAgent` (`action='list' | 'get' | 'delete'`); delete is a high-risk operation and is force-confirmed at the tool layer.
