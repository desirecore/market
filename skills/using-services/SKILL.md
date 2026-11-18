---
license: "MIT"
name: using-services
description: >-
  Find and call HTTP/MCP services registered in the global Apps & Services
  catalog, or connect a catalog MCP service to this Agent. For an MCP server
  this Agent already has, skip this skill and search ToolCatalog by the server
  ID. 调用目录里登记的 API、查找本 Agent 尚未接入的现成服务时使用。
version: 1.1.0
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - service
  - catalog
  - http
  - mcp
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
      name: 使用服务
      short_desc: 发现并调用全局目录中已注册的服务
      description: >-
        查找并调用全局「应用与服务」目录里登记的 HTTP/MCP 服务，或把其中的 MCP 服务接入本 Agent；本 Agent 已接入的 MCP 服务端不用本技能，按服务端 ID 用 ToolCatalog 检索其工具。Use when 用户要调用目录里的 API 或找尚未接入的现成服务。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Using Services
      short_desc: Discover and invoke registered services from the catalog
      description: >-
        Find and call HTTP/MCP services registered in the global Apps & Services catalog, or connect a catalog MCP service to this Agent. For an MCP server this Agent already has, skip this skill and search ToolCatalog by the server ID. Use when the user asks to call an API from the catalog or to find an existing service this Agent has not connected yet.
      body: ./SKILL.md
      translated_by: human
      source_hash: sha256:1ed16897ea44ed91
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="9" width="6" height="6" rx="1.5"/><rect x="15" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/><path d="M9 11.5h3.5V6H15"/><path d="M9 12.5h3.5V18H15"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# using-services Skill

## Native applications and outward protocols

**DesireCore Control** is a `native-app` for external agents, not an installed internal MCP service. The presence of its dashboard or outward `/mcp` endpoint does not authorize this Agent to invoke it through `using-services`, register it, or bypass GUI approval. Use `app-install-manager` (1.5.2 or newer) for its App lifecycle and the governed `ControlDesireCoreGui` for runtime GUI access. An App installation must not mint an internal service or `svc-*` skill.

## L0: One-line Summary

Teach the Agent how to look up and call services from the global
"Apps & Services" catalog.

## L1: Overview

The "Apps & Services" catalog stores all registered HTTP/MCP services. This
meta-skill is your manual for **finding** the right service and **invoking**
it correctly. Each non-trivial registered service also has its own
`svc-<id>` Skill auto-generated from its operations — prefer that when it
exists; this meta-skill is the fallback for ad-hoc discovery.

### When to use

- The user asks you to do something that might already have a registered service
  (e.g. "search the product database", "send a notification")
- You see `svc-<id>` Skill in your available skills list — activate it directly
- You need to call an HTTP API and want to check if it's been registered (to
  benefit from governance, credential injection, and audit)

### When NOT to use

- The user gives you a one-off URL to fetch — use `HttpRequest` directly
- You already have the per-service `svc-<id>` Skill activated — follow it
  instead, it's more specific
- The named service is already one of this Agent's MCP servers — find its
  tools as in Step 0; no catalog lookup is needed

## L2: How to discover and call

### Step 0 — Check whether it is already one of this Agent's MCP servers

A service the user names ("use the xxx service") may already be one of this
Agent's MCP servers; the server ID is the name it was connected under. Then no
catalog lookup is needed:

1. If the system prompt lists the MCP servers available this turn (only newer
   clients have that section), check there first; a missing section does not
   mean the server is not connected.
2. Search `ToolCatalog` by the server ID, for example
   `ToolCatalog(query="<server ID>", max_results=20)`. Put only the ID itself in
   the query, not a wildcard such as `<ID>__*`: the search has no wildcards and
   would find nothing. If the number of results equals `max_results`, there may
   be more; raise it and search again.
3. Once found, use the tool names in the result; do not build names from the
   naming pattern (see Step 4, item 3). If the result marks a tool as not
   declared yet, load it the way the result says and call it from the next model
   request on; if what you find is the server's authentication tool, complete
   authentication as its description says first. You are done with this skill
   at that point.
