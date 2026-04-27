---
name: OpenAI 语音合成
description: >-
  Use this skill when the user wants to convert text to speech audio.
  Calls the OpenAI TTS API through the media proxy to generate audio files.
  Supports multiple voices (alloy, echo, fable, onyx, nova, shimmer) and
  audio formats (mp3, opus, aac, flac).
  Use when 用户提到 语音合成、文字转语音、TTS、朗读、读出来、
  生成语音、生成音频、文本转音频、配音、念出来。
license: Complete terms in LICENSE.txt
version: 1.1.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: openai
tags:
  - media
  - audio
  - tts
  - speech
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
    stroke="#007AFF" stroke-width="1.5" fill="#007AFF"
    fill-opacity="0.1"/><path d="M8 9v6M11 7v10M14 10v4M17 8v8"
    stroke="#007AFF" stroke-width="2"
    stroke-linecap="round"/></svg>
  short_desc: 基于 OpenAI TTS 的文本转语音技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# openai-tts 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
3. **`responseType` 必须为 `"binary"`** — OpenAI TTS 返回二进制音频流，不是 JSON

## 完整执行流程

### 前置条件

- 用户已在资源管理器-算力中配置 OpenAI Provider 并填写 API Key
- agent-service 正在运行

### 语音选择指南

| 语音 | 特点 | 适用场景 |
|------|------|---------|
| alloy | 中性平衡 | 通用（推荐默认） |
| echo | 低沉稳重 | 旁白、播客 |
| fable | 温暖叙事 | 故事、有声书 |
| onyx | 深沉有力 | 新闻播报 |
| nova | 活泼明亮 | 对话、教学 |
| shimmer | 柔和温柔 | 冥想、助眠 |

### 生成语音

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "serviceType": "tts",
    "endpoint": "/audio/speech",
    "body": {
      "model": "tts-1",
      "input": "要转换的文本内容",
      "voice": "alloy",
      "response_format": "mp3",
      "speed": 1.0
    },
    "responseType": "binary",
    "binaryMimeType": "audio/mpeg"
  }'
```

成功响应（代理层自动保存音频文件到 media-store）：

```json
{
  "success": true,
  "media": {
    "type": "audio",
    "mediaId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3",
    "name": "media-proxy-generated",
    "mimeType": "audio/mpeg",
    "size": 123456
  },
  "statusCode": 200
}
```

### 展示结果

从响应中提取 `media.mediaId`，音频文件可通过以下 URL 访问：

```
https://127.0.0.1:${PORT}/api/media/${mediaId}
```

向用户提供播放链接即可。

### 参数说明

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| model | 模型 | "tts-1"（标准）, "tts-1-hd"（高清） | tts-1 |
| input | 要转换的文本 | 最大 4096 字符 | — |
| voice | 语音角色 | alloy, echo, fable, onyx, nova, shimmer | alloy |
| response_format | 音频格式 | mp3, opus, aac, flac | mp3 |
| speed | 语速倍率 | 0.25 - 4.0 | 1.0 |

### binaryMimeType 映射

根据 `response_format` 设置对应的 `binaryMimeType`：

| response_format | binaryMimeType |
|----------------|----------------|
| mp3 | audio/mpeg |
| opus | audio/opus |
| aac | audio/aac |
| flac | audio/flac |

### 错误处理

- `success: false` + `statusCode: 400`：通常是 input 为空或超长
- `success: false` + `statusCode: 401`：API Key 无效或过期
- `success: false` + `statusCode: 429`：速率限制，建议稍后重试
- `success: false` + `error: "未找到匹配的供应商"`：用户未配置 OpenAI Provider
- `success: false` + `error: "未配置 API Key"`：用户未填写 OpenAI API Key

### 注意事项

- OpenAI TTS API 返回的是二进制音频流，不是 JSON，所以 `responseType` 必须设为 `"binary"`
- `binaryMimeType` 必须与 `response_format` 对应，否则文件扩展名可能不正确
- `tts-1-hd` 音质更好但生成速度较慢，适合离线场景
- input 最大 4096 字符，超长文本需要分段处理
- 如果用户未明确要求，默认使用 `tts-1` + `alloy` + `mp3` + `1.0` 倍速
