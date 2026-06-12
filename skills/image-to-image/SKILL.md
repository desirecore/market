---
name: image-to-image
description: >-
  Use this skill when the user wants to edit, transform, or modify an existing
  image using AI. Supports image-to-image generation via the OpenAI-compatible
  images/generations API with gpt-image-2 model.
  Use when 用户提到 图生图、修改图片、编辑图片、图片变换、改图、
  换背景、换风格、图片编辑、以图生图、参考图、基于这张图、
  把这张图改成、在这张图上、image edit、img2img。
license: Complete terms in LICENSE.txt
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: auto
tags:
  - media
  - image
  - editing
  - img2img
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-06-12'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 图生图
      short_desc: 基于参考图片的 AI 图像编辑与变换技能
      description: >-
        当用户希望基于已有图片进行编辑、变换或修改时使用此技能。支持通过 gpt-image-2 模型进行图生图，使用 OpenAI 兼容的 images/generations API。用户提到 图生图、修改图片、编辑图片、图片变换、改图、换背景、换风格、图片编辑、以图生图、参考图、基于这张图、把这张图改成、在这张图上。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:b3d5e7f01a2c4e8f
      translated_by: human
    en-US:
      name: Image-to-Image
      short_desc: AI image editing and transformation based on reference images
      description: "Use this skill when the user wants to edit, transform, or modify an existing image using AI. Supports image-to-image via gpt-image-2 model through the OpenAI-compatible images/generations API. Trigger keywords: image edit, img2img, modify image, transform image, change background, change style, based on this image, edit this image."
      body: ./SKILL.md
      source_hash: sha256:b3d5e7f01a2c4e8f
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#007AFF" stroke-width="1.5" fill="#007AFF"
    fill-opacity="0.1"/><path d="M6 15l3-4 2.5 3 3.5-5 4 6H6z" fill="#007AFF"
    fill-opacity="0.3" stroke="#007AFF" stroke-width="1.2"
    stroke-linejoin="round"/><path d="M14 4l3 3-3 3" stroke="#007AFF"
    stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/><path d="M17 7H11" stroke="#007AFF"
    stroke-width="1.5" stroke-linecap="round"/></svg>
  short_desc: 基于参考图片的 AI 图像编辑与变换技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# image-to-image Skill

## Mandatory Rules (violations cause failure)

1. **STRICTLY follow the execution steps below** — do NOT improvise, explore alternative endpoints, or try models not listed in this document
2. **Must access agent-service over HTTPS** — the API address is already provided in the system prompt under "本机 API" section (e.g. `https://127.0.0.1:PORT`); use it directly with `-k` to skip certificate verification
3. **Must upload to media-store via `/api/media/upload`** — `/tmp` is only a transient download/decode location, never use a local path as the final output
4. **Must use the `dc-media://` protocol to display images** — the only form the frontend can render correctly
5. **Use Bash curl throughout** — do not use the HttpRequest tool or Python (except for the b64 extraction script)
6. **Use `/images/generations` endpoint with `image` field** — same endpoint as text-to-image, the `image` field triggers image-to-image mode
7. **Only use `gpt-image-2` model** — do NOT try dall-e-3, wan2.7-image, or any other model for image-to-image

## Provider & Default Compute

This skill uses the `gpt-image-2` model through the DesireCore Cloud provider. You do NOT need to specify a provider — just pass `"serviceType": "image_gen"` and the system will automatically route to the correct provider.

- **DesireCore Cloud** (default, always available): The built-in compute provider supports `gpt-image-2` for image-to-image. Users can use it immediately without any configuration.

**Never** try to query provider lists, read compute.json, or explore available models through API calls. The model listed above is guaranteed to work.

## When to Use This Skill

This skill should be triggered when the user:
- Sends an image and asks to modify/edit/transform it
- Asks to change the style, background, or content of an existing image
- Wants to use a reference image to generate a new image
- Uses keywords like "图生图", "修改图片", "编辑图片", "基于这张图", "img2img"

**Do NOT use this skill** when the user simply asks to "generate an image" or "draw something" without providing a reference image — use the `dashscope-image-gen` skill instead.

## How to Identify the User's Input Image

The user's input image can come from several sources:

