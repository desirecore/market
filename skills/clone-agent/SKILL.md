---
name: clone-agent
description: >-
  完整克隆现有智能体为独立本地副本，并安全处理私有记忆、偏好、关系与团队分发影响。Use when 用户要求复制、克隆或基于现有 Agent 创建独立变体。
version: 1.0.0
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - agent
  - clone
  - meta
metadata:
  author: desirecore
  updated_at: '2026-08-25'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 克隆智能体
      short_desc: 完整复制现有智能体为独立本地副本，可选继承用户私有数据
      description: >-
        完整克隆现有智能体为独立本地副本，并安全处理私有记忆、偏好、关系与团队分发影响。Use when 用户要求复制、克隆或基于现有 Agent 创建独立变体。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:d97c5736c37e1bcf
      translated_by: human
    en-US:
      name: Clone Agent
      short_desc: Clone an existing Agent into an independent local copy with optional private user data
      description: >-
        Clone an existing Agent into an independent local copy while safely handling private memory, preferences, relationships, and team distribution impact. Use when the user asks to copy, clone, or create an independent variant from an existing Agent.
      body: ./SKILL.md
      source_hash: sha256:d97c5736c37e1bcf
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="cl-a" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop offset="1" stop-color="#AF52DE"/></linearGradient></defs><rect x="7" y="7" width="13" height="13" rx="3" fill="url(#cl-a)" fill-opacity="0.12" stroke="url(#cl-a)" stroke-width="1.5"/><path d="M16 7V6a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v7a3 3 0 0 0 3 3h1" stroke="url(#cl-a)" stroke-width="1.5" stroke-linecap="round"/><path d="M11 13h5m-2.5-2.5V16" stroke="#34C759" stroke-width="1.8" stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.96
---

# clone-agent Skill

## L0: One-Sentence Summary

Clone an existing Agent into an independent local copy while explicitly handling private user data and team distribution impact.

## L1: Overview

Use this skill when the user wants to copy an Agent or create an independent variant that keeps the source Agent's persona, principles, skills, and configuration. The clone receives a new ID and UUID. It is not an empty-template create operation and never creates a fork in GitHub, Gitee, or another code hosting account.

## L2: Detailed Specification

Flow: decide whether cloning is appropriate → inspect the source Agent → confirm the clone name and private-data choices → call ManageAgent → report the clone's local and distribution properties.

### 1. Choose Clone or Create

- Use `clone` when the user wants to retain an existing Agent's persona, rules, skills, and configuration in an independent copy or variant.
- Use `create-agent` when the user wants a new Agent in a similar domain but with independently designed behavior.
- Do not recreate an Agent merely to make it “similar”; `create` produces a fresh template and does not inherit the source capability package.

### 2. Confirm the Source

If the user did not provide an exact ID, call `ManageAgent(action='list')`; use `ManageAgent(action='get', id)` when name, status, or description needs verification.

The tool rejects these cases and they must not be bypassed:

- The core `desirecore` Agent cannot be cloned.
- An Agent whose routing was fixed by the human model selector cannot be cloned autonomously; ask the user to use the UI.
- The source Agent does not exist.

### 3. Name and Private User Data

- `name` is optional; the default is “Source Name (Copy)”.
- Private user data is not copied by default. Pass `copyUserData` only when the user explicitly asks the clone to inherit memory, preferences, or relationship state.
- `copyUserData.memory` copies private memory between the user and the source Agent.
- `copyUserData.preferences` copies user preferences for the source Agent.
- `copyUserData.relationship` copies the user-Agent relationship profile.

Before enabling any of these fields, explain the exact scope and obtain confirmation. Do not interpret “full clone” as consent to copy private user data.

### 4. Execute

Basic call:

```json
{
  "action": "clone",
  "id": "source-agent-id",
  "name": "New Copy Name"
}
```

When private-data copying was explicitly confirmed:

```json
{
  "action": "clone",
  "id": "source-agent-id",
  "name": "New Copy Name",
  "copyUserData": {
    "memory": true,
    "preferences": false,
    "relationship": false
  }
}
```

ManageAgent performs a local-only copy, applies both caller and source Provider ceilings, registers the new Agent, and compensates by removing an incomplete clone if registration fails. Never use a git hosting fork, local HTTP API, or direct AgentFS directory copy instead.

### 5. Receipt and Team Impact

After success, report:

- The new Agent ID and that it is ready for Delegate / ManageTeam.
- Which private-data categories were actually copied; missing source categories are skipped, so trust the tool receipt rather than the request.
- The clone has `local` origin. Adding it to a team makes that team `distributable=false`. If the team must later be published or forked by others, use an Agent published to a remote repository instead.

On failure, follow the tool's exact result. If compensation cleanup also failed, preserve the evidence and clearly request human governance rather than retrying blindly.
