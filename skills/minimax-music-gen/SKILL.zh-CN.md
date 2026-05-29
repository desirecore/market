<!-- locale: zh-CN -->

# minimax-music-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
3. **禁止使用 `output_format: "url"`** — URL 下载在 Token Plan 等场景下会因 CDN 鉴权失败返回空文件。必须使用默认的 hex 格式，音频数据直接在 API 响应中返回

## 完整执行流程

### 前置条件

- 用户已在资源管理器-算力中配置 MiniMax Provider（常规 API 或 Token Plan）并填写 API Key
- agent-service 正在运行

### 核心概念

MiniMax Music Generation 是**同步 API**（非异步任务模式），调用后直接返回音频数据。支持三种模式：

| 模式 | model | 说明 |
|------|-------|------|
| 歌曲生成 | `music-2.6` | 提供 prompt + lyrics，生成带人声的歌曲 |
| 纯器乐 | `music-2.6` | 设置 `is_instrumental: true`，仅需 prompt |
| 翻唱/Cover | `music-cover` | 提供参考音频 + prompt，基于旋律骨架重新编曲 |

### 歌词结构标签

lyrics 字段支持以下结构标签来组织歌曲段落：

| 标签 | 含义 |
|------|------|
| `[verse]` | 主歌 |
| `[chorus]` | 副歌 |
| `[bridge]` | 桥段 |
| `[intro]` | 前奏 |
| `[outro]` | 尾声 |
| `[interlude]` | 间奏 |

示例歌词格式：
```
[verse]
夜晚的城市灯火阑珊
我独自走在回家的路上

[chorus]
这一刻时间仿佛停止
所有的喧嚣都已远去
```

### 生成歌曲（带人声）

**注意：不要传 `output_format` 参数，使用默认的 hex 格式。**

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

### 生成纯器乐

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

### 响应处理与保存

API 返回 JSON，音频数据以 hex 编码存放在 `data.data.audio.data` 字段中。

**响应结构**：
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

**注意**：`status` 字段含义为 1=合成中（流式场景）、2=合成完成。非流式模式下返回时 status 为 2。

### 将 hex 音频数据保存到 media-store

从响应 JSON 中提取 `data.data.audio.data` 字段的 hex 字符串，转为二进制后上传：

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
# 将 API 响应保存到临时文件（避免 hex 数据过大撑爆 shell 变量）
# 假设上一步的 curl 输出已保存到 /tmp/minimax-music-resp.json

# 提取 hex 数据并转为二进制（纯 Bash，不依赖 Python）
jq -r '.data.data.audio.data' /tmp/minimax-music-resp.json | xxd -r -p > /tmp/minimax-music.mp3

# 验证文件有效（大于 1KB 且为音频格式）
FILE_SIZE=$(stat -f%z /tmp/minimax-music.mp3 2>/dev/null || stat -c%s /tmp/minimax-music.mp3 2>/dev/null)
if [ "$FILE_SIZE" -lt 1024 ]; then
  echo "ERROR: 音频文件异常（${FILE_SIZE} 字节），可能生成失败"
  exit 1
fi

# 上传到 media-store
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-music.mp3;type=audio/mpeg"
```

从上传响应 JSON 中提取 `mediaId` 字段。

### 展示结果

在回复中使用 dc-media 协议引用（前端会自动识别音频扩展名并渲染播放器）：

```
![音乐生成结果](dc-media://这里替换为mediaId)
```

### 参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| model | 模型名称 | 是 | "music-2.6" |
| prompt | 音乐风格/情绪描述 | 有歌词时可选，纯器乐/cover 必填 | — |
| lyrics | 歌词（支持结构标签） | 非纯器乐模式必填 | — |
| is_instrumental | 是否生成纯器乐 | 否 | false |
| lyrics_optimizer | 根据 prompt 自动生成歌词 | 否 | false |
| audio_setting.format | 音频格式：mp3/wav/pcm | 否 | "mp3" |
| audio_setting.sample_rate | 采样率：16000/24000/32000/44100 | 否 | 32000 |
| audio_setting.bitrate | 比特率：32000/64000/128000/256000 | 否 | 128000 |

### prompt 写法建议

prompt 用于描述音乐的风格、情绪和乐器编排，建议用逗号分隔关键词：

- 风格：`独立民谣`、`电子舞曲`、`古典钢琴`、`摇滚`、`R&B`、`爵士`、`嘻哈`
- 情绪：`温暖`、`忧郁`、`欢快`、`史诗感`、`空灵`、`治愈`
- 乐器：`吉他伴奏`、`钢琴独奏`、`弦乐铺底`、`合成器`、`鼓点强劲`
- 结构：`渐进式编曲`、`开场留白渐入高潮`、`轻柔开头爆发副歌`

示例：`"独立民谣,温暖治愈,木吉他为主,轻柔的鼓点,渐进式编曲"`

### 自动生成歌词模式

如果用户只描述了想要的音乐风格但没有提供歌词，可以设置 `lyrics_optimizer: true`，模型会根据 prompt 自动生成歌词：

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

### 错误处理

- `base_resp.status_code: 1002`：频率限制，稍后重试
- `base_resp.status_code: 1004`：API Key 认证失败
- `base_resp.status_code: 1008`：余额不足
- `base_resp.status_code: 1026`：内容敏感，修改歌词或 prompt 后重试
- `base_resp.status_code: 2013`：参数错误，检查必填字段
- `success: false` + `error: "未找到匹配的供应商"`：未找到已启用且支持 `music_gen` 服务的 MiniMax Provider

### 注意事项

- prompt 长度限制 1-2000 字符，lyrics 长度限制 1-3500 字符
- Token Plan 用户：所有套餐免费使用 music-2.6（100 首/天，每首 ≤5 分钟）
- 如果用户未明确要求，默认使用 `music-2.6` + `mp3` 格式 + 44100 采样率
- 如果用户只给了主题没给歌词，使用 `lyrics_optimizer: true` 自动生成歌词
- 如果用户要求纯音乐/伴奏，设置 `is_instrumental: true`
- 音乐生成耗时较长（通常 30-90 秒），请耐心等待
- hex 数据量较大（几 MB），务必用临时文件中转，不要用 shell 变量存储
