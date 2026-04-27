---
name: MiniMax 语音合成
description: >-
  Use this skill when the user wants to convert text to speech using MiniMax's
  T2A (Text-to-Audio) API. Supports multiple voice styles, emotional control,
  and voice cloning. Use when 用户提到 语音合成、文字转语音、TTS、朗读、
  读出来、生成语音、生成音频、文本转音频、配音、念出来、MiniMax 语音。
license: Complete terms in LICENSE.txt
version: 1.2.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
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
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#007AFF" stroke-width="1.5" fill="#007AFF"
    fill-opacity="0.1"/><path d="M8 9v6M11 7v10M14 10v4M17 8v8"
    stroke="#007AFF" stroke-width="2"
    stroke-linecap="round"/></svg>
  short_desc: 基于 MiniMax Speech-02 的文本转语音技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
  listed: false
---

# minimax-tts 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python

## 完整执行流程

### 前置条件

- 用户已在资源管理器-算力中配置 MiniMax Media Provider 并填写 API Key
- agent-service 正在运行

### 语音选择指南

| voice_id | 特点 | 适用场景 |
|----------|------|---------|
| male-qn-qingse | 青涩男声 | 旁白、播客 |
| female-shaonv | 少女女声 | 有声书、对话 |
| female-yujie | 御姐女声 | 专业播报 |
| presenter_male | 主持人男声 | 新闻、正式场合 |
| presenter_female | 主持人女声 | 新闻、正式场合 |

### 生成语音

MiniMax TTS 返回 JSON（包含音频 URL 或 hex 数据），`responseType` 使用 `"json"`。

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

### 响应处理

MiniMax TTS 返回 JSON，根据请求参数可能返回 URL 或 hex 格式：

**URL 格式响应**（推荐，需在 audio_setting 中设置 `"format": "url"`）：
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

**Hex 格式响应**（默认）：
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

### 下载并上传到 media-store

音频 URL 有时效限制，必须立即下载并保存到本地 media-store。

**URL 格式**：
```bash
PORT=$(cat ~/.desirecore/agent-service.port)
AUDIO_URL="响应中的audio_url"
curl -sL "$AUDIO_URL" -o /tmp/minimax-tts.mp3 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-tts.mp3;type=audio/mpeg"
```

**Hex 格式**：
```bash
PORT=$(cat ~/.desirecore/agent-service.port)
HEX_DATA="响应中的hex数据"
echo -n "$HEX_DATA" | xxd -r -p > /tmp/minimax-tts.mp3 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-tts.mp3;type=audio/mpeg"
```

从 JSON 响应中提取 `mediaId` 字段。

### 展示结果

在回复中使用 dc-media 协议引用（前端会自动识别音频扩展名并渲染播放器）：

```
![语音合成结果](dc-media://这里替换为mediaId)
```
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| model | 模型 | "speech-02-hd"（高清）或 "speech-02-turbo"（快速） |
| text | 要转换的文本 | 最大 10000 字符 |
| voice_setting.voice_id | 语音角色 | "male-qn-qingse" |
| voice_setting.speed | 语速 | 1.0 |
| voice_setting.vol | 音量 | 1.0 |
| voice_setting.pitch | 音调 | 0 |
| audio_setting.format | 音频格式 | "mp3" |
| audio_setting.sample_rate | 采样率 | 32000 |

### 特殊语法

MiniMax TTS 支持在文本中插入停顿标记：
- `<#0.5#>` — 停顿 0.5 秒
- `<#2#>` — 停顿 2 秒
- 有效范围：0.01 ~ 99.99 秒

示例：`"你好<#1#>欢迎来到 DesireCore"`

### 错误处理

- `success: false` + `statusCode: 400`：文本为空或参数格式错误
- `success: false` + `statusCode: 401`：API Key 无效
- `success: false` + `statusCode: 429`：频率限制
- `success: false` + `error: "未找到匹配的供应商"`：未配置 MiniMax Media Provider

### 注意事项

- 文本超过 3000 字符时建议使用流式输出（但代理模式暂不支持流式）
- 返回的 audio_url 有 24 小时时效
- 如果用户未明确要求，默认使用 `speech-02-hd` + `male-qn-qingse` + 1.0 倍速
- 长文本建议分段调用，每段不超过 3000 字符
