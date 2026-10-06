---
license: "MIT"
name: manage-teams
description: 创建和管理 Agent 团队，组织多 Agent 协作。Use when 需要多个 Agent 持续协作、建立组织架构，或发布、安装和同步团队仓库时。
version: 1.4.0
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
  updated_at: '2026-10-06'
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
        创建和管理 Agent 团队，组织多 Agent 协作。Use when 需要多个 Agent 持续协作、建立组织架构，或发布、安装和同步团队仓库时。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:778c6fb42f550a02
      translated_by: human
    en-US:
      name: Team Management
      short_desc: Create teams, manage members, and organize multi-Agent collaboration
      description: >-
        Create and govern Agent teams. Use when multiple Agents need sustained collaboration, an organizational hierarchy, or a team repository must be published, installed, or synchronized.
      body: ./SKILL.md
      source_hash: sha256:778c6fb42f550a02
      translated_by: human
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
  required_client_version: 10.0.178
---

# manage-teams Skill

## L0: One-line Summary

Use `ManageTeam` to inspect, create, and govern Agent teams, with the required checks before organizational changes or remote synchronization.

## L1: When to Use

Use a team when:

- multiple Agents need sustained collaboration around one task and a shared team workdir;
- a stable supervisor, membership, or parent-child organizational structure is required;
- a team repository must be published, installed, or synchronized.

Do not create a team when:

- one expert is needed once: use `Delegate(mode="sync" | "async")`;
- several experts only need to provide one-off opinions: use `Delegate(mode="fan-out")`;
- the work is temporary file exploration: use a Worker instead of creating a lasting organization.

A team defines organization, shared directories, and governance. Actual work is still dispatched to members with `Delegate`.

## L2: Execution Specification

### 1. Inspect Before Mutating

- If `teamId` is unknown, call `ManageTeam(action="list")` first.
- Before modifying, disbanding, or synchronizing a team, call `ManageTeam(action="get", teamId=...)` and verify its name, type, supervisor, members, local repository directory, and remote state.
- Never guess a path under `~/.desirecore`; use only the absolute repository path returned by `get`.
- `list` can filter by `parentTeamId`. With `tree=true`, `teamId` selects the subtree root and `parentTeamId` is ignored.

### 2. Action Reference

| action | Purpose | Key parameters and notes |
|---|---|---|
| `list` | List teams or an organization tree | `parentTeamId?`, `tree?`, `teamId?` |
| `get` | Inspect one team and its repository path | `teamId` |
| `create` | Create an ephemeral team | `name` or `task`; `supervisor?`, `members?`, `memberRouting?`, `parentTeamId?`, `workdirMode?` |
| `add_member` | Add one member | `teamId`, `agentId` |
| `add_members` | Add members in a batch | `teamId`, `members` |
| `remove_member` | Remove one member | `teamId`, `agentId` |
| `remove_members` | Remove members in a batch | `teamId`, `members` |
| `set_supervisor` | Replace the supervisor | `teamId`, `agentId` |
| `set_member_source` | Declare where a member Agent comes from | `teamId`, `agentId`, `memberSource`; `git` needs `url` (https, will be cloned) and `ref` (defaults to `main`), `registry` needs `id`+`version`, `core`/`local` need nothing else |
| `update` | Partially update team configuration | `teamId`; supports `name/type/isolation/parentTeamId/description/avatar/avatarImage` |
| `promote` | Promote an ephemeral team to persistent | `teamId`; one-way and never implicit |
| `disband` | Disband a team | `teamId`; enters approval; preserves a full archive, requiring workdir binding and content review on restore |
| `fork_team` | Install a team from a remote repository | `url`; `name?`, `installMembers?`; enters approval |
| `push` | Push a local team to its connected remote | `teamId`; enters approval |
| `pull` | Pull and validate a team from its connected remote | `teamId`; enters approval |
| `add_remote` | Configure or replace a publishing destination | `teamId`, `url`; optional `connectionId`, `branch`, `isPrivate`; does not create a repository |
| `remove_remote` | Remove remote configuration and the local connection binding | `teamId`; leaves the remote repository intact |
| `install_members` | Install or repair members from the existing lock | `teamId`; optional `forceUpdate`, default false |
| `upgrade_members` | Resolve a new lock and attempt safe updates | `teamId`; optional `forceUpdate`, default true; preserves local edits and commits |
| `release` | Create a local version or publish one exact version | `teamId`; `push` defaults to false, optional `changelogEntry`, `expectedCommit`; retry with `releaseTag` |

### 3. Create a Team

Before creation:

1. Every Agent in `supervisor` and `members` must already exist. Verify IDs with `ManageAgent(action="list" | "get")`; create or install a missing Agent through its corresponding Agent Skill before creating the team.
2. The DesireCore core Agent, `desirecore`, cannot be a supervisor. When the core Agent initiates creation, it must explicitly choose a regular Agent as `supervisor`.
3. Normally do not add `desirecore` as a member. Reach core capabilities through `Delegate` instead.
4. One Agent may supervise only one team. If the intended supervisor already leads another team, assign a successor there first.

Choose the workdir mode deliberately:

- `merged` (default): the shared team directory is primary while member and global workdirs remain available;
- `team_only`: exposes only the shared team directory, for high-reliability work where every member must operate on the same project. It does not delete member workdir configuration.

Use `memberRouting` to express routing intent without pinning a Provider or model:

```json
{
  "supervisor-agent": {
    "tier": "flagship",
    "requiredCapabilities": ["reasoning"],
    "reasoning": "high"
  },
  "member-agent": {
    "tier": "balanced"
  }
}
```

- keys must belong to the selected `supervisor` or `members`;
- Agents using a fixed model must not appear in `memberRouting`;
- omitted Smart members retain their current routing profile; the concrete Provider/model is resolved when that member executes work.

