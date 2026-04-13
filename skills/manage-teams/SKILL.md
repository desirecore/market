---
name: 团队管理
description: 创建和管理 Agent 团队，组织多 Agent 协作。Use when 需要多个 Agent 围绕同一任务协作、需要建立组织架构、或需要组长统一调度分派任务时。
version: 1.2.1
type: procedural
risk_level: medium
status: enabled
tags:
  - group
  - collaboration
  - organization
metadata:
  author: desirecore
  updated_at: '2026-04-13'
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
  short_desc: 创建团队、管理成员、组织多 Agent 协作
  category: productivity
---

# manage-teams 技能

## L0：一句话摘要

创建和管理 Agent 团队，组织多 Agent 围绕共同任务协作。

## L1：概述与使用场景

### 能力描述

manage-teams 是一个**流程型技能（Procedural Skill）**，赋予 DesireCore 创建和管理 Agent 团队的能力。团队是多个 Agent 围绕共同任务协作的组织单元，每个团队有一个组长（supervisor）负责接收需求、拆解任务、分派给成员、汇总结果。

### 使用场景

- 需要多个 Agent 围绕同一任务持续协作（如项目组）
- 需要建立组织架构（部门/团队层级）
- 需要组长统一调度、拆解和分派任务
- 简单一次性委派不够，需要共享上下文的长期协作

### 核心价值

- **组织化协作**：从单点委派升级为团队协作模式
- **灵活管理**：支持临时团队和持久团队两种模式
- **动态调整**：运行时可添加/移除成员、更换组长

## L2：详细规范

## 核心概念

### 团队 vs 单点委派

| 场景 | 推荐方式 | 理由 |
|------|---------|------|
| 一次性简单问题 | `delegate(target, mode='sync')` | 无需组织开销 |
| 需要一个专家处理 | `delegate(target, mode='sync/async')` | 一对一足够 |
| 需要多专家各出意见 | `delegate(targets, mode='fan-out')` | 并行分派无需创建团队 |
| 持续协作 + 共享上下文 | **创建团队** | 团队提供共享 workdir 和组织架构 |
| 组织架构管理 | **创建嵌套团队** | 部门/团队层级关系 |

### 团队类型

- **临时团队（ephemeral）**：任务驱动，完成后可解散。适合项目制协作。
- **持久团队（persistent）**：长期存在，适合部门/团队。临时团队可升级为持久团队。

### 组长唯一性约束

**一个 Agent 只能担任一个团队的组长（TL）。** 这是组织架构的硬性约束：

- 创建团队时，如果调用者已是其他团队的组长，应先卸任原团队组长（`set_supervisor` 指定接替者）再创建新团队
- 不要将已担任组长的 Agent 设为另一个团队的组长
- 一个 Agent 可以同时是某团队的组长和另一个团队的普通成员，但不能同时担任两个团队的组长

### 组长职责

1. 接收用户需求，分析任务复杂度
2. 拆解子任务，决定需要哪些成员参与
3. 使用 `delegate` 工具分派任务（单点或 fan-out）
4. 汇总各成员结果，给出综合回答
5. 根据需要动态调整成员（添加/移除）

## 操作指南

### 创建团队

```
manage_team({
  action: 'create',
  name: '房产评估项目组',
  members: ['legal-advisor', 'finance-advisor', 'real-estate'],
  task: '综合评估目标房产'
})
```

组长默认为调用者（你自己）。创建后你就是这个团队的 supervisor。

### 向团队成员分派任务

**单点委派**（一个成员处理）：
```
delegate({
  target: 'legal-advisor',
  task: '检查该房产的产权状况和法律风险',
  mode: 'sync'
})
```

**扇出委派**（多个成员并行）：
```
delegate({
  targets: ['legal-advisor', 'finance-advisor', 'real-estate'],
  task: '从各自专业角度评估这套房产',
  mode: 'fan-out',
  strategy: 'parallel'
})
```

### 管理成员

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

### 团队生命周期

```
// 任务完成，解散临时团队
manage_team({ action: 'disband', teamId: '...' })

// 或升级为持久团队（长期使用）
manage_team({ action: 'promote', teamId: '...' })
```

## 最佳实践

1. **先评估再创建团队**：简单任务直接 delegate，不要过度组织
2. **成员精简**：只拉入真正需要的专家，避免信息过载
3. **优先团队内成员**：在团队中优先委派给团队内成员。如需团队外专家的一次性意见，可临时 delegate 咨询而无需加入团队；若反复需要，则用 add_member 正式拉入
4. **明确任务描述**：分派时给出清晰的任务描述和背景信息
5. **及时汇总**：收到成员结果后及时汇总，不要让用户等待
6. **动态调整**：发现缺少某领域专家时，用 add_member 补充
7. **用完即散**：临时团队任务完成后及时解散，保持组织整洁
8. **组长唯一**：一个 Agent 只担任一个团队的组长，避免职责分散导致管理混乱
