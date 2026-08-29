---
name: configuring-compute
description: >-
  Configure DesireCore compute providers through governed tools: inspect,
  enable or disable providers, sync models, and set API keys without reading
  them back. Use the dedicated DesireCore GUI tool for fields not yet covered
  by ManageCompute. Never call renderer-only /api/compute management endpoints
  from Bash or HttpRequest. 用户要求配置算力、同步模型或设置 API Key 时使用。
version: 1.1.0
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
  updated_at: '2026-08-30'
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
        通过受治理工具配置 DesireCore 算力：查看和启停 provider、同步模型、只写 API Key；
        ManageCompute 尚未覆盖的字段使用专用 DesireCore GUI 工具。禁止从 Bash 或 HttpRequest
        调用仅供可信渲染器使用的 /api/compute 管理端点。
      body: ./SKILL.zh-CN.md
      translated_by: human
      source_hash: sha256:b37d5baa849e88e9
    en-US:
      name: Configure Compute
      short_desc: Configure model providers and API keys for the user (keys are write-only)
      description: >-
        Configure DesireCore compute through governed tools: inspect and enable providers,
        sync models, and write API keys without reading them back. Use the dedicated
        DesireCore GUI tool for fields not covered by ManageCompute; never call renderer-only
        /api/compute management endpoints from Bash or HttpRequest.
      body: ./SKILL.md
      translated_by: human
      source_hash: sha256:b37d5baa849e88e9
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v2M15 2v2M9 20v2M15 20v2M2 9h2M2 15h2M20 9h2M20 15h2"/></svg>
  category: productivity
  channel: latest
  maintainer:
    name: DesireCore Official
    verified: true
---

# Configure Compute

Configure DesireCore compute through governed tools. Do not call the local
`/api/compute/*` management endpoints from Bash, HttpRequest, or scripts: those
endpoints intentionally require a trusted renderer Origin and instance token.

## Security contract

- API keys are write-only for agents. Never read `secrets.json`, request
  `ComputeCredential(action='get', raw=true)`, or repeat a key in tool results or chat.
- Use `ComputeCredential(action='set')` to create or replace the key of an
  existing user-managed provider. If the provider has no credential reference,
  the tool creates and attaches one without returning the plaintext. This path
  is approval-gated and audited; approval cards, tool events, receipts, and
  session history redact the sensitive value. System-managed credentials are
  not writable.
- Pass a value to `ComputeCredential(action='set')` only when the user already supplied the
  replacement key in the current request. If the agent must never handle the
  plaintext, use the GUI to focus the password field, let the user type into it
  directly, then continue the save flow. Never ask for the key in ordinary chat
  or read the masked field back into the model.
- `credentialMode=none` means the provider needs no key. Ollama is treated as
  `none` even when an older config does not declare the field.
- If the user asks for the current key, explain that the agent can replace it but
  cannot read it back. The human-only UI reveal flow remains separate.

## Workflow for an existing provider

First confirm `ManageCompute` is available through the current tool catalog. If
it is absent (for example on an older installed client), use the governed GUI
workflow below for the whole task; do not fall back to local HTTP.

1. Call `ManageCompute(action='list')`. Record the exact provider ID,
   enabled state, credential mode, status, and model count.
2. If credential mode is `required` and the user supplied a new key in the
   current request, call `ComputeCredential(action='set', providerId=..., value=...)`.
   Do not echo the value. If the agent must not handle plaintext,
   use the human-entry GUI flow below. For `none`, skip this step.
3. Call `ManageCompute(action='set_enabled', providerId=..., enabled=true)`.
4. Call `ManageCompute(action='sync_models', providerId=...)`. For Ollama
   this discovers locally installed models; for supported cloud providers it
   merges the built-in model list.
5. Call `InspectModels` to verify the intended model is selectable. When the
   user asked for a real test, run one short fixed-model conversation and verify
   the run receipt names the requested provider/model.

Mutating ManageCompute and ComputeCredential operations use the platform's
approval policy. Do not add a second confirmation in prose unless information
is missing or the user requested a destructive replacement.

## Fields not yet covered by ManageCompute

Creating a new custom provider, changing base URL/API format, deleting a
provider, and interactive key verification currently remain GUI operations.
Use `ControlDesireCoreGui`, not a generic browser/CUA tool:

1. `list_instances`, then `begin(instance=<id>, mode=control, reason=...)` for
   the intended DesireCore instance. The default `observe` mode is read-only and
   cannot modify compute settings.
2. Use the governed CDP methods to open Resources → Compute and make the change.
3. Finish with `end`. If `ManageCompute` exists, call `ManageCompute(action='list')`; on
   an older client, verify the saved state in the GUI instead. Call
   `InspectModels` when available to confirm model selection.

If the installed version includes `ControlDesireCoreGui` but reports that GUI
control is disabled, the owner must set
`config/security.json#desktopGuiControl.enabled=true` and restart that instance.
If the tool is absent from the catalog entirely, the client is too old and must
be upgraded; changing the switch cannot add a missing tool. Do not bypass the
renderer HTTP boundary.

## Completion report

Report the provider ID, enabled state, synchronized model count, and model test
result. Never include the key, its encrypted storage, or a plaintext fingerprint.
