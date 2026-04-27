---
name: OpenAI 文生图
description: >-
  Use this skill when the user wants to generate images from text descriptions.
  Calls the OpenAI DALL-E 3 API through the media proxy to create images.
  Supports different sizes (1024x1024, 1792x1024, 1024x1792) and styles
  (natural, vivid). Use when 用户提到 生成图片、画图、文生图、创建图片、
  AI 绘画、生成插图、画一张、帮我画、设计图片、DALL-E。
license: Complete terms in LICENSE.txt
version: 1.3.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: openai
tags:
  - media
  - image
  - generation
  - dall-e
  - openai
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-04-25'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#34C759" stroke-width="1.5" fill="#34C759"
    fill-opacity="0.1"/><circle cx="8.5" cy="8.5" r="2" stroke="#34C759"
    stroke-width="1.2"/><path d="M3 16l5-5 4 4 3-3 6 6" stroke="#34C759"
    stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  short_desc: 基于 OpenAI DALL-E 3 的文本生成图片技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# openai-image-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须使用 `"response_format": "url"`** — 禁止 `"b64_json"`，base64 会导致输出截断
2. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
3. **必须通过 `/api/media/upload` 上传到 media-store** — 禁止保存到本地路径
4. **必须使用 `dc-media://` 协议展示图片** — 唯一能让前端正确渲染的方式
5. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python

## 完整执行流程（严格按此三步执行）

### 第一步：调用 API 生成图片

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "serviceType": "image_gen",
    "endpoint": "/images/generations",
    "body": {
      "model": "dall-e-3",
      "prompt": "这里替换为图片描述",
      "n": 1,
      "size": "1024x1024",
      "style": "vivid",
      "quality": "standard",
      "response_format": "url"
    },
    "responseType": "json"
  }'
```

从 JSON 响应中提取 `data.data[0].url` 得到图片 URL。`data.data[0].revised_prompt` 是 DALL-E 优化后的提示词，可展示给用户。

### 第二步：下载并上传到 media-store

OpenAI URL 仅 1 小时有效，必须立即下载。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
IMAGE_URL="第一步拿到的图片URL"
curl -sL "$IMAGE_URL" -o /tmp/dalle-gen.png && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/dalle-gen.png;type=image/png"
```

从 JSON 响应中提取 `mediaId` 字段。

### 第三步：用 dc-media 协议展示图片

在你的回复文本中直接写 Markdown 图片语法：

```
![图片描述](dc-media://这里替换为mediaId)
```

前端会自动将 `dc-media://` 转为可访问的图片 URL 并渲染。

## 参数映射

| 用户意图 | size | style | quality |
|---------|------|-------|---------|
| 正方形（默认） | "1024x1024" | "vivid" | "standard" |
| 横版/风景 | "1792x1024" | "vivid" | "standard" |
| 竖版/手机 | "1024x1792" | "vivid" | "standard" |
| 写实/自然 | — | "natural" | — |
| 高清 | — | — | "hd" |

## 错误处理

- `"error": "未找到匹配的供应商"`：未配置 OpenAI Provider
- `statusCode: 401`：API Key 无效或过期
- `statusCode: 429`：速率限制，稍后重试
