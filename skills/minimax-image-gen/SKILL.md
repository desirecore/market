---
name: minimax-image-gen
description: >-
  Use this skill when the user wants to generate images using MiniMax's
  image-01 model. Supports text-to-image and subject reference for character
  consistency. Use when 用户提到 生成图片、画图、文生图、创建图片、
  AI 绘画、生成插图、画一张、帮我画、设计图片、MiniMax 画图。
license: Complete terms in LICENSE.txt
version: 1.3.1
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
provider: minimax
tags:
  - media
  - image
  - generation
  - minimax
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-04-25'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: MiniMax 文生图
      short_desc: 基于 MiniMax image-01 的文本生成图片技能
      description: >-
        Use this skill when the user wants to generate images using MiniMax's image-01 model. Supports text-to-image and subject reference for character consistency. Use when 用户提到 生成图片、画图、文生图、创建图片、 AI 绘画、生成插图、画一张、帮我画、设计图片、MiniMax 画图。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:4630268ef3bd4e23
      translated_by: human
    en-US:
      name: MiniMax Image Generation
      short_desc: Text-to-image generation skill powered by MiniMax image-01
      description: >-
        Use this skill when the user wants to generate images using MiniMax's image-01 model. Supports text-to-image and subject reference for character consistency. Use when the user mentions generate images, draw a picture, text-to-image, create an image, AI painting, generate illustration, draw one for me, help me draw, design an image, MiniMax drawing.
      body: ./SKILL.md
      source_hash: sha256:4630268ef3bd4e23
      translated_by: human
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#34C759" stroke-width="1.5" fill="#34C759"
    fill-opacity="0.1"/><circle cx="8.5" cy="8.5" r="2" stroke="#34C759"
    stroke-width="1.2"/><path d="M3 16l5-5 4 4 3-3 6 6" stroke="#34C759"
    stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
  listed: false
---

# minimax-image-gen Skill

## Mandatory Rules (violations will cause feature failure)

1. **Must use `"response_format": "url"`** — `"base64"` is forbidden, base64 will cause output truncation
2. **Must access agent-service over HTTPS** — `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
3. **Must upload to media-store via `/api/media/upload`** — saving to local paths is forbidden
4. **Must use the `dc-media://` protocol to display images** — the only way the frontend can render correctly
5. **Use Bash curl throughout** — do not use the HttpRequest tool or Python

## Complete Execution Flow (strictly follow these three steps)

### Step 1: Call the API to generate the image

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "provider-minimax-media-001",
    "endpoint": "/image_generation",
    "body": {
      "model": "image-01",
      "prompt": "这里替换为英文图片描述",
      "aspect_ratio": "1:1",
      "response_format": "url",
      "n": 1
    },
    "responseType": "json"
  }'
```

Extract `data.data.image_urls[0]` from the JSON response to obtain the image URL.

### Step 2: Download and upload to media-store

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
IMAGE_URL="第一步拿到的图片URL"
curl -sL "$IMAGE_URL" -o /tmp/minimax-gen.png && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-gen.png;type=image/png"
```

Extract the `mediaId` field from the JSON response (format like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`).

### Step 3: Display the image with the dc-media protocol

Write Markdown image syntax directly in your reply text:

```
![图片描述](dc-media://这里替换为mediaId)
```

For example: `![白色的猫坐在书桌上](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.png)`

The frontend will automatically convert `dc-media://` into an accessible image URL and render it.

## Parameter Mapping

| User Intent | aspect_ratio |
|---------|-------------|
| Square / avatar | "1:1" |
| Landscape / scenery / wallpaper | "16:9" |
| Portrait / phone / poster | "9:16" |
| Standard photo | "4:3" |
| Portrait photo | "3:4" |

## Subject Reference (character consistency)

Add `subject_reference` in the body:

```json
"subject_reference": [
  { "type": "character", "image_file": { "url": "参考图片URL" } }
]
```

## Error Handling

- `"error": "未找到匹配的供应商"`: MiniMax Media Provider not configured
- `statusCode: 401`: Invalid API Key
- `statusCode: 429`: Rate limited, retry later
