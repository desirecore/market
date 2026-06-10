---
name: dashscope-image-gen
description: >-
  Use this skill when the user wants to generate images using Alibaba Cloud
  DashScope's Wan (通义万相) series models. Supports text-to-image with multiple
  model tiers (wan2.7-image-pro, wan2.7-image). Uses OpenAI-compatible
  images/generations API for synchronous image generation.
  Use when 用户提到 生成图片、画图、文生图、创建图片、AI 绘画、
  生成插图、画一张、帮我画、设计图片、通义万相、万相、阿里云画图、dashscope 画图。
license: Complete terms in LICENSE.txt
version: 1.3.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
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
  updated_at: '2026-06-10'
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
        当用户希望使用阿里云 DashScope 的通义万相系列模型生成图片时使用此技能。支持多种模型层级（wan2.7-image-pro / wan2.7-image）的文生图，通过 OpenAI 兼容的 images/generations API 同步生成图片。用户提到 生成图片、画图、文生图、创建图片、AI 绘画、生成插图、画一张、帮我画、设计图片、通义万相、万相、阿里云画图、dashscope 画图。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:a2c4e8f01b3d5e7f
      translated_by: human
    en-US:
      name: DashScope Image Generation
      short_desc: Text-to-image generation using Alibaba Cloud Wan (通义万相) models
      description: "Use this skill when the user wants to generate images using Alibaba Cloud DashScope's Wan (通义万相) series models. Supports text-to-image with multiple model tiers (wan2.7-image-pro, wan2.7-image) via the OpenAI-compatible images/generations API. Trigger keywords: generate image, draw, text-to-image, create image, AI painting, illustration, design picture, Wan, Tongyi Wanxiang, DashScope."
      body: ./SKILL.md
      source_hash: sha256:a2c4e8f01b3d5e7f
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

1. **STRICTLY follow the execution steps below** — do NOT improvise, explore alternative endpoints, or try models not listed in this document
2. **Must access agent-service over HTTPS** — the API address is already provided in the system prompt under "本机 API" section (e.g. `https://127.0.0.1:PORT`); use it directly with `-k` to skip certificate verification
3. **Must upload to media-store via `/api/media/upload`** — `/tmp` is only a transient download/decode location, never use a local path as the final output
4. **Must use the `dc-media://` protocol to display images** — the only form the frontend can render correctly
5. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
6. **Use `/images/generations` endpoint** — synchronous call; the response contains b64_json image data
7. **Only use models listed below** — do NOT try dall-e-3, qwen-vl, or any model not in the Model Selection table

## Provider & Default Compute

This skill uses Alibaba Cloud DashScope's Wan (通义万相) models. You do NOT need to specify a provider — just pass `"serviceType": "image_gen"` and the system will automatically route to the correct provider:

- **DesireCore Cloud** (default, always available): The built-in compute provider already supports `image_gen` with Wan models. Users can generate images immediately without any configuration.
- **DashScope** (user-configured): If the user has configured their own DashScope API key, the system may route to it.

**Never** try to query provider lists, read compute.json, or explore available models through API calls. The models listed below are guaranteed to work.

## Model Selection

| Model | Characteristics | When to use |
|------|------|---------|
| wan2.7-image-pro | Flagship, 4K resolution, thinking_mode | User asks for top quality, 4K, or rich detail |
| wan2.7-image | Standard high quality, thinking_mode | **Default**, for unspecified requests |

**Default rule**: if the user does not specify a model, use `wan2.7-image`.

## Full Execution Flow (strictly follow these steps)

### How to get the API address

The system prompt already contains the agent-service API address under "本机 API" (e.g. `Agent Service: https://127.0.0.1:61000`). Extract the URL from there and use it directly.

If for any reason you cannot find it in the system prompt, use this fallback:

```bash
PORT=$(cat "${DESIRECORE_HOME:-$HOME/.desirecore}/agent-service.port")
# Then use https://127.0.0.1:${PORT}
```

### Step 1: Generate the image (single curl command)

Call `/images/generations` through media-proxy. **You MUST use this exact request structure** — do not add `messages`, `response_format`, or any other parameters not shown here:

```bash
# Save response to a temp file to avoid base64 flooding the terminal
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceType": "image_gen",
    "endpoint": "/images/generations",
    "body": {
      "model": "wan2.7-image",
      "prompt": "Replace this with the image description (English usually gives better results)",
      "size": "1024x1024",
      "n": 1
    },
    "responseType": "json"
  }' -o /tmp/dashscope-response.json

# Check success and extract b64_json directly to image file (NEVER cat the response to stdout)
python3 -c "
import json, base64, sys
with open('/tmp/dashscope-response.json') as f:
    resp = json.load(f)
if not resp.get('success'):
    print('ERROR:', json.dumps(resp, ensure_ascii=False)[:500])
    sys.exit(1)
b64 = resp['data']['data'][0]['b64_json']
with open('/tmp/dashscope-gen.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('OK: saved to /tmp/dashscope-gen.png')
"
```

**CRITICAL**: The response contains a large base64 image (~2MB). NEVER print the raw response or b64_json to the terminal. Always save to file with `-o` and extract with the python3 script above.

**Response format** (saved in `/tmp/dashscope-response.json`):
```json
{
  "success": true,
  "data": {
    "created": 1781060911,
    "data": [{"b64_json": "<very large base64 string>"}],
    "size": "1024x1024"
  }
}
```

### Step 2: Upload to media-store

```bash
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

Pass `size` in the `body` object:

```json
{
  "model": "wan2.7-image",
  "prompt": "your image description",
  "size": "1024x1024",
  "n": 1
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
| `n` | Number of images, 1-4, default 1 |
| `size` | Image size, e.g. "1024x1024" |

## Multiple Image Generation

When `n > 1`, download and upload each image, then render them one by one:

```
![Image 1 description](dc-media://mediaId1)
![Image 2 description](dc-media://mediaId2)
```

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| `"No matching provider"` | No enabled provider supports `image_gen` | Tell user to enable a provider with image_gen support in settings |
| `"API Key not configured"` | API Key missing | Tell user to configure API key |
| `statusCode: 401` | API Key invalid or expired | Tell user to check API key |
| `statusCode: 429` | Rate limited | Wait and retry once |
| `statusCode: 400` | Bad parameters | Check model name and size are from the tables above |
| `statusCode: 403 AccessDenied.Unpurchased` | Model not activated | Tell user to enable the model in Alibaba Cloud console |

**On any error**: Do NOT try alternative models, alternative endpoints, or read config files. Report the error to the user clearly.

## Notes

- Image generation calls are synchronous and typically return in 10-60 seconds (wan2.7-image-pro can take longer)
- Image URLs expire; download promptly
- English prompts usually produce the best results; Chinese is also supported
- When the user does not specify a model or size, default to `wan2.7-image` + `1024x1024`
