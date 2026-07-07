# 配置算力

通过 Agent Service HTTP API 帮用户配置算力供应商——模型 API 端点与 API Key。

## 安全模型（先读这里，不可协商）

- **API Key 只写不读。** 你可以创建和覆盖密钥，但**永远无法**读回已有密钥。
  没有任何 API 会向你返回密钥明文：`GET /api/compute/config` 只返回掩码值，
  运行时同时拦截对 `secrets.json` 的文件读取（Read/Grep 工具与 shell 命令一律拒绝）。
- **不要尝试绕过。** 不要读取 `~/.desirecore/config/secrets.json`，不要在对话中
  超出必要地回显用户提供的密钥，除 `POST /api/compute/secrets` 外不要在任何地方存放密钥。
- 如果用户问「我现在的 key 是什么」，回答：密钥无法读回，只能替换；
  可引导用户到供应商设置页，那里有仅限用户本人的明文查看控件。

## 如何调用 API

- 优先使用 `Bash` 工具 + `curl`。API 基础地址已注入到 system prompt 的
  「本机 API」小节，直接引用即可。
- Windows 无 Git Bash 时，用 `HttpRequest` 工具调用相同 URL。

## 工作流程

### 1. 查看当前配置

```bash
curl -s $BASE/api/compute/config
```

响应中的 `providers[]` 里 `apiKey` 是**掩码展示值**（前 4 位 + 圆点），
`hasApiKey: boolean` 表示是否已配置密钥。据此决定是新建 provider 还是更新现有的。
掩码 `apiKey` 不是真实密钥，不要当作密钥使用。

### 2. 创建 provider（如需要）

```bash
curl -s -X POST $BASE/api/compute/providers \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "deepseek",
    "label": "DeepSeek",
    "baseUrl": "https://api.deepseek.com",
    "services": ["chat"],
    "apiFormat": "openai-completions",
    "priceCurrency": "CNY"
  }'
```

必填字段：`provider`、`label`、`baseUrl`、`services`。响应返回创建的 provider
及其生成的 `id`——后续步骤要用。已知供应商预设与模型列表可通过
`GET /api/compute/pi-providers` 和 `GET /api/compute/pi-models/:provider` 获取。

### 3. 设置 API Key（只写）

向用户索取密钥。provider 已有 `apiKeyRef` 则复用；否则生成一个形如
`key-<随机串>` 的引用名并挂到 provider 上：

```bash
# 写入密钥（只写端点，没有对应的 GET）
curl -s -X POST $BASE/api/compute/secrets \
  -H 'Content-Type: application/json' \
  -d '{"ref": "key-abc123", "value": "<用户提供的API_KEY>"}'

# 如果 provider 还没有 apiKeyRef，补挂上去
curl -s -X PUT $BASE/api/compute/providers/<id> \
  -H 'Content-Type: application/json' \
  -d '{"apiKeyRef": "key-abc123"}'
```

### 4. 验证密钥

```bash
curl -s -X POST $BASE/api/compute/verify-key \
  -H 'Content-Type: application/json' \
  -d '{"provider": "deepseek", "baseUrl": "https://api.deepseek.com", "apiKeyRef": "key-abc123", "apiFormat": "openai-completions"}'
```

返回 `{ valid, latencyMs, errorMessage?, suggestedBaseUrl? }`。若返回
`suggestedBaseUrl`，主动提议更新 provider 的 `baseUrl`。

### 5. 启用并填充模型

```bash
curl -s -X PUT $BASE/api/compute/providers/<id> \
  -H 'Content-Type: application/json' -d '{"enabled": true}'

# 可选：从内置注册表同步模型列表
curl -s -X POST $BASE/api/compute/sync-models/<id>
```

### 6. 刷新配置让 UI 生效

收尾必做：

```bash
curl -s -X POST $BASE/api/compute/reload
```

该端点重新校验配置并向客户端 UI 广播刷新事件。把返回的 `providerCount` /
`enabledProviderCount` / `modelCount` 报告给用户作为完成确认。

## 端点速查

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| GET | `/api/compute/config` | 完整配置；`apiKey` 为掩码 + `hasApiKey` |
| POST | `/api/compute/providers` | 创建 provider |
| PUT | `/api/compute/providers/:id` | 局部更新（label/baseUrl/enabled/apiFormat/apiKeyRef/...） |
| DELETE | `/api/compute/providers/:id` | 删除 provider |
| POST | `/api/compute/secrets` | 写入密钥 `{ref, value}` —— **只写** |
| DELETE | `/api/compute/secrets/:ref` | 删除密钥 |
| POST | `/api/compute/verify-key` | 端到端验证密钥 |
| POST | `/api/compute/sync-models/:id` | 从注册表同步模型列表 |
| POST | `/api/compute/reload` | 重新校验配置 + 广播 UI 刷新 |
| GET | `/api/compute/pi-providers` | 已知供应商预设 |
| GET | `/api/compute/pi-models/:provider` | 预设供应商的已知模型 |

## 错误处理

| 现象 | 原因 | 处理 |
| ---- | ---- | ---- |
| 创建时 400 | 缺必填字段 / 携带未知字段 | 修正请求体（schema 严格，`additionalProperties: false`） |
| PUT 时 404 | provider id 错误 | 重新 GET config 拿列表 |
| 验证 `valid: false` | 密钥错 / baseUrl 错 / apiFormat 错 | 把 `errorMessage` 转告用户；有 `suggestedBaseUrl` 则尝试 |
| 任何端点 403 | 误触凭证门控端点（明文查看） | 立即停止——该端点仅供人类用户的 UI 使用 |

## 确认礼仪

- 覆盖已有密钥（`hasApiKey: true`）前，先向用户确认。
- 删除 provider 或密钥前，先向用户确认。
- 完成后向用户总结变更内容（provider、启用状态、模型数量），不要复述密钥值。