Example:

```json
{
  "action": "create",
  "name": "Contract Review Project",
  "supervisor": "legal-lead",
  "members": ["contract-reviewer", "risk-analyst"],
  "task": "Review contracts continuously and consolidate risks",
  "workdirMode": "team_only"
}
```

### 4. Change Organization and Configuration

- Prefer batch member actions to avoid observable intermediate states.
- `set_supervisor` uses `agentId`; first verify that the Agent does not already supervise another team.
- `set_member_source` declares provenance, it does not move files. A team whose roster still contains a `local` member is **not distributable** — `members.lock.json` cannot pin an ID that exists only on this machine, so a fork elsewhere would silently come up short a member. Switch each member to `git` or `registry` before publishing. The action resolves and writes the lock automatically; inspect its receipt. It cannot change a member's `role`; use `set_supervisor` for that.
- `update` is a patch: omitted fields remain unchanged.
- `parentTeamId: null` detaches the team and makes it top-level; an empty string is invalid.
- `type` only allows `ephemeral → persistent`. Repeating the current value is idempotent; use `promote` for an explicit upgrade.
- `isolation`: `soft` uses shared session isolation; `hard` uses independent Agent copies.
- `description` is the marketplace-facing team description, not the `task` supplied at creation.

Use a declared avatar with:

```json
{
  "action": "update",
  "teamId": "team-id",
  "avatar": { "char": "CR", "color": "purple" }
}
```

For an image avatar, use `avatarImage.source` with `dc-media://<mediaId>`, a bare `mediaId`, or an image path inside the workdir. PNG/JPEG/WebP are supported. Do not pass an HTTP(S) URL or base64. Remove the image with `{ "remove": true }`; `remove` and `source` are mutually exclusive.

### 5. Team Lifecycle

- Disband an ephemeral team after its project is complete so the organization does not accumulate stale teams.
- Use `promote` only for an explicit long-term collaboration requirement; promotion is one-way.
- `disband` archives the complete team directory and ends its local workdir binding, even without Git initialization. Archive failure preserves the original data and reports failure. The action enters approval; the caller's approval mode determines whether a human card appears. To restore, first check that the team ID is free, then bind the workdir and approve its content again.

### 6. Team Repository and Remote Synchronization

The team directory is a Git repository containing governance data such as `team.json`, member locks, and `shared/rules.md`.

For local Git work:

1. obtain the absolute repository path with `get`;
2. run `status/log/diff/add/commit/tag` with Bash in that directory;
3. after the local commit is complete, call `ManageTeam(action="push")`.

Remote `fork_team/push/pull` must go through `ManageTeam` because it enforces team Schema validation, roster consistency, the core-Agent supervisor prohibition, workspace types, out-of-bounds symlink checks, and approval. Do not bypass those controls with raw `git push/pull`. This rule is not based on an assumption that Agents can never access credentials.

- `push/pull` require a remote configuration. Use `add_remote` to configure the destination and an existing connection when needed. Client team settings are also available; the Agent chooses the configuration path.
- Locally created and forked teams do not inherit a directly pushable remote configuration by default.
- `fork_team` defaults to `installMembers=true`; a same-ID local Agent that has diverged from its lock is protected and skipped rather than overwritten.
- `pull` may replace local team configuration. Inspect local state first and identify the target remote in the approval card.

Release and member versions:

- `release` defaults to a local version. Set `push=true` for publication; approval identifies the target and version. Only the branch and this exact release tag are pushed, never all tags or private backup/archive refs.
- Inspect the team with `get`; constrain a new release HEAD with `expectedCommit`. Inspect `tag/version/commitHash` and `branchPushed/tagPushed/pushed` separately.
- After network failure or an unknown remote outcome, inspect the remote and retry with the returned `releaseTag`; do not create another version. Omit `changelogEntry` on retries.
- `install_members` follows the exact existing lock. `upgrade_members` resolves declarations and attempts safe updates to new pins. Both preserve local edits and commits, avoid downgrades, and do not approve installed content.
- `complete=false` or `outdated/diverged/failed/unreachable` means members remain unaligned. Neither `success=true`, skipped counts nor zero failures proves all members were upgraded. Inspect each receipt before choosing repairs.
- Conflicting pins for an Agent shared by multiple teams do not authorize overwriting a local fork; preserve data and report the conflict.
- Remote actions, remote-source declarations and destination configuration enter approval. `ask-external` retains approval for them; `allow-all` respects the user's full trust in the acting Agent.

### 7. Dispatch and Finish

After team creation, dispatch work to the supervisor or members with `Delegate`:

- one member: `Delegate(target=..., mode="sync" | "async", teamId=...)`;
- several members: `Delegate(targets=[...], mode="fan-out", teamId=...)`;
- prefer team members for sustained collaboration; a one-off outside opinion does not require membership.

Report the team name and ID, type, supervisor and members, workdir mode, organizational changes, and whether remote operations completed. Never expose credentials or a remote URL containing a token.

### 8. Failure Recovery

- `Agent does not exist`: verify the ID; create or install the Agent, then retry.
- `Core Agent cannot supervise`: explicitly choose a regular Agent as `supervisor`.
- `Supervisor already leads another team`: run `set_supervisor` on the existing team before retrying.
- `Remote not configured`: use `add_remote` to configure the destination, or use client team settings; do not guess a hidden API.
- Local content changed or conflicts exist: obtain the directory with `get`, inspect Git state, preserve user changes, and only then decide whether to commit, pull, or retry.
- If this Skill is missing or disabled, the minimal operation may still be executed from the `ManageTeam` action/parameter Schema and tool error messages. Never bypass the tool by editing AgentFS directly.
