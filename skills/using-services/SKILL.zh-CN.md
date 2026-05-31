<!-- locale: zh-CN -->

# 使用服务（using-services）

## L0：一句话总结

教会 Agent 如何从全局"应用与服务目录"里查找并正确调用服务。

## L1：概述

"应用与服务目录"存放所有已注册的 HTTP/MCP 服务。本元技能是你的 **使用手册**：
帮你 **找到** 合适的服务、**正确** 调用它。每个非平凡的注册服务还会自动生成
专属 `svc-<id>` Skill —— 优先用专属技能；本元技能是临时发现的兜底。

### 何时使用

- 用户让你做某件事，目录里可能有现成服务（如"搜产品库"、"发通知"）
- 你看到可用技能里有 `svc-<id>` —— 直接激活它
- 你打算调用一个 HTTP API，想先查目录，借力治理、凭据注入和审计

### 何时不要用

- 用户给了一次性 URL —— 直接 `HttpRequest` 即可
- 你已激活了 `svc-<id>` 专属 Skill —— 跟着它走，更具体

## L2：如何发现并调用

### Step 1 — 列目录

拉取注册表：

```yaml
tool: HttpRequest
parameters:
  url: http://127.0.0.1:<agent-service-port>/api/registry/services
  method: GET
```

响应（节选）：

```json
{
  "data": {
    "services": [
      {
        "id": "acme-search-api",
        "name": "Acme 搜索 API",
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

### Step 2 — 选候选

按 `tags`、`protocol`、`name` 过滤。调用 **前** 必须检查：

- `status === 'online'` → 可以调
- `status === 'offline'` / `'error'` → 告诉用户服务下线，**别** 盲目重试
- `status === 'degraded'` → 降级使用，告诉用户
- `reviewStatus === 'pending'`（仅 `origin='agent'`）→ 只有当 `registeredBy`
  就是你自己时才能调；否则请用户在 Store UI 提升后再用
- `riskLevel === 'critical'` → 每次调用都会触发人类审批

### Step 3 — 构造请求（HTTP 服务）

如果服务声明了 `operations`，优先用 —— 它们是稳定契约点。URL 拼成
`<endpoint><operation.path>`。

```yaml
tool: HttpRequest
parameters:
  url: https://api.acme.example/search/v1/items?q=widget
  method: GET
  headers:
    Authorization: "Bearer ${secrets/api-keys/acme}"   # 调用时解引用
```

如果服务带 `auth.secretRef`，**不要** 在聊天里向用户索要明文凭据。
`HttpRequest` 工具会自动解引用。

### Step 4 — 构造请求（MCP 服务）

MCP 服务不走 `HttpRequest`，它通过 Agent 的 `mcp_servers` 配置暴露成工具：

1. 若你的 Agent 还没接入该 MCP，POST `http://127.0.0.1:<agent-service-port>/api/agents/<your-id>/mcp-servers`
   传 `{ serverId: '<service.id>', config: <connection> }`
2. 下轮 query 时 MCP discovery 会自动暴露该服务器的工具
3. 直接用 MCP 工具名调用即可

### Step 5 — 处理响应

- 2xx → 解析使用
- 4xx → 多半是客户端错（参数错、缺鉴权）；修好后可重试一次，仍失败就告诉用户
- 5xx → 服务端问题，把目录里的 `status` 一并告诉用户
- **service-approval 拒绝** → 响应里会有 `"decision":"rejected"`；不要重试，问用户怎么办

### Step 6 — 不要绕开目录

如果目录里有该服务，**就用目录**。直接调未声明的 URL 虽然 `HttpRequest`
也能成功，但你会失去：

- 高风险操作的审批闸门
- 凭据注入（你得自己问用户要 key）
- 审计追踪与 `lastUsed` 统计
- 其他 Agent 复用你的调用模式

## 常见失败模式

- **目录读取失败**：降级直接 `HttpRequest`，并告诉用户已绕开治理。
- **没匹配上**：问用户要不要 **注册** 一个新的 —— 激活 `registering-services`。
- **`status === 'offline'`**：汇报情况，建议检查底层服务，**不要** 强行调用。
