---
name: manage-teams
description: 创建和管理 Agent 团队，组织多 Agent 协作。Use when 需要多个 Agent 围绕同一任务协作、需要建立组织架构、或需要组长统一调度分派任务时。
version: 1.2.2
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - group
  - collaboration
  - organization
metadata:
  author: desirecore
  updated_at: '2026-04-13'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 团队管理
      short_desc: 创建团队、管理成员、组织多 Agent 协作
      description: >-
        创建和管理 Agent 团队，组织多 Agent 协作。Use when 需要多个 Agent 围绕同一任务协作、需要建立组织架构、或需要组长统一调度分派任务时。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:d773c10ef1cf4ac7
      translated_by: human
    en-US:
      name: Team Management
      short_desc: Create teams, manage members, and organize multi-Agent collaboration
      description: >-
        Create and manage Agent teams to organize multi-Agent collaboration. Use when multiple Agents need to collaborate on the same task, when organizational structure is required, or when a team leader needs to orchestrate and dispatch tasks.
      body: ./SKILL.md
      source_hash: sha256:d773c10ef1cf4ac7
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="mt-a" x1="1" y1="7" x2="16"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#mt-a)" fill-opacity="0.15" stroke="url(#mt-a)"
    stroke-width="1.5"/><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
    fill="url(#mt-a)" fill-opacity="0.1" stroke="url(#mt-a)"
    stroke-width="1.5"/><circle cx="17" cy="8" r="3" fill="url(#mt-a)"
    fill-opacity="0.2" stroke="url(#mt-a)" stroke-width="1.3"/><path d="M23
    21v-1.5a3 3 0 0 0-3-3h-2" stroke="url(#mt-a)" stroke-width="1.3"
    stroke-linecap="round"/><path d="M19.5 1.2L17.5 4M19.5 1.2L21.5 4M17.5
    4h4" stroke="#34C759" stroke-width="1.2" stroke-linecap="round"
    stroke-linejoin="round"/><circle cx="19.5" cy="1.2" r="1"
    fill="#34C759"/><circle cx="17.5" cy="4" r="0.9" fill="#34C759"
    fill-opacity="0.7"/><circle cx="21.5" cy="4" r="0.9" fill="#34C759"
    fill-opacity="0.7"/></svg>
  category: productivity
---

# manage-teams Skill

## L0: One-line Summary

Create and manage Agent teams to organize multiple Agents collaborating around a shared task.

## L1: Overview and Use Cases

### Capability Description

manage-teams is a **Procedural Skill** that gives DesireCore the ability to create and manage Agent teams. A team is an organizational unit in which multiple Agents collaborate around a shared task; each team has a supervisor responsible for receiving requirements, decomposing tasks, dispatching work to members, and consolidating results.

### Use Cases

- Multiple Agents need to collaborate continuously on the same task (e.g., a project group)
- An organizational hierarchy is required (departments / team levels)
- A supervisor is needed to centrally orchestrate, decompose, and dispatch tasks
- Simple one-off delegation is insufficient and long-term collaboration with shared context is required

### Core Value

- **Organized collaboration**: upgrade from point-to-point delegation to a team collaboration model
- **Flexible management**: supports both ephemeral and persistent team modes
- **Dynamic adjustment**: members can be added/removed and supervisors swapped at runtime

## L2: Detailed Specification

## Core Concepts

### Teams vs. Single-point Delegation

| Scenario | Recommended Approach | Rationale |
|------|---------|------|
| One-off simple problem | `delegate(target, mode='sync')` | No need for organizational overhead |
| Need a single expert to handle | `delegate(target, mode='sync/async')` | One-to-one is sufficient |
| Need multiple experts to weigh in | `delegate(targets, mode='fan-out')` | Parallel dispatch without creating a team |
| Continuous collaboration + shared context | **Create a team** | Teams provide a shared workdir and structure |
| Organizational hierarchy management | **Create nested teams** | Department / team hierarchy relationships |

### Team Types

- **Ephemeral team**: task-driven, can be disbanded after completion. Suitable for project-based collaboration.
- **Persistent team**: long-lived, suitable for departments / teams. Ephemeral teams can be promoted to persistent.

### Supervisor Uniqueness Constraint

**An Agent can only serve as the supervisor (TL) of a single team.** This is a hard constraint of the organizational structure:

- When creating a team, if the caller is already a supervisor of another team, they must first step down from the original team (use `set_supervisor` to designate a successor) before creating the new team
- Do not assign an Agent who already serves as supervisor to be the supervisor of another team
- An Agent can simultaneously be the supervisor of one team and a regular member of another, but cannot be supervisor of two teams at once

### Supervisor Responsibilities

1. Receive user requirements and analyze task complexity
2. Decompose subtasks and decide which members are needed
3. Use the `delegate` tool to dispatch tasks (single-point or fan-out)
4. Consolidate results from members and produce an integrated answer
5. Dynamically adjust members (add/remove) as needed

## Operations Guide

### Create a Team

```
manage_team({
  action: 'create',
  name: '房产评估项目组',
  members: ['legal-advisor', 'finance-advisor', 'real-estate'],
  task: '综合评估目标房产'
})
```

The supervisor defaults to the caller (you). After creation, you are the supervisor of this team.

### Dispatch Tasks to Team Members

**Single-point delegation** (one member handles it):
```
delegate({
  target: 'legal-advisor',
  task: '检查该房产的产权状况和法律风险',
  mode: 'sync'
})
```

**Fan-out delegation** (multiple members in parallel):
```
delegate({
  targets: ['legal-advisor', 'finance-advisor', 'real-estate'],
  task: '从各自专业角度评估这套房产',
  mode: 'fan-out',
  strategy: 'parallel'
})
```

### Manage Members

```
// 添加成员
manage_team({ action: 'add_member', teamId: '...', agentId: 'new-agent' })

// 批量添加成员
manage_team({ action: 'add_members', teamId: '...', members: ['agent-a', 'agent-b'] })

// 移除成员
manage_team({ action: 'remove_member', teamId: '...', agentId: 'old-agent' })

// 批量移除成员
manage_team({ action: 'remove_members', teamId: '...', members: ['agent-a', 'agent-b'] })

// 更换组长
manage_team({ action: 'set_supervisor', teamId: '...', agentId: 'new-leader' })
```

### Team Lifecycle

```
// 任务完成，解散临时团队
manage_team({ action: 'disband', teamId: '...' })

// 或升级为持久团队（长期使用）
manage_team({ action: 'promote', teamId: '...' })
```

## Best Practices

1. **Evaluate before creating a team**: simple tasks should be delegated directly without over-organizing
2. **Keep membership lean**: only bring in the experts truly needed to avoid information overload
3. **Prefer in-team members**: within a team, prefer delegating to its members. For one-off opinions from outside experts, ad-hoc `delegate` consultation is fine without joining the team; if needed repeatedly, formally bring them in via `add_member`
4. **Clear task descriptions**: provide a clear task description and background information when dispatching
5. **Consolidate promptly**: synthesize member results promptly — do not keep the user waiting
6. **Adjust dynamically**: when missing a domain expert, supplement with `add_member`
7. **Disband after use**: disband ephemeral teams promptly when their task is done to keep the organization tidy
8. **One supervisor per Agent**: an Agent should only serve as supervisor of one team to avoid management chaos from divided responsibilities