4. Only if nothing is found, look up the catalog from Step 1.

Confirm the connection only in the ways above; do not read this Agent's config
file or config endpoints for it: the environment variables and headers in MCP
config may hold plaintext credentials.

### Step 1 — List the catalog

Fetch the registry:

```yaml
tool: HttpRequest
parameters:
  url: http://127.0.0.1:<agent-service-port>/api/registry/services
  method: GET
```

Response shape (excerpt):

```json
{
  "data": {
    "services": [
      {
        "id": "acme-search-api",
        "name": "Acme Search API",
        "protocol": "http",
        "endpoint": "https://api.acme.example/search",
        "tags": ["search", "products"],
        "status": "online",
        "origin": "agent",
        "reviewStatus": "approved",
        "riskLevel": "medium",
        "operations": [...]
      }
    ],
    "total": 1,
    "source": "official"
  }
}
```

### Step 2 — Pick a candidate

Filter by `tags`, `protocol`, `name`. Important checks **before** invoking:

- `status === 'online'` → safe to call
- `status === 'offline'` / `'error'` → tell the user the service is down,
  **don't** retry blindly
- `status === 'degraded'` → degrade gracefully, mention it to the user
- `reviewStatus === 'pending'` (only `origin='agent'`) → you can only call it
  if `registeredBy` is you; otherwise ask the user to promote it
- `riskLevel === 'critical'` → expect a human approval prompt on every call

### Step 3 — Build the request (HTTP services)

If the service has `operations`, prefer them — they define stable contract
points. Build the URL as `<endpoint><operation.path>`.

```yaml
tool: HttpRequest
parameters:
  url: https://api.acme.example/search/v1/items?q=widget
  method: GET
  headers:
    Authorization: "Bearer ${secrets/api-keys/acme}"  # resolved at call time
```

If the service declares `auth.secretRef`, **do not** prompt the user for the
secret value during chat. The `HttpRequest` tool resolves it automatically.

### Step 4 — Build the request (MCP services)

MCP services aren't called via `HttpRequest` — they are tools exposed through
the Agent's `mcp_servers` config:

1. If you haven't added the MCP service to your Agent yet, POST to
   `http://127.0.0.1:<agent-service-port>/api/agents/<your-id>/mcp-servers` with `{ serverId: '<service.id>', config: <connection> }`
2. Next query, MCP discovery will auto-expose tools from the server
3. Once connected, the tools are registered in this Agent's tool pool as
   `<serverId>__<toolName>`; when that name breaks the model API's character or
   length rules, the model sees a different, rewritten name. Do not guess call
   names from the remote declaration or the naming pattern: search `ToolCatalog`
   by the server ID as in Step 0 and use the names in the result; for tools the
   result marks as not declared, load them the way the result says before
   calling.

### Step 5 — Handle the response

- 2xx → parse and use
- 4xx → likely a client error (bad params, missing auth); fix the request,
  then retry once; if it still fails, report to the user
- 5xx → server-side problem, report `status` of the service back so the user
  knows
- **Service-approval rejected** → response will contain `"decision":"rejected"`;
  do not retry, ask the user how to proceed

### Step 6 — Don't fall through to raw URL fetching

If the catalog has a service for what you need, **use it**. Don't bypass
governance by calling an undeclared URL directly — `HttpRequest` will still
work, but you lose:

- Approval gating for high-risk operations
- Credential injection (you'd need to ask the user for keys yourself)
- Audit trail and `lastUsed` tracking
- Other Agents being able to reuse your call patterns

## Failure modes

- **Catalog read fails**: just fall back to direct `HttpRequest` and warn the
  user that governance is bypassed.
- **No matching service**: ask the user if they want to **register** a new
  one — activate `registering-services` skill.
- **`status === 'offline'`**: report the situation, suggest checking the
  underlying service, **don't** call anyway.
