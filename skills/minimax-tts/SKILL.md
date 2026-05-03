---
name: minimax-tts
description: >-
  Use this skill when the user wants to convert text to speech using MiniMax's
  T2A (Text-to-Audio) API. Supports multiple voice styles, emotional control,
  and voice cloning. Use when 用户提到 语音合成、文字转语音、TTS、朗读、
  读出来、生成语音、生成音频、文本转音频、配音、念出来、MiniMax 语音。
license: Complete terms in LICENSE.txt
version: 1.2.1
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
provider: minimax
tags:
  - media
  - audio
  - tts
  - speech
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
      name: MiniMax 语音合成
      short_desc: 基于 MiniMax Speech-02 的文本转语音技能
      description: >-
        Use this skill when the user wants to convert text to speech using MiniMax's T2A (Text-to-Audio) API. Supports multiple voice styles, emotional control, and voice cloning. Use when 用户提到 语音合成、文字转语音、TTS、朗读、 读出来、生成语音、生成音频、文本转音频、配音、念出来、MiniMax 语音。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:f372052761b12559
      translated_by: human
    en-US:
      name: MiniMax Text-to-Speech
      short_desc: Text-to-speech skill powered by MiniMax Speech-02
      description: >-
        Use this skill when the user wants to convert text to speech using MiniMax's T2A (Text-to-Audio) API. Supports multiple voice styles, emotional control, and voice cloning. Use when the user mentions text-to-speech, TTS, read aloud, read it out, generate speech, generate audio, text-to-audio, voiceover, narrate it, MiniMax voice.
      body: ./SKILL.md
      source_hash: sha256:f372052761b12559
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#007AFF" stroke-width="1.5" fill="#007AFF"
    fill-opacity="0.1"/><path d="M8 9v6M11 7v10M14 10v4M17 8v8"
    stroke="#007AFF" stroke-width="2"
    stroke-linecap="round"/></svg>
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
  listed: false
---

# minimax-tts Skill

## Mandatory Rules (violations will cause feature failure)

1. **Must access agent-service over HTTPS** — `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Use Bash curl throughout** — do not use the HttpRequest tool or Python

## Complete Execution Flow

### Prerequisites

- The user has configured a MiniMax Media Provider with an API Key under Resources → Compute
- agent-service is running

### Voice Selection Guide

| voice_id | Characteristics | Use Cases |
|----------|------|---------|
| male-qn-qingse | Young male voice | Narration, podcasts |
| female-shaonv | Young female voice | Audiobooks, dialogue |
| female-yujie | Mature female voice | Professional broadcasting |
| presenter_male | Male anchor voice | News, formal occasions |
| presenter_female | Female anchor voice | News, formal occasions |

### Generate Speech

MiniMax TTS returns JSON (containing an audio URL or hex data); use `"json"` for `responseType`.

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "provider-minimax-media-001",
    "endpoint": "/t2a_v2",
    "body": {
      "model": "speech-02-hd",
      "text": "要转换为语音的文本内容",
      "voice_setting": {
        "voice_id": "male-qn-qingse",
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0
      },
      "audio_setting": {
        "format": "mp3",
        "sample_rate": 32000
      }
    },
    "responseType": "json"
  }'
```

### Response Handling

MiniMax TTS returns JSON which, depending on the request parameters, may contain a URL or hex format:

**URL format response** (recommended, requires `"format": "url"` in audio_setting):
```json
{
  "success": true,
  "data": {
    "data": {
      "audio": {
        "audio_url": "https://...",
        "status": 1
      }
    },
    "base_resp": { "status_code": 0, "status_msg": "success" }
  },
  "statusCode": 200
}
```

**Hex format response** (default):
```json
{
  "success": true,
  "data": {
    "data": {
      "audio": {
        "data": "hex编码的音频数据...",
        "status": 1
      }
    },
    "extra_info": {
      "audio_length": 12345,
      "audio_sample_rate": 32000,
      "audio_size": 67890
    }
  },
  "statusCode": 200
}
```

### Download and Upload to media-store

Audio URLs have a time limit, so they must be downloaded immediately and saved to the local media-store.

**URL format**:
```bash
PORT=$(cat ~/.desirecore/agent-service.port)
AUDIO_URL="响应中的audio_url"
curl -sL "$AUDIO_URL" -o /tmp/minimax-tts.mp3 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-tts.mp3;type=audio/mpeg"
```

**Hex format**:
```bash
PORT=$(cat ~/.desirecore/agent-service.port)
HEX_DATA="响应中的hex数据"
echo -n "$HEX_DATA" | xxd -r -p > /tmp/minimax-tts.mp3 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-tts.mp3;type=audio/mpeg"
```

Extract the `mediaId` field from the JSON response.

### Display the Result

Reference it in your reply using the dc-media protocol (the frontend will automatically detect the audio extension and render a player):

```
![语音合成结果](dc-media://这里替换为mediaId)
```

### Parameter Reference

| Parameter | Description | Default |
|------|------|--------|
| model | Model | "speech-02-hd" (HD) or "speech-02-turbo" (fast) |
| text | Text to convert | Max 10000 characters |
| voice_setting.voice_id | Voice persona | "male-qn-qingse" |
| voice_setting.speed | Speaking speed | 1.0 |
| voice_setting.vol | Volume | 1.0 |
| voice_setting.pitch | Pitch | 0 |
| audio_setting.format | Audio format | "mp3" |
| audio_setting.sample_rate | Sample rate | 32000 |

### Special Syntax

MiniMax TTS supports inserting pause markers in the text:
- `<#0.5#>` — pause for 0.5 seconds
- `<#2#>` — pause for 2 seconds
- Valid range: 0.01 ~ 99.99 seconds

Example: `"你好<#1#>欢迎来到 DesireCore"`

### Error Handling

- `success: false` + `statusCode: 400`: empty text or malformed parameters
- `success: false` + `statusCode: 401`: invalid API Key
- `success: false` + `statusCode: 429`: rate limited
- `success: false` + `error: "未找到匹配的供应商"`: MiniMax Media Provider not configured

### Notes

- For text exceeding 3000 characters, streaming output is recommended (proxy mode does not yet support streaming)
- Returned audio_url is valid for 24 hours
- Unless the user specifies otherwise, default to `speech-02-hd` + `male-qn-qingse` + 1.0x speed
- For long text, split it into segments of no more than 3000 characters each
