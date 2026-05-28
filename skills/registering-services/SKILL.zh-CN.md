<!-- locale: zh-CN -->

# 注册服务（registering-services）

## L0：一句话总结

教会 Agent 如何把一个外部 HTTP/MCP 服务安全地登记进全局"应用与服务目录"，
并经人类用户审批。

## L1：概述

这是一个 **元技能**，告诉你（Agent）**怎么** 把新服务添加进共享的"应用与服务目录"。
本技能 **不负责** 调用外部服务 —— 注册成功且 approved 后，请用
`~/.desirecore/skills/svc-<id>/` 下的专属 Skill 或者 `using-services`
元技能来真正发起调用。

### 何时使用

- 用户让你"把 X API 注册到目录里"
- 你刚部署了某个后端，希望别的 Agent 能用到
- 你发现一个有用的公共 API，想让团队共享

### 何时不要用

- 一次性 HTTP 调用，别人不需要重复用 —— 直接 `HttpRequest` 即可
- 只给 **自己这个 Agent** 加 MCP 服务 —— 直接 POST `/api/agents/<your-id>/mcp-servers`，无需目录条目
- 修改已有目录条目 —— 必须由用户在 Store UI 提升 / 拒绝

## L2：如何注册一个服务

### Step 1 — 收集必填字段

调用 API 前，先准备好：

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | kebab-case，全局唯一（如 `acme-search-api`） |
| `name` | 是 | 显示名 |
| `description` | 是 | 一句话功能描述 |
| `protocol` | 是 | `'http'` 或 `'mcp'` |
| `tags` | 是 | 搜索标签数组，如 `['search', 'web']` |
| `registeredBy` | 是 | **你自己的 agent id** |
| `endpoint` | `protocol='http'` 时必填 | API 基础 URL |
| `riskLevel` | 推荐 | `low` / `medium` / `high` / `critical` |
| `auth` | 服务需要鉴权时 | `{ type, secretRef }` — 见下文 |
| `operations` | 推荐 | 操作清单，会被 per-service Skill 渲染成示例 |
| `capabilities` | 可选 | 能力标签 |

### Step 2 — 诚实地选择 `riskLevel`

`riskLevel` 决定 **未来调用** 该服务时是否触发审批闸门：

- `low` — 只读数据，调用无副作用（如公开天气 API）
- `medium` — 大多数 API 的默认值；同一会话首次调用可能提示
- `high` — 涉及金钱、发邮件、修改用户数据等的服务
- `critical` — 可能造成不可逆后果；**每次** 调用都要人类审批

**不确定时倾向于更高风险等级。** 低估比高估更糟。

### Step 3 — 用 `secretRef` 引用凭据，**不要** 内联明文

**不要把 API key/token 写进目录条目。** 目录是全局可见的，Store UI 任何人都能查看，
未来还可能被审计。正确做法：

```jsonc
{
  "auth": {
    "type": "bearer",
    "secretRef": "secrets/api-keys/acme"  // 指针，不是真正的 key
  }
}
```

`HttpRequest` 在调用时解引用 `secretRef`。如果对应 secret 还不存在，请通过
用户自己的凭据管理流程让他/她填好 —— 不要在聊天里收明文。

### Step 4 — 调用注册 API

用 `HttpRequest` 工具 POST 到本机 Agent Service：

```yaml
tool: HttpRequest
parameters:
  url: http://127.0.0.1:<agent-service-port>/api/registry/agent-services
  method: POST
  body:
    id: acme-search-api
    name: "Acme 搜索 API"
    description: "对 Acme 产品库做全文搜索"
    protocol: http
    endpoint: https://api.acme.example/search
    tags: ["search", "products"]
    registeredBy: "<your-agent-id>"
    riskLevel: medium
    auth:
      type: bearer
      secretRef: secrets/api-keys/acme
    operations:
      - name: search
        method: GET
        path: /v1/items
        description: "按 query 搜索商品"
      - name: getDetail
        method: GET
        path: /v1/items/{id}
        description: "按 id 获取单个商品"
```

（Agent Service 端口由运行时提供；不确定如何获取时用 `request-help` 技能问。）

### Step 5 — 等待人类批准

该端点会触发 **service-approval** 请求，HTTP 调用会一直阻塞，直到用户在
Store UI 批准或拒绝。

- **批准** → 条目写入 `~/.desirecore/config/registry-agent-services.json`，
  状态为 `reviewStatus: 'pending'`。pending 期间 **只有你**（注册者）能调用。
- **拒绝** → API 返回 403；不要重试，问用户下一步怎么办。

人类后续可以在 Store UI 把条目从 `pending` **提升（promote）** 为 `approved`。
提升后该服务对所有 Agent 可调，且会触发 `service-skill-generator` 生成
`~/.desirecore/skills/svc-<id>/SKILL.md`，里头有基于 `operations` 的示例。

### Step 6 — 不要重复注册

如果 `POST /api/registry/agent-services` 返回 `409 Conflict`，说明该服务已存在。
除非用户明确要求注册一个独立变种，否则不要换个 id 静默注册 —— 偷偷影子覆盖
已有服务是治理失败。

## 常见失败模式

- **SSRF 拦截**：注册 API 拒绝私网地址（10.x / 172.16-31.x / 192.168.x / 169.254.x），
  本机环回除外。公网 IP 与 DNS 域名允许。
- **缺 `registeredBy`**：API 返回 400。必须带上你自己的 agent id —— 不允许匿名注册。
- **审批超时**：broker 等待用户太久会超时，按 `rejected` 处理。
