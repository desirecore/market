---
name: dashscope-image-gen
description: >-
  Use this skill when the user wants to generate images using Alibaba Cloud
  DashScope's Wan (通义万相) series models. Supports text-to-image with multiple
  model tiers (wan2.7-image-pro, wan2.7-image). Uses OpenAI-compatible
  chat/completions API for synchronous image generation.
  Use when 用户提到 生成图片、画图、文生图、创建图片、AI 绘画、
  生成插图、画一张、帮我画、设计图片、通义万相、万相、阿里云画图、dashscope 画图。
license: Complete terms in LICENSE.txt
version: 1.1.1
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: dashscope
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
  updated_at: '2026-05-08'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 阿里云 文生图
      short_desc: 基于阿里云通义万相的文本生成图片技能
      description: >-
        当用户希望使用阿里云 DashScope 的通义万相系列模型生成图片时使用此技能。支持多种模型层级（wan2.7-image-pro / wan2.7-image）的文生图，通过 OpenAI 兼容的 chat/completions API 同步生成图片。用户提到 生成图片、画图、文生图、创建图片、AI 绘画、生成插图、画一张、帮我画、设计图片、通义万相、万相、阿里云画图、dashscope 画图。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:135b99cdd33441fb
      translated_by: human
    en-US:
      name: DashScope Image Generation
      short_desc: Text-to-image generation using Alibaba Cloud Wan (通义万相) models
      description: "Use this skill when the user wants to generate images using Alibaba Cloud DashScope's Wan (通义万相) series models. Supports text-to-image with multiple model tiers (wan2.7-image-pro, wan2.7-image) via the OpenAI-compatible chat/completions API. Trigger keywords: generate image, draw, text-to-image, create image, AI painting, illustration, design picture, Wan, Tongyi Wanxiang, DashScope."
      body: ./SKILL.md
      source_hash: sha256:135b99cdd33441fb
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
  short_desc: 基于阿里云通义万相的文本生成图片技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# dashscope-image-gen Skill

## Mandatory Rules (violations cause failure)

1. **Must access agent-service over HTTPS** — use `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Must upload to media-store via `/api/media/upload`** — `/tmp` is only a transient download/decode location, never use a local path as the final output
3. **Must use the `dc-media://` protocol to display images** — the only form the frontend can render correctly
4. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
5. **Use compatible-mode (`/chat/completions`)** — synchronous call; the response contains the image URL directly

## Model Selection

| Model | Characteristics | When to use |
|------|------|---------|
| wan2.7-image-pro | Flagship, 4K resolution, thinking_mode | User asks for top quality, 4K, or rich detail |
| wan2.7-image | Standard high quality, thinking_mode | **Default**, for unspecified requests |

**Default rule**: if the user does not specify a model, use `wan2.7-image`.

## Full Execution Flow (strictly three steps)

### Prerequisites

- The user has configured an Alibaba Cloud DashScope provider in Resource Manager → Compute and filled in an API Key
- agent-service is running

### Step 1: Call the text-to-image API (synchronous)

Generate the image via media-proxy's compatible-mode endpoint; the response includes the image URL directly:

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "dashscope",
    "serviceType": "image_gen",
    "endpoint": "/chat/completions",
    "body": {
      "model": "wan2.7-image",
      "messages": [
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Replace this with the image description (English usually gives better results)"}
          ]
        }
      ]
    },
    "responseType": "json"
  }'
```

**Example response**:
```json
{
  "success": true,
  "data": {
    "request_id": "...",
    "output": {
      "choices": [
        {
          "message": {
            "role": "assistant",
            "content": [
              {
                "type": "image",
                "image": "https://dashscope-result.oss.aliyuncs.com/..."
              }
            ]
          },
          "finish_reason": "stop"
        }
      ]
    }
  },
  "statusCode": 200
}
```

Locate the item with `type: "image"` inside `data.output.choices[0].message.content` and extract its `image` URL.

### Step 2: Download and upload to media-store

The image URL is time-limited; download and persist it to the local media-store immediately:

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
IMAGE_URL="image URL from step 1's response"
curl -sL "$IMAGE_URL" -o /tmp/dashscope-gen.png && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/dashscope-gen.png;type=image/png"
```

Pick the `mediaId` field from the JSON response (format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`).

### Step 3: Render the image via the dc-media protocol

In your reply text, write Markdown image syntax directly:

```
![Image description](dc-media://replace-with-mediaId)
```

For example: `![White fox in a forest](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.png)`

The frontend will translate `dc-media://` into a reachable image URL and render it.

## Parameter Mapping

### Size selection

When calling Wan via compatible-mode, the size is passed as the top-level `size` parameter:

```json
{
  "model": "wan2.7-image",
  "size": "1024x1024",
  "messages": [...]
}
```

| User intent | size value |
|---------|-----------|
| Square / avatar / default | "1024x1024" |
| Landscape / scenery / wallpaper | "1792x1024" |
| Portrait / mobile / poster | "1024x1792" |

### Optional parameters (top-level body fields)

| Parameter | Description |
|------|------|
| `n` | Number of images, 1–4, default 1 |
| `size` | Image size, e.g. "1024x1024" |

## Multiple Image Generation

When `n > 1`, the `choices` array contains multiple entries, each with an image inside `message.content`. Download and upload each image, then render them one by one:

```
![Image 1 description](dc-media://mediaId1)
![Image 2 description](dc-media://mediaId2)
```

## Error Handling

- `success: false` + `error: "No matching provider"`: DashScope provider not configured or disabled
- `success: false` + `error: "API Key not configured"`: API Key missing
- `statusCode: 401`: API Key invalid or expired
- `statusCode: 429`: rate limited, retry later
- `statusCode: 400` + `InvalidParameter`: bad parameters (e.g. unsupported size)
- `statusCode: 403` + `AccessDenied.Unpurchased`: model not activated; enable it in the Alibaba Cloud console

## Notes

- compatible-mode calls are synchronous and typically return in 10–60 seconds (wan2.7-image-pro can take longer)
- Image URLs expire; download promptly
- English prompts usually produce the best results; Chinese is also supported
- When the user does not specify a model or size, default to `wan2.7-image` + `1024x1024`
