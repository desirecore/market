<!-- locale: zh-CN -->

# 使用服务（using-services）

## 原生应用与对外协议

**DesireCore Control** 是供外部智能体使用的 `native-app`，不是已经安装的内部 MCP 服务。看到它的管理页或对外 `/mcp` 端点，不代表本 Agent 获准通过 `using-services` 调用、注册它或绕过 GUI 审批。应用生命周期使用 `app-install-manager`（1.5.2 或更新版本），运行时 GUI 接管使用受治理的 `ControlDesireCoreGui`。应用安装不得生成内部服务或 `svc-*` 技能。

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
- 用户点名的服务已是本 Agent 接入的 MCP 服务端 —— 按 Step 0 直接找到它的工具，不必查目录

## L2：如何发现并调用

### Step 0 — 先确认是不是本 Agent 已接入的 MCP 服务端

用户点名的服务（如「用 xxx 这个服务」）可能就是本 Agent 已接入的 MCP 服务端，服务端 ID 就是接入时用的名字。这时不需要查目录：

1. 系统提示词里若列出了本轮可用的 MCP 服务端（较新的客户端才有这一段），先在其中核对；没有这一段不代表没有接入。
2. 用 `ToolCatalog` 按服务端 ID 检索，例如 `ToolCatalog(query="<服务端 ID>", max_results=20)`。query 只写 ID 本身，不要写 `<ID>__*` 这类通配：检索不支持通配，会一个都查不到。返回条数等于 `max_results` 时可能还有更多，调大后再查。
3. 命中后以结果里的工具名为准，不要按命名习惯拼名字（见 Step 4 第 3 条）。结果标明某个工具尚未声明时，按结果给出的加载方式加载，下一次模型请求起再调用；查到的是该服务端的认证工具时，按它的说明先完成认证。到这里就不必继续本技能。
4. 查不到时再从 Step 1 查目录。

确认接入情况只用以上方式，不要为此读取本 Agent 的配置文件或配置接口：MCP 配置里的环境变量和请求头可能含明文凭据。

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
3. 接入生效后，工具在本 Agent 的工具池里注册为 `<serverId>__<工具名>`；名字不符合模型接口的字符或长度要求时，模型看到的是改写后的另一个名字。所以不要按远端声明名或命名习惯猜调用名：按 Step 0 用 `ToolCatalog` 以服务端 ID 检索，以结果里的名字为准；结果标明未声明的，按结果给出的加载方式加载后再调用。

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
