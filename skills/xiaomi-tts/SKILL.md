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
    default_locale: en-US
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
      source_hash: sha256:afa1138c9b2cbd20
      translated_by: human
    en-US:
      name: Xiaomi MiMo TTS
      short_desc: Text-to-speech synthesis using Xiaomi MiMo models
      description: "Use this skill when the user wants to convert text to speech using Xiaomi MiMo's TTS models (mimo-v2.5-tts). Built on the OpenAI-compatible chat/completions API with audio response, supporting multiple preset voices and custom voice design. Trigger keywords: text-to-speech, TTS, read aloud, narrate, generate audio, voice synthesis, MiMo voice, Xiaomi TTS."
      body: ./SKILL.md
      source_hash: sha256:afa1138c9b2cbd20
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

# xiaomi-tts Skill

## Mandatory Rules (violations cause failure)

1. **Must access agent-service over HTTPS** — use `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Must upload to media-store via `/api/media/upload`** — `/tmp` is only a transient download/decode location, never use a local path as the final output
3. **Must use the `dc-media://` protocol to display audio** — the only form the frontend can render correctly
4. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
5. **Use the `/chat/completions` endpoint** — Xiaomi MiMo TTS speaks OpenAI-compatible chat format

## Model Selection

| Model | Characteristics | When to use |
|------|------|---------|
| mimo-v2.5-tts | Standard TTS, multiple preset voices | **Default**, regular speech synthesis |
| mimo-v2.5-tts-voicedesign | Custom voice design | When you need a voice generated from a description |
| mimo-v2.5-tts-voiceclone | Voice cloning | When you need to clone a specific voice (reference audio required) |

**Default rule**: if the user does not specify a model, use `mimo-v2.5-tts`.

## Voice Selection

### Preset Voices

| voice_id | Name | Characteristics |
|----------|------|------|
| default_zh | Default Chinese | General-purpose Chinese female voice |
| default_en | Default English | General-purpose English female voice |
| mimo_default | MiMo Default | MiMo's signature voice |
| Bingtang | Bingtang | Sweet female voice |
| Moli | Moli | Soft, gentle female voice |
| Suda | Suda | Young male voice |
| Baihua | Baihua | Mature male voice |
| Mia | Mia | English female voice |
| Chloe | Chloe | English female voice |
| Milo | Milo | English male voice |
| Dean | Dean | English male voice |

**Default rule**: use `Bingtang` for Chinese text and `Mia` for English text; if the user doesn't specify, pick automatically by content language.

## Full Execution Flow (strictly three steps)

### Prerequisites

- The user has configured a Xiaomi MiMo provider in Resource Manager → Compute and filled in an API Key
- agent-service is running

### Step 1: Call the TTS API

Generate speech via media-proxy's `/chat/completions` endpoint.

**Important**: `messages` must use the `assistant` role (not `user`); the text to synthesize goes in the assistant message's content.

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
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
          "content": "Replace this with the text to synthesize"
        }
      ],
      "voice": "Bingtang",
      "audio": {"format": "mp3"}
    },
    "responseType": "json"
  }'
```

**Example response**:
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
            "data": "base64-encoded audio data...",
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

Pull the base64-encoded audio data from `data.choices[0].message.audio.data`.

### Step 2: Decode and upload to media-store

The audio comes back as base64; decode it and save to the local media-store.

**Recommended approach** (write the full response to a file first to avoid overlong shell arguments):

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
# Save the full request and response to a file
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "xiaomi",
    "serviceType": "tts",
    "endpoint": "/chat/completions",
    "body": {
      "model": "mimo-v2.5-tts",
      "messages": [{"role": "assistant", "content": "Text to synthesize"}],
      "voice": "Bingtang",
      "audio": {"format": "mp3"}
    },
    "responseType": "json"
  }' > /tmp/xiaomi-tts-response.json

# Extract and decode the base64 audio data
cat /tmp/xiaomi-tts-response.json | jq -r '.data.choices[0].message.audio.data' | base64 -d > /tmp/xiaomi-tts.mp3

# Upload to media-store
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/xiaomi-tts.mp3;type=audio/mpeg"
```

Pick the `mediaId` field from the JSON response (format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3`).

### Step 3: Render the audio via the dc-media protocol

In your reply text, write Markdown syntax directly:

```
![TTS result](dc-media://replace-with-mediaId)
```

For example: `![TTS: Hello world](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.mp3)`

The frontend detects the `.mp3` extension and renders an audio player.

## Parameter Mapping

### Request body parameters (inside `body`)

| Parameter | Description | Default |
|------|------|--------|
| `model` | Model name | "mimo-v2.5-tts" |
| `messages[0].role` | **Must be "assistant"** | "assistant" (fixed) |
| `messages[0].content` | Text to synthesize | required |
| `voice` | Voice ID | "Bingtang" (Chinese) / "Mia" (English) |
| `audio.format` | Audio format | "mp3" (also accepts "wav") |

### User intent mapping

| User intent | Parameter |
|---------|---------|
| Sweet / cute | voice: "Bingtang" |
| Gentle / refined | voice: "Moli" |
| Young male | voice: "Suda" |
| Mature male | voice: "Baihua" |
| English female | voice: "Mia" or "Chloe" |
| English male | voice: "Milo" or "Dean" |
| High fidelity / lossless | audio.format: "wav" |

## Error Handling

- `success: false` + `error: "No matching provider"`: Xiaomi MiMo provider not configured or disabled
- `success: false` + `error: "API Key not configured"`: API Key missing
- `statusCode: 401`: API Key invalid or expired
- `statusCode: 429`: rate limited, retry later
- `statusCode: 400`: bad parameters (e.g. unknown voice, empty text)
- `statusCode: 403`: model not activated or insufficient permission

## Notes

- Calls are synchronous, typically 3–15 seconds depending on text length
- Audio is returned as base64, so URL expiry is not a concern, but watch shell argument length on long responses
- For long text, split into segments (no more than ~500 chars each), then upload and render each segment
- When the user doesn't specify, default to `mimo-v2.5-tts` + auto-selected voice by language + `mp3`
- Token Plan keys (prefix `tp-`) use the `https://token-plan-cn.xiaomimimo.com/v1` endpoint
- Pay-as-you-go keys use the `https://api.xiaomimimo.com/v1` endpoint
- media-proxy picks the correct endpoint based on configuration; the skill does not need to differentiate
