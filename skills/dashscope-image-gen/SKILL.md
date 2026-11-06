---
name: dashscope-image-gen
description: >-
  Generate images using the user’s explicit choice or saved image-generation default and the current runtime catalog. Requires an enabled provider, model access and quota; provider terms and separate usage charges apply. Use for drawing, illustrations, text-to-image and AI image creation.
license: MIT
version: 1.4.3
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
provider: auto
tags:
  - media
  - image
  - generation
  - dashscope
  - alibaba
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-11-07'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: AI 文生图
      short_desc: 遵循已配置默认与实际模型目录生成图片
      description: >-
        按用户明确选择或已保存的图片生成默认与当前运行时目录生成图片。需要已启用的供应商、模型访问权限及额度；供应商条款与单独使用费用仍适用。适用于画图、插画、文生图与 AI 图片创作。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:77a264d25e3bed8c
      translated_by: human
    en-US:
      name: AI Image Generation
      short_desc: Generate images with configured defaults and the runtime catalog
      description: "Generate images using the user’s explicit choice or saved image-generation default and the current runtime catalog. Requires an enabled provider, model access and quota; provider terms and separate usage charges apply. Use for drawing, illustrations, text-to-image and AI image creation."
      body: ./SKILL.md
      source_hash: sha256:77a264d25e3bed8c
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#34C759" stroke-width="1.5" fill="#34C759"
    fill-opacity="0.1"/><path d="M7 14l3-4 2.5 3 3.5-5 4 6H7z" fill="#34C759"
    fill-opacity="0.4" stroke="#34C759" stroke-width="1.2"
    stroke-linejoin="round"/><circle cx="15.5" cy="8.5" r="1.5" fill="#34C759"
    fill-opacity="0.6"/></svg>
  short_desc: Generate images with configured defaults and the runtime catalog
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
compatibility: Requires a running DesireCore agent-service and an enabled image_gen provider with model access and quota. Hosted services are external and subject to provider terms and separate usage charges.
---

# dashscope-image-gen Skill

## Scope and prerequisites

Generate and deliver images with a configured image-generation service. This skill does not provide a hosted model, credentials, quota, or a subscription. The user needs an enabled `image_gen` provider and access to the selected model; provider terms and separate usage charges apply. A catalog entry is not proof that an upstream channel is currently available.

## Model and provider selection

1. Honor the user's explicit model/provider choice. Check the current runtime catalog and applicable API contract rather than guessing from a model family or this skill's name.
2. When the user does not name a model, use the saved `defaultServiceMap.image_gen` binding, including its provider. Do not replace it with a model named in an example. If no usable default exists, inspect currently enabled image-generation capabilities and choose within the user's requirements; clarify when a choice would change their requested service or cost constraints.
3. Resolve a binding through available compute-inspection tools or `GET /api/compute/config` on the current agent-service. The configuration API masks keys; extract only the default binding, provider ID/enabled state, and image-model metadata needed for the request. Never request or print credentials. Model `serviceType` can be `image_gen` or an array containing it. For raw API calls, resolve the upstream model ID as `userOverrides.apiModelId`, then `apiModelId`, then `modelName`.
4. Availability comes from the actual selected provider and response. There is no static model whitelist or guaranteed default in this skill. For example, a Wan model may be offered through an official gateway or a user's own DashScope connection; its name alone does not determine the route.

## Choose an execution path

Use the current tool/API contract that fits the request. When available and suitable, `GenerateImage` handles provider adaptation, generation, media persistence, and dimension receipts in one call. Discover its current schema if needed. For a saved default, pass its provider ID as `provider` and omit `model` so the tool resolves the saved model; for an explicit model, pass the verified model ID and provider. Preserve the user's prompt, reference images, quantity, and requested dimensions.

Example tool arguments after resolving the saved provider (replace the placeholder, do not send it literally):

```json
{
  "provider": "<saved-image-provider-id>",
  "prompt": "A warm, quiet library illustration, without lettering",
  "n": 1
}
```

The raw API path below remains available for supported native operations or providers that need it. Do not interpret this example as a requirement to bypass a suitable generation tool.

## Raw API path

### Resolve the local service and request

Use the current agent-service address and caller authentication from the system's local API instructions, including the current isolated home. Do not guess another instance's port or obtain an upstream key. For a self-signed local HTTPS certificate, curl can use `-k` as directed by that local API contract.

For an OpenAI-compatible image-generation provider, submit `POST /api/media-proxy` with the resolved provider ID and upstream model ID. The proxy injects upstream authentication. This request is an example structure; model-specific endpoints, supported sizes/counts, and response fields must follow that provider's current contract:

```json
{
  "providerId": "<resolved-image-provider-id>",
  "serviceType": "image_gen",
  "endpoint": "/images/generations",
  "body": {
    "model": "<resolved-upstream-model-id>",
    "prompt": "A warm, quiet library illustration, without lettering",
    "n": 1
  },
  "responseType": "json"
}
```

`serviceType` alone selects a provider; it does not populate `body.model`. Keep the resolved provider/model binding together. If the saved provider or model is missing, disabled, or unsupported by the chosen path, explain the actual limitation rather than silently choosing a different one. Native DashScope and other protocols may require a different documented request; do not send an OpenAI-compatible payload to an unrelated endpoint.

### Persist and display the result

Save a potentially large response to a unique temporary file (`mktemp` or equivalent). Do not print raw responses, base64 image data, authorization headers, or signed download URLs. Check the proxy's `success` and the provider's actual response. Decode `b64_json` or download returned image URLs as appropriate; Python may be used for local JSON/base64 handling. A failed request is not an image.

Upload each resulting image through `POST /api/media/upload` using multipart field `file`, then read the returned `mediaId`. Temporary paths are staging locations, not final deliverables. Display the persisted image using the actual returned ID:

```text
![Image description](dc-media://<returned-mediaId>)
```

When using `GenerateImage`, consume its persisted image content/metadata directly; an additional manual upload is unnecessary. Check the actual image and dimension receipt before claiming the requested size, aspect ratio, lettering constraints, or visual content was achieved.

## Failures and recovery

- Report the selected provider/model, whether the failure was local validation or an upstream response, and a bounded, sanitized error code/message. Do not expose credentials or raw response bodies.
- Missing configuration, missing credentials, authentication failures, quota/rate limits, unsupported parameters, and upstream channel failures are different conditions. Diagnose from actual evidence; an HTTP status alone does not establish which model or account is at fault.
- `model_not_found`, `model_price_error`, or “No available channel” can indicate that the selected gateway lacks an authorized route. Recheck the current binding/catalog and report that service limitation. Do not automatically switch to another model or provider, including a model mentioned in an older example.
- Retry or choose an alternative only when the response and the user's authorization support it. Preserve explicit model/provider and cost constraints; request the user's choice if a different service is needed. Do not claim success until an image has been generated and persisted.
