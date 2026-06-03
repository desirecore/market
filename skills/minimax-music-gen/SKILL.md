---
name: minimax-music-gen
description: >-
  Use this skill when the user wants to generate music using MiniMax's
  Music Generation API. Supports text-to-music with lyrics, instrumental
  generation, and music cover. Use when 用户提到 生成音乐、文生音乐、
  AI 作曲、创作歌曲、写一首歌、音乐生成、AI 音乐、MiniMax 音乐、
  作词作曲、纯音乐、伴奏、翻唱、cover。
license: Complete terms in LICENSE.txt
version: 1.1.4
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
provider: minimax
tags:
  - media
  - audio
  - music
  - generation
  - minimax
requires:
  tools:
    - Bash
metadata:
  author: desirecore
  updated_at: '2026-05-05'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: MiniMax 音乐生成
      short_desc: 基于 MiniMax Music 2.6 的文本生成音乐技能
      description: >-
        Use this skill when the user wants to generate music using MiniMax's Music Generation API. Supports text-to-music with lyrics, instrumental generation, and music cover. Use when 用户提到 生成音乐、文生音乐、 AI 作曲、创作歌曲、写一首歌、音乐生成、AI 音乐、MiniMax 音乐、 作词作曲、纯音乐、伴奏、翻唱、cover。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:403153a9c1da2ad9
      translated_by: human
    en-US:
      name: MiniMax Music Generation
      short_desc: Text-to-music skill powered by MiniMax Music 2.6
      description: >-
        Use this skill when the user wants to generate music using MiniMax's Music Generation API. Supports text-to-music with lyrics, instrumental generation, and music cover. Use when the user mentions generating music, text-to-music, AI composing, creating songs, writing a song, music generation, AI music, MiniMax music, songwriting, instrumental music, accompaniment, cover, or remake.
      body: ./SKILL.md
      source_hash: sha256:f3785e1da2fc5a11
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#AF52DE" stroke-width="1.5" fill="#AF52DE"
    fill-opacity="0.1"/><path d="M9 18V6l10-2v12" stroke="#AF52DE"
    stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/><circle cx="6.5" cy="18" r="2.5" fill="#AF52DE"
    fill-opacity="0.6"/><circle cx="16.5" cy="16" r="2.5" fill="#AF52DE"
    fill-opacity="0.6"/></svg>
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# minimax-music-gen Skill

## Mandatory Rules (violations will cause functionality to fail)

1. **Must access agent-service over HTTPS** — `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
3. **Do not use `output_format: "url"`** — URL downloads will return empty files in scenarios such as Token Plan due to CDN authentication failures. Always use the default hex format; audio data is returned directly in the API response

## Full Execution Flow

### Prerequisites

- The user has configured the MiniMax Provider (regular API or Token Plan) in Resource Manager → Compute and filled in the API Key
- agent-service is running

### Core Concepts

MiniMax Music Generation is a **synchronous API** (not an asynchronous task model); it returns audio data directly when called. Three modes are supported:

| Mode | model | Description |
|------|-------|-------------|
| Song generation | `music-2.6` | Provide prompt + lyrics to generate a song with vocals |
| Pure instrumental | `music-2.6` | Set `is_instrumental: true`; only a prompt is needed |
| Cover | `music-cover` | Provide a reference audio + prompt; rearrange based on the melodic skeleton |

### Lyrics Structure Tags

The lyrics field supports the following structure tags to organize song sections:

| Tag | Meaning |
|-----|---------|
| `[verse]` | Verse |
| `[chorus]` | Chorus |
| `[bridge]` | Bridge |
| `[intro]` | Intro |
| `[outro]` | Outro |
| `[interlude]` | Interlude |

Example lyrics format:
```
[verse]
夜晚的城市灯火阑珊
我独自走在回家的路上

[chorus]
这一刻时间仿佛停止
所有的喧嚣都已远去
```

### Generate a Song (with Vocals)

**Note: Do not pass the `output_format` parameter; use the default hex format.**

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "minimax",
    "serviceType": "music_gen",
    "endpoint": "/music_generation",
    "body": {
      "model": "music-2.6",
      "prompt": "独立民谣,温暖,治愈,吉他伴奏",
      "lyrics": "[verse]\n歌词内容\n\n[chorus]\n副歌内容",
      "audio_setting": {
        "format": "mp3",
        "sample_rate": 44100,
        "bitrate": 256000
      }
    },
    "responseType": "json"
  }'
```

### Generate Pure Instrumental

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "minimax",
    "serviceType": "music_gen",
    "endpoint": "/music_generation",
    "body": {
      "model": "music-2.6",
      "prompt": "电子音乐,氛围感,空灵,合成器铺底",
      "is_instrumental": true,
      "audio_setting": {
        "format": "mp3",
        "sample_rate": 44100,
        "bitrate": 256000
      }
    },
    "responseType": "json"
  }'
