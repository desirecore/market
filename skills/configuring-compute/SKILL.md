---
name: configuring-compute
description: >-
  Configure compute providers (model API endpoints and API keys) for the user
  via the Agent Service HTTP API: create/update providers, write API keys
  (write-only), verify them, and reload the configuration. Use when the user
  asks to add or configure a model provider, set an API key, or fix compute
  configuration. 用户要求配置算力、添加模型供应商或设置 API Key 时使用。
version: 1.0.0
type: meta
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - compute
  - provider
  - configuration
  - meta
metadata:
  author: desirecore
  updated_at: '2026-07-07'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 配置算力
      short_desc: 帮用户配置模型供应商与 API Key（密钥只写不读）
      description: >-
        通过 Agent Service HTTP API 为用户配置算力供应商（模型 API 端点与 API Key）：
        创建/更新 provider、写入 API Key（只写）、验证密钥、刷新配置。
        Use when 用户要求添加或配置模型供应商、设置 API Key、修复算力配置。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Configure Compute
      short_desc: Configure model providers and API keys for the user (keys are write-only)
      description: >-
        Configure compute providers (model API endpoints and API keys) for the user
        via the Agent Service HTTP API: create/update providers, write API keys
        (write-only), verify them, and reload the configuration. Use when the user
        asks to add or configure a model provider, set an API key, or fix compute configuration.
      body: ./SKILL.md
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
---

# Configure Compute

Help the user configure compute providers — model API endpoints and API keys —
through the Agent Service HTTP API.

## Security model (read this first, non-negotiable)

- **API keys are write-only.** You can create and overwrite keys; you can NEVER
  read an existing key back. There is no API that returns key plaintext to you,
  `GET /api/compute/config` returns masked values only, and the runtime blocks
  file reads of `secrets.json` (Read/Grep tools and shell commands alike).
- **Do not try to work around this.** Never attempt to read
  `~/.desirecore/config/secrets.json`, never echo a key the user gave you back
  into chat more than necessary, never store keys anywhere except via
  `POST /api/compute/secrets`.
- If the user asks "what is my current key", answer: keys cannot be read back;
  they can only be replaced. Point them to the provider settings UI, which has
  a user-only reveal control.

## How to call the API

- Prefer the `Bash` tool with `curl`. The API base URL is already injected into
  the "Local API" section of the system prompt; reference it directly.
- On Windows without Git Bash, use the `HttpRequest` tool with the same URLs.

## Workflow

### 1. Inspect current configuration

```bash
curl -s $BASE/api/compute/config
```

Response contains `providers[]` where `apiKey` is a **masked display value**
(first 4 chars + bullets) and `hasApiKey: boolean` tells you whether a key is
configured. Use this to decide between creating a new provider and updating an
existing one. Never treat the masked `apiKey` as a real key.

### 2. Create a provider (if needed)

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

Required fields: `provider`, `label`, `baseUrl`, `services`. The response
returns the created provider with its generated `id` — keep it for later steps.
Known provider presets and model lists are available via
`GET /api/compute/pi-providers` and `GET /api/compute/pi-models/:provider`.

### 3. Set the API key (write-only)

Ask the user for the key. Reuse the provider's existing `apiKeyRef` if set;
otherwise generate one like `key-<random>` and attach it to the provider:

```bash
# Write the secret (write-only endpoint; there is no GET counterpart)
curl -s -X POST $BASE/api/compute/secrets \
  -H 'Content-Type: application/json' \
  -d '{"ref": "key-abc123", "value": "<API_KEY_FROM_USER>"}'

# Attach the ref to the provider if it was not set yet
curl -s -X PUT $BASE/api/compute/providers/<id> \
  -H 'Content-Type: application/json' \
  -d '{"apiKeyRef": "key-abc123"}'
```

### 4. Verify the key

```bash
curl -s -X POST $BASE/api/compute/verify-key \
  -H 'Content-Type: application/json' \
  -d '{"provider": "deepseek", "baseUrl": "https://api.deepseek.com", "apiKeyRef": "key-abc123", "apiFormat": "openai-completions"}'
```

Returns `{ valid, latencyMs, errorMessage?, suggestedBaseUrl? }`. If
`suggestedBaseUrl` is present, offer to update the provider's `baseUrl`.

### 5. Enable and populate models

```bash
curl -s -X PUT $BASE/api/compute/providers/<id> \
  -H 'Content-Type: application/json' -d '{"enabled": true}'

# Optional: sync the model list from the built-in registry
curl -s -X POST $BASE/api/compute/sync-models/<id>
```

### 6. Reload so the UI reflects the change

Always finish with:

```bash
curl -s -X POST $BASE/api/compute/reload
```

This re-validates the configuration and broadcasts a refresh event to the
client UI. Report the returned `providerCount` / `enabledProviderCount` /
`modelCount` to the user as confirmation.

## Endpoint reference

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/api/compute/config` | Full config; `apiKey` masked + `hasApiKey` |
| POST | `/api/compute/providers` | Create provider |
| PUT | `/api/compute/providers/:id` | Patch provider (label/baseUrl/enabled/apiFormat/apiKeyRef/...) |
| DELETE | `/api/compute/providers/:id` | Remove provider |
| POST | `/api/compute/secrets` | Write key `{ref, value}` — **write-only** |
| DELETE | `/api/compute/secrets/:ref` | Delete key |
| POST | `/api/compute/verify-key` | Probe a key end-to-end |
| POST | `/api/compute/sync-models/:id` | Sync model list from registry |
| POST | `/api/compute/reload` | Re-validate config + broadcast UI refresh |
| GET | `/api/compute/pi-providers` | Known provider presets |
| GET | `/api/compute/pi-models/:provider` | Known models for a preset |

## Error handling

| Symptom | Cause | Action |
| ------- | ----- | ------ |
| 400 on create | Missing required field / unknown field | Fix the request body (schema is strict, `additionalProperties: false`) |
| 404 on PUT | Wrong provider id | Re-list via GET config |
| `valid: false` on verify | Wrong key / wrong baseUrl / wrong apiFormat | Show `errorMessage` to the user; try `suggestedBaseUrl` if present |
| 403 anywhere | You tried a credential-gated endpoint (key reveal) | Stop — that endpoint is for the human user's UI only |

## Confirmation etiquette

- Before overwriting an existing key (`hasApiKey: true`), confirm with the user.
- Before deleting a provider or key, confirm with the user.
- After finishing, summarize what changed (provider, enabled state, model count)
  without repeating the key value.