1. **Image in the current conversation**: The user uploads an image in chat. It appears in the conversation as `dc-media://<mediaId>` or as an image attachment. Extract the `mediaId` (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`).

2. **Image from a previous generation**: The user refers to a previously generated image (e.g. "modify the image above", "change the pig picture"). Look back in the conversation for the most recent `dc-media://<mediaId>` reference.

3. **Image URL**: The user provides an external URL. Download it first with `curl -sL "<url>" -o /tmp/input-image.png`.

## Full Execution Flow (strictly follow these steps)

### How to get the API address

The system prompt already contains the agent-service API address under "本机 API" (e.g. `Agent Service: https://127.0.0.1:61000`). Extract the URL from there and use it directly.

If for any reason you cannot find it in the system prompt, use this fallback:

```bash
PORT=$(cat "${DESIRECORE_HOME:-$HOME/.desirecore}/agent-service.port")
# Then use https://127.0.0.1:${PORT}
```

### Step 1: Download the input image and convert to base64

Download the user's image from media-store and convert it to a base64 data URL:

```bash
# Download from media-store (replace <mediaId> with the actual media ID)
curl -sk "https://127.0.0.1:${PORT}/api/media/<mediaId>" -o /tmp/input-image.png

# Convert to base64 data URL (NEVER print base64 to terminal)
python3 -c "
import base64, sys
with open('/tmp/input-image.png', 'rb') as f:
    data = f.read()
b64 = base64.b64encode(data).decode()
# Detect MIME type from magic bytes
mime = 'image/png'
if data[:2] == b'\xff\xd8':
    mime = 'image/jpeg'
elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
    mime = 'image/webp'
data_url = f'data:{mime};base64,{b64}'
with open('/tmp/input-image-dataurl.txt', 'w') as f:
    f.write(data_url)
print(f'OK: data URL saved, image size: {len(data)} bytes, mime: {mime}')
"
```

**CRITICAL**: The base64 data URL can be very large (1-5MB). NEVER print it to the terminal. Always save to file.

### Step 2: Generate the edited image (single curl command)

Call `/images/generations` with the `image` field through media-proxy. **You MUST use this exact request structure**:

```bash
# Read data URL from file and build request
IMAGE_DATA_URL=$(cat /tmp/input-image-dataurl.txt)

# Save response to temp file to avoid base64 flooding the terminal
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"serviceType\": \"image_gen\",
    \"endpoint\": \"/images/generations\",
    \"body\": {
      \"model\": \"gpt-image-2\",
      \"prompt\": \"Replace this with the edit description in English\",
      \"image\": \"${IMAGE_DATA_URL}\",
      \"size\": \"1024x1024\",
      \"n\": 1
    },
    \"responseType\": \"json\"
  }" -o /tmp/img2img-response.json

# Check success and extract b64_json to image file (NEVER cat the response to stdout)
python3 -c "
import json, base64, sys
with open('/tmp/img2img-response.json') as f:
    resp = json.load(f)
if not resp.get('success'):
    print('ERROR:', json.dumps(resp, ensure_ascii=False)[:500])
    sys.exit(1)
b64 = resp['data']['data'][0]['b64_json']
with open('/tmp/img2img-output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('OK: saved to /tmp/img2img-output.png')
"
```

**CRITICAL**: The response contains a large base64 image (~2MB). NEVER print the raw response or b64_json to the terminal. Always save to file with `-o` and extract with the python3 script above.

**IMPORTANT**: Combine Step 1 and Step 2 into a single Bash tool call to minimize round trips. The full script should: download image → convert to base64 → build curl request → extract result.

**Response format** (saved in `/tmp/img2img-response.json`):
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

### Step 3: Upload to media-store

```bash
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/img2img-output.png;type=image/png"
```

Pick the `mediaId` field from the JSON response (format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`).

### Step 4: Render the image via the dc-media protocol

In your reply text, write Markdown image syntax directly:

```
![Image description](dc-media://replace-with-mediaId)
```

The frontend will translate `dc-media://` into a reachable image URL and render it.

## Parameter Mapping

### Size selection

Pass `size` in the `body` object:

| User intent | size value |
|---------|-----------|
| Square / default | "1024x1024" |
| Landscape / wide | "1536x1024" |
| Portrait / tall | "1024x1536" |
| Auto (let model decide) | "auto" |

### Prompt guidelines for image-to-image

- **Be specific about what to change**: "Change the background to a beach scene" is better than "edit this image"
- **Describe the desired result**: "A pig wearing an astronaut suit in space" rather than "make it space-themed"
- **English prompts usually produce better results**; Chinese is also supported
- **Mention what to preserve**: "Keep the main subject but change the background" helps maintain fidelity

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| `"No matching provider"` | No enabled provider supports `image_gen` | Tell user to enable a provider with image_gen support in settings |
| `"API Key not configured"` | API Key missing | Tell user to configure API key |
| `statusCode: 401` | API Key invalid or expired | Tell user to check API key |
| `statusCode: 429` | Rate limited | Wait and retry once |
| `statusCode: 400` | Bad parameters | Check model name and size; ensure image is valid base64 |
| Image download fails | mediaId not found or expired | Ask user to re-upload the image |

**On any error**: Do NOT try alternative models, alternative endpoints, or read config files. Report the error to the user clearly.

## Notes

- Image-to-image calls are synchronous and typically return in 15-60 seconds
- Input image is sent as base64 in the request body, which increases request size significantly
- The `gpt-image-2` model can handle various edit types: style transfer, background change, object modification, artistic transformation
- When the user does not specify a size, default to `1024x1024`
- If the user's input image is very large, consider mentioning that processing may take longer
