---
name: using-services
description: >-
  Discover and invoke HTTP/MCP services already registered in the global
  catalog. Use when the user asks the Agent to call an API, search for an
  existing service, or query a backend that was registered via the
  registering-services skill. 调用某个 API、查找已有服务、访问已注册的后端服务时使用。
version: 1.0.2
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
  updated_at: '2026-06-29'
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
        发现并调用全局应用与服务目录中已经注册过的 HTTP/MCP 服务。Use when 用户让 Agent 调用某个 API、查找已有服务，或访问通过 registering-services 注册的后端。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Using Services
      short_desc: Discover and invoke registered services from the catalog
      description: >-
        Discover and invoke HTTP/MCP services already registered in the global catalog. Use when the user asks the Agent to call an API, search for an existing service, or query a backend that was registered via the registering-services skill.
      body: ./SKILL.md
      translated_by: human
      source_hash: sha256:8a20b2835e5e54d1
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#34C759" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="9" width="6" height="6" rx="1.5"/><rect x="15" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/><path d="M9 11.5h3.5V6H15"/><path d="M9 12.5h3.5V18H15"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# using-services Skill

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

## L2: How to discover and call

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
3. Call the tools by their MCP-declared names directly

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
