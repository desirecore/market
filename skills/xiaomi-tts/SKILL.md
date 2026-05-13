---
name: xiaomi-tts
description: >-
  Use this skill when the user wants to convert text to speech using Xiaomi
  MiMo's TTS models (mimo-v2.5-tts). Uses OpenAI-compatible chat/completions
  API with audio response. Supports multiple preset voices and custom voice
  design.
  Use when 用户提到 语音合成、文字转语音、TTS、朗读、读出来、生成语音、
  生成音频、文本转音频、配音、念出来、小米语音、MiMo 语音、小米 TTS。
license: Complete terms in LICENSE.txt
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: xiaomi
tags:
  - media
  - audio
  - tts
  - speech
  - xiaomi
  - mimo
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-05-08'
  i18n:
    default_locale: zh-CN
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 小米 MiMo 语音合成
      short_desc: 基于小米 MiMo 的文本转语音技能
      description: >-
        当用户希望使用小米 MiMo 的 TTS 模型（mimo-v2.5-tts）将文本转为语音时使用此技能。基于 OpenAI 兼容的 chat/completions API，响应中携带音频。支持多种预置音色和自定义音色设计。用户提到 语音合成、文字转语音、TTS、朗读、读出来、生成语音、生成音频、文本转音频、配音、念出来、小米语音、MiMo 语音、小米 TTS。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:2dd06b13152349e5
      translated_by: human
    en-US:
      name: Xiaomi MiMo TTS
      short_desc: Text-to-speech synthesis using Xiaomi MiMo models
      source_hash: sha256:2dd06b13152349e5
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#FF6900" stroke-width="1.5" fill="#FF6900"
    fill-opacity="0.1"/><path d="M8 9v6M11 7v10M14 10v4M17 8v8"
    stroke="#FF6900" stroke-width="2"
    stroke-linecap="round"/></svg>
  short_desc: 基于小米 MiMo 的文本转语音技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# xiaomi-tts 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **必须通过 `/api/media/upload` 上传到 media-store** — /tmp 仅作下载/解码中转，不可直接以本地路径作为最终输出
3. **必须使用 `dc-media://` 协议展示音频** — 唯一能让前端正确渲染的方式
4. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
5. **使用 /chat/completions 端点** — 小米 MiMo TTS 使用 OpenAI 兼容格式

## 模型选择指南

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| mimo-v2.5-tts | 标准 TTS，多种预置音色 | **默认首选**，常规语音合成 |
| mimo-v2.5-tts-voicedesign | 自定义音色设计 | 需要特定音色描述生成 |
| mimo-v2.5-tts-voiceclone | 声音克隆 | 需要克隆特定人声（需上传参考音频） |

**默认规则**：用户未指定模型时，使用 `mimo-v2.5-tts`。

## 音色选择指南

### 预置音色

| voice_id | 名称 | 特点 |
|----------|------|------|
| default_zh | 默认中文 | 中文通用女声 |
| default_en | 默认英文 | 英文通用女声 |
| mimo_default | MiMo 默认 | MiMo 特色音色 |
| Bingtang | 冰糖 | 甜美女声 |
| Moli | 茉莉 | 温柔女声 |
| Suda | 苏打 | 年轻男声 |
| Baihua | 白桦 | 成熟男声 |
| Mia | Mia | 英文女声 |
| Chloe | Chloe | 英文女声 |
| Milo | Milo | 英文男声 |
| Dean | Dean | 英文男声 |

**默认规则**：中文内容用 `Bingtang`，英文内容用 `Mia`，用户未指定时按内容语言自动选择。

## 完整执行流程（严格按此三步执行）

### 前置条件

- 用户已在资源管理器-算力中配置小米 MiMo Provider 并填写 API Key
- agent-service 正在运行

### 第一步：调用 TTS API

通过 media-proxy 的 /chat/completions 端点生成语音。

