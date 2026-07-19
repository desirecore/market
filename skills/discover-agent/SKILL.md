---
name: discover-agent
description: 根据用户需求推荐最匹配的智能体，展示候选列表并引导选择。Use when 用户描述需求但不确定该找哪个智能体帮忙，或想浏览可用的智能体。
version: 2.6.3
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - discovery
  - recommendation
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
      name: 发现智能体
      short_desc: 根据需求描述智能推荐最匹配的智能体，引导快速选择
      description: 根据用户需求推荐最匹配的智能体，展示候选列表并引导选择。Use when 用户描述需求但不确定该找哪个智能体帮忙，或想浏览可用的智能体。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:72159b331107dfb6
      translated_by: human
    en-US:
      name: Discover Agent
      short_desc: Intelligently recommend the best-matching Agent based on the user’s need description, and guide quick selection
      description: >-
        Recommend the best-matching Agent based on the user’s needs, show a candidate list, and guide selection. Use when the user describes a need but is unsure which Agent to ask for help, or wants to browse available Agents.
      body: ./SKILL.md
      source_hash: sha256:72159b331107dfb6
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-19'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="da-a" x1="2" y1="2" x2="22"
    y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"
    stop-opacity="0.12"/><stop offset="1" stop-color="#007AFF"
    stop-opacity="0.06"/></linearGradient></defs><circle cx="12" cy="12" r="10"
    fill="url(#da-a)" stroke="#AF52DE" stroke-width="1.5"/><path d="M16.24
    7.76l-1.8 5.41a2 2 0 0 1-1.27 1.27L7.76 16.24" fill="#FF9500"
    fill-opacity="0.85"/><path d="M7.76 16.24l1.8-5.41a2 2 0 0 1 1.27-1.27L16.24
    7.76" fill="#AF52DE" fill-opacity="0.7"/><circle cx="12" cy="12" r="1.5"
    fill="white" stroke="#AF52DE" stroke-width="0.8"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.90
---

# discover-agent skill

## L0: One-Sentence Summary

Match and recommend the most suitable Agent among registered Agents based on the user's need description.

## L1: Overview

Procedural skill: understand the need → retrieve with `ManageAgent(action='list')` → semantic match scoring → rank and present → guide selection; on no match, hand off to create-agent automatically. Applies when the user doesn't know which Agent to pick, wants to browse available Agents, is a new user getting oriented, or is unhappy with the current Agent and wants an alternative. Its value is what the tool can't give: semantic need matching (not keyword search), candidate ranking and presentation, and the create hand-off on no match. `list` / `get` are read-only, approval-free.

## L2: Detailed Spec

Flow: need understanding → retrieval → match evaluation → ranking → presentation → guided selection.

### Stage 1: Need Understanding

Trigger (any): user says "find me a… / is there a… / who can help me…", describes a task without naming an Agent, "which Agents are there", or the system detects a need that mismatches the current Agent. Extract dimensions from the description: `domain` (legal/finance/tech/education), `task_type` (consult/review/analyze/create), `keywords` (contract/report/code/paper…), `urgency` (routine/urgent).

### Stage 2: Retrieval

`ManageAgent(action='list')` fetches all registered Agents (returns a compact list with name / id / status / description). Filtering: by default show non-offline Agents; offline ones appear only as a fallback when there's no better candidate; exclude internal system Agents (e.g. DesireCore itself) unless the user explicitly asks.

### Stage 3: Match Evaluation

Judge match with LLM semantic understanding (not a formula): relevance of description / persona to the need, association of skills to the task type, domain fit, status availability (online preferred). Presentation tiers: strong match → mark "recommended", partial → "possibly relevant", no clear relation → don't show.

### Stage 4: Ranking

Descending by overall score; ties broken by online status; show the most relevant few — you decide how many by relevance, avoiding flooding the screen.

### Stage 5: Presentation

- **With matches**: list candidates, each with name, description, key skills, status, and match score; ask the user to choose or refine the need. E.g. "1. Legal Advisor (92%) — contract review and legal risk assessment; skills: contract review / risk assessment / legal research; online".
- **No match**: report that none were found and offer three options — retry with a more specific description / create a new specialized Agent (hand off to create-agent) / browse all.
- **Browse mode** (user wants to see all): list name + description grouped by online / offline, and ask whether to view details of any.

### Stage 6: Guided Selection

- Chose an Agent → switch to that Agent's conversation, passing the user's need context (source / target / user_intent).
- Wants more detail → `ManageAgent(action='get', id)` for details (name / description / status / version / skill count / tool count / Git status); present the key info in natural language or a table and ask whether to chat.
- Unhappy with candidates → guide the user to refine the need or suggest creating a new Agent.
- Chose "create new" → invoke the create-agent skill, passing the gathered requirements.

### Collaboration and Error Handling

- Collaboration: on no match, hand off to create-agent (pass the need as initial info); on a successful match, optionally create a task and assign it to the target Agent.
- Errors: tool call fails → report error and suggest retry; empty Agent list → guide the user to create the first Agent; overly vague need → ask follow-ups and offer domain options; `get` returns "Agent not found: <id>" → fall back to `list` to reconfirm available Agents; recommended Agent in an abnormal state → mark the status and suggest picking an online one.
- `list` / `get` are read-only, approval-free, and risk-free; always done via `ManageAgent`.