```

### Response Handling and Saving

The API returns JSON; audio data is hex-encoded and stored in the `data.data.audio.data` field.

**Response structure**:
```json
{
  "success": true,
  "data": {
    "data": {
      "audio": {
        "data": "hex编码的音频数据...",
        "status": 2
      }
    },
    "extra_info": {
      "music_duration": 180000,
      "music_sample_rate": 44100,
      "music_channel": 2,
      "bitrate": 256000,
      "music_size": 1234567
    },
    "base_resp": { "status_code": 0, "status_msg": "success" }
  },
  "statusCode": 200
}
```

**Note**: The `status` field means 1 = synthesizing (streaming scenario), 2 = synthesis complete. In non-streaming mode, the returned status is 2.

### Save the hex Audio Data to media-store

Extract the hex string from the `data.data.audio.data` field of the response JSON, convert it to binary, and upload:

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
# Save the API response to a temporary file (avoid letting large hex data overflow shell variables)
# Assume the curl output of the previous step has been saved to /tmp/minimax-music-resp.json

# Extract hex data and convert to binary (pure Bash, no Python dependency)
jq -r '.data.data.audio.data' /tmp/minimax-music-resp.json | xxd -r -p > /tmp/minimax-music.mp3

# Verify the file is valid (greater than 1KB and in audio format)
FILE_SIZE=$(stat -f%z /tmp/minimax-music.mp3 2>/dev/null || stat -c%s /tmp/minimax-music.mp3 2>/dev/null)
if [ "$FILE_SIZE" -lt 1024 ]; then
  echo "ERROR: 音频文件异常（${FILE_SIZE} 字节），可能生成失败"
  exit 1
fi

# Upload to media-store
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-music.mp3;type=audio/mpeg"
```

Extract the `mediaId` field from the upload response JSON.

### Display the Result

In the reply, use a dc-media protocol reference (the frontend will automatically detect the audio extension and render a player):

```
![音乐生成结果](dc-media://这里替换为mediaId)
```

### Parameter Descriptions

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| model | Model name | Yes | "music-2.6" |
| prompt | Music style/mood description | Optional when lyrics are present; required for pure instrumental/cover | — |
| lyrics | Lyrics (structure tags supported) | Required when not in pure instrumental mode | — |
| is_instrumental | Whether to generate pure instrumental | No | false |
| lyrics_optimizer | Auto-generate lyrics from the prompt | No | false |
| audio_setting.format | Audio format: mp3/wav/pcm | No | "mp3" |
| audio_setting.sample_rate | Sample rate: 16000/24000/32000/44100 | No | 32000 |
| audio_setting.bitrate | Bitrate: 32000/64000/128000/256000 | No | 128000 |

### Tips for Writing Prompts

The prompt is used to describe the music's style, mood, and instrumentation; commas are recommended to separate keywords:

- Style: `独立民谣`, `电子舞曲`, `古典钢琴`, `摇滚`, `R&B`, `爵士`, `嘻哈`
- Mood: `温暖`, `忧郁`, `欢快`, `史诗感`, `空灵`, `治愈`
- Instruments: `吉他伴奏`, `钢琴独奏`, `弦乐铺底`, `合成器`, `鼓点强劲`
- Structure: `渐进式编曲`, `开场留白渐入高潮`, `轻柔开头爆发副歌`

Example: `"独立民谣,温暖治愈,木吉他为主,轻柔的鼓点,渐进式编曲"`

### Auto-generated Lyrics Mode

If the user only describes the desired music style without providing lyrics, set `lyrics_optimizer: true` and the model will auto-generate lyrics from the prompt:

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "minimax",
    "serviceType": "music_gen",
    "endpoint": "/music_generation",
    "body": {
      "model": "music-2.6",
      "prompt": "一首关于夏日海边回忆的歌,独立民谣,温暖,吉他",
      "lyrics_optimizer": true,
      "audio_setting": {
        "format": "mp3",
        "sample_rate": 44100,
        "bitrate": 256000
      }
    },
    "responseType": "json"
  }'
```

### Error Handling

- `base_resp.status_code: 1002`: rate limit reached, retry later
- `base_resp.status_code: 1004`: API Key authentication failed
- `base_resp.status_code: 1008`: insufficient balance
- `base_resp.status_code: 1026`: content sensitive, modify the lyrics or prompt and retry
- `base_resp.status_code: 2013`: parameter error, check required fields
- `success: false` + `error: "未找到匹配的供应商"`: No enabled MiniMax provider with `music_gen` service found

### Notes

- The prompt length limit is 1-2000 characters; the lyrics length limit is 1-3500 characters
- Token Plan users: all plans use music-2.6 for free (100 tracks/day, each track ≤5 minutes)
- Unless the user specifies otherwise, default to `music-2.6` + `mp3` format + 44100 sample rate
- If the user only gives a theme without lyrics, use `lyrics_optimizer: true` to auto-generate lyrics
- If the user requests pure music/accompaniment, set `is_instrumental: true`
- Music generation takes a relatively long time (typically 30-90 seconds); please be patient
- The hex data volume is large (several MB); always use a temporary file as intermediary, do not store it in shell variables