**重要**：messages 必须使用 `assistant` role（不是 user），要合成的文本放在 assistant 消息的 content 中。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "xiaomi",
    "serviceType": "tts",
    "endpoint": "/chat/completions",
    "body": {
      "model": "mimo-v2.5-tts",
      "messages": [
        {
          "role": "assistant",
          "content": "这里替换为要合成的文本内容"
        }
      ],
      "voice": "Bingtang",
      "audio": {"format": "mp3"}
    },
    "responseType": "json"
  }'
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "id": "chatcmpl-...",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "audio": {
            "data": "base64编码的音频数据...",
            "format": "mp3"
          }
        },
        "finish_reason": "stop"
      }
    ]
  },
  "statusCode": 200
}
```

从 `data.choices[0].message.audio.data` 提取 base64 编码的音频数据。

### 第二步：解码并上传到 media-store

音频以 base64 返回，需要解码后保存到本地 media-store。

**推荐方式**（先保存完整响应到文件，避免 shell 参数过长）：

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
# 将完整请求和响应保存到文件
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "xiaomi",
    "serviceType": "tts",
    "endpoint": "/chat/completions",
    "body": {
      "model": "mimo-v2.5-tts",
      "messages": [{"role": "assistant", "content": "要合成的文本"}],
      "voice": "Bingtang",
      "audio": {"format": "mp3"}
    },
    "responseType": "json"
  }' > /tmp/xiaomi-tts-response.json

# 提取 base64 音频数据并解码
cat /tmp/xiaomi-tts-response.json | jq -r '.data.choices[0].message.audio.data' | base64 -d > /tmp/xiaomi-tts.mp3

# 上传到 media-store
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/xiaomi-tts.mp3;type=audio/mpeg"
```

从 JSON 响应中提取 `mediaId` 字段（格式如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3`）。

### 第三步：用 dc-media 协议展示音频

在你的回复文本中直接写 Markdown 语法：

```
![语音合成结果](dc-media://这里替换为mediaId)
```

例如：`![TTS: 你好世界](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.mp3)`

前端会自动检测 `.mp3` 扩展名并渲染为音频播放器。

## 参数映射

### 请求体参数（放在 body 中）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `model` | 模型名称 | "mimo-v2.5-tts" |
| `messages[0].role` | **必须为 "assistant"** | "assistant"（固定） |
| `messages[0].content` | 要合成的文本 | 必填 |
| `voice` | 音色 ID | "Bingtang"（中文）/ "Mia"（英文） |
| `audio.format` | 音频格式 | "mp3"（可选 "wav"） |

### 用户意图映射

| 用户意图 | 参数选择 |
|---------|---------|
| 甜美/可爱 | voice: "Bingtang" |
| 温柔/知性 | voice: "Moli" |
| 年轻男声 | voice: "Suda" |
| 成熟男声 | voice: "Baihua" |
| 英文女声 | voice: "Mia" 或 "Chloe" |
| 英文男声 | voice: "Milo" 或 "Dean" |
| 高音质/无损 | audio.format: "wav" |

## 错误处理

- `success: false` + `error: "未找到匹配的供应商"`：未配置小米 MiMo Provider 或未启用
- `success: false` + `error: "未配置 API Key"`：未填写 API Key
- `statusCode: 401`：API Key 无效或已过期
- `statusCode: 429`：频率限制，稍后重试
- `statusCode: 400`：参数错误（如 voice 不存在、文本为空）
- `statusCode: 403`：模型未开通或权限不足

## 注意事项

- 调用是同步的，通常 3-15 秒返回（视文本长度而定）
- 音频以 base64 返回，无外部 URL 时效问题，但数据量较大时注意 shell 参数长度限制
- 长文本建议分段合成（每段不超过 500 字），然后逐段上传展示
- 如果用户未明确要求音色/格式，默认使用 `mimo-v2.5-tts` + 按语言选音色 + `mp3`
- Token Plan 密钥（tp- 前缀）使用 `https://token-plan-cn.xiaomimimo.com/v1` 端点
- 按量付费密钥使用 `https://api.xiaomimimo.com/v1` 端点
- media-proxy 会自动根据配置选择正确的端点，技能无需区分
