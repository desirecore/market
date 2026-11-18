---
license: MIT
name: delete-agent
description: Archive unused Agents, list local archives and restore them through
  ManageAgent. Only the user can permanently delete an Agent through the
  interface.
version: 2.7.0
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - agent
  - deletion
  - meta
metadata:
  author: desirecore
  updated_at: '2026-11-17'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 删除与恢复智能体
      short_desc: 归档或恢复智能体，保留历史并报告团队和调度事项
      description: 通过 ManageAgent 归档不再使用的智能体、查询本机归档与恢复；永久删除仅由用户在界面完成。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:4f5aae9c80b22ee9
      translated_by: ai:gpt-6
      translated_at: '2026-11-16'
    en-US:
      name: Archive and Restore Agents
      short_desc: Archive or restore Agents, keep history, and report team and
        schedule follow-up
      description: Archive unused Agents, list local archives and restore them through
        ManageAgent. Only the user can permanently delete an Agent through the
        interface.
      body: ./SKILL.md
      source_hash: sha256:4f5aae9c80b22ee9
      translated_by: ai:gpt-6
      translated_at: '2026-11-16'
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><defs><linearGradient id="da2-a" x1="2" y1="7" x2="16"
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
  required_client_version: 10.0.204
---

# delete-agent Skill

## L0: One-Sentence Summary

Archive unused Agents or restore them from local archives, preserve conversation history, and report team and schedule follow-up from actual receipts.

## L1: Overview

Use this for deleting an Agent, recovering an accidental deletion, or inspecting local archives. Use `ManageAgent`, without local HTTP calls or manually moving archive directories. Deletion archives the Agent: it can be recovered locally, does not expire automatically, and is excluded from subsequent backups and migration packages. Only the user can permanently delete it through Settings → Data & Privacy → Archive.

## L2: Detailed Specification

### Archive an Agent

When the target is unspecified, list candidates with `ManageAgent(action='list')`; use `get` for details. Verify the name and ID, explaining that history is retained and teams it leads are archived too. Do not reconfirm a clearly authorized target; clarify ambiguous targets first. The tool protects built-in Agents, the caller itself, and active Agents. Stop an active target through the interface or wait until it is idle.

Call `ManageAgent(action='delete', id='example-agent')`. Do not ask whether to delete history or pass `deleteRuns=true`: the new tool rejects it. Approval follows the caller's approval mode; do not promise a dialog. Report the actual archive identifier, team and worktree dispositions, and warnings. Unbinding preserves worktrees and branches. Retain `archiveId` for recovery when needed; do not claim archiving reclaims all disk space.

### List Archives and Restore

Use `ManageAgent(action='list_archived')` to inspect local archives. This is read-only and does not roll forward or repair incomplete transactions. Explain the actual `phase`, `restorable`, and `originalIdOccupied` values. Query again when an identifier is missing or an archive has disappeared; never invent an `archiveId`.

For a restorable entry, call `ManageAgent(action='restore', archiveId='identifier from the list')`. If the original ID is occupied, obtain the user's choice of a new name and pass `name`; never overwrite an existing Agent. When the original ID is free, providing `name` renames without forcing an ID change. `restoreLedTeams` defaults to `true`; pass `false` if the user wants its led teams to remain archived.

An occupied original ID means restoration under a new ID: conversation history remains under the original ID, schedules are not restored, and absolute-path environments in private skills may need preparation again. Explain these consequences before execution. Restoration has the same approval tier as creation, with no additional confirmation. The owner still validates identity and permissions; do not supply a fabricated `userId` or impersonate the official Renderer.

### Complete the Handoff from the Receipt

`agentId` identifies the actual restored Agent. `idChanged` and `runsAttached` describe identity and history attachment. Report `teams.restored`, `teams.pending`, `teams.memberOf`, and `warnings`. Led teams not restored together need handling in the archive page's Teams segment; former memberships are not reinstated.

Schedules do not enable automatically. `schedules.reenablable` can be enabled through the existing update entry; `recreateRequired` must be recreated, with scripts uploaded again; `dropped` lists definitions not restored under a new ID. Old instance authorization does not revive. MCP OAuth, App links, and worktree bindings are not reinstated. Agent restoration does not establish that all teams, schedules, or authorizations have been restored.

### Failures and Permanent Deletion

Preserve returned error codes, states, and warnings. `AGENT_RESTORE_ID_OCCUPIED` requires `name` or another query to inspect concurrent occupation. Do not bypass `AGENT_RESTORE_USER_MISMATCH` by claiming another identity. Follow the actual failure for incomplete, corrupt, or cleanup-pending archives; do not remove containers yourself. Verify unknown results through the list before retrying a restore or creating another Agent.

If the user explicitly requests permanent deletion or history removal, guide them to the interface to review credential files and history scope and complete confirmation. Do not attempt `purge`, directory deletion through Bash, or Renderer-protected HTTP endpoints. Existing backup copies are unaffected by permanent deletion. Whether marketplace uninstall is recoverable depends on the actual client capability; this Skill does not promise later implementation stages.
