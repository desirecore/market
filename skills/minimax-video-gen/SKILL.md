---
name: MiniMax 文生视频
description: >-
  Use this skill when the user wants to generate videos using MiniMax's
  Hailuo model. Supports text-to-video, image-to-video, and subject reference.
  The API is asynchronous — submit a task, poll for status, then download.
  Use when 用户提到 生成视频、文生视频、AI 视频、创建视频、视频生成、
  动画生成、MiniMax 视频、海螺、Hailuo、图片变视频、图生视频。
license: Complete terms in LICENSE.txt
version: 1.2.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: minimax
tags:
  - media
  - video
  - generation
  - minimax
  - hailuo
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
    stroke="#AF52DE" stroke-width="1.5" fill="#AF52DE"
    fill-opacity="0.1"/><polygon points="10,7 18,12 10,17" fill="#AF52DE"
    fill-opacity="0.6" stroke="#AF52DE" stroke-width="1.2"
    stroke-linejoin="round"/></svg>
  short_desc: 基于 MiniMax Hailuo 的文本/图片生成视频技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
  listed: false
---

# minimax-video-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
3. **轮询间隔 10 秒** — 使用 `sleep 10` 等待

## 完整执行流程

### 前置条件

- 用户已在资源管理器-算力中配置 MiniMax Media Provider 并填写 API Key
- agent-service 正在运行

### 核心概念：三步异步流程

MiniMax 视频生成采用异步任务模式：

1. **提交任务**：POST 创建视频生成任务，返回 `task_id`
2. **轮询状态**：用 `task_id` 查询任务状态，直到 `status` 为 `"Success"` 或 `"Fail"`
3. **下载视频**：用 `file_id` 获取下载 URL

### 模型选择与降级策略

| 模型 | 支持模式 | 特点 | 适用场景 |
|------|---------|------|---------|
| MiniMax-Hailuo-2.3 | 文生视频 + 图生视频 | 最高画质，默认首选 | 用户未指定时的默认选择 |
| MiniMax-Hailuo-2.3-fast | **仅图生视频** | 速度快，成本低 50% | 图生视频场景下额度不足时降级 |

**降级规则（强制）**：
1. 默认使用 `MiniMax-Hailuo-2.3`
2. **文生视频（T2V）额度不足时**：`MiniMax-Hailuo-2.3-fast` 不支持文生视频，无法降级。应直接告知用户额度不足，建议等待额度重置或切换到其他视频生成服务（如可灵）
3. **图生视频（I2V）额度不足时**：可降级到 `MiniMax-Hailuo-2.3-fast`，告知用户"已切换到快速模型生成"
4. 如果用户做图生视频且明确要求快速生成，直接使用 `MiniMax-Hailuo-2.3-fast`

### 第一步：提交文生视频任务

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "provider-minimax-media-001",
    "endpoint": "/video_generation",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "用户描述的视频内容"
    },
    "responseType": "json"
  }'
```

可选参数（加入 body 中）：
- `"duration"`: 视频时长秒数（6 或 10）
- `"resolution"`: `"768P"` 或 `"1080P"`

从 JSON 响应中提取 `data.task_id`。

### 第一步（备选）：图生视频

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "provider-minimax-media-001",
    "endpoint": "/video_generation",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "描述图片中场景的动态变化",
      "first_frame_image": "https://图片URL"
    },
    "responseType": "json"
  }'
```

### 第二步：轮询任务状态

每隔 10 秒调用一次，直到 `status` 为 `"Success"` 或 `"Fail"`。将 `TASK_ID` 替换为第一步返回的 `task_id`。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
TASK_ID="第一步返回的task_id"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"providerId\": \"provider-minimax-media-001\",
    \"endpoint\": \"/query/video_generation?task_id=${TASK_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

轮询响应（进行中）：
```json
{
  "success": true,
  "data": {
    "task_id": "task_xxx",
    "status": "Processing",
    "file_id": ""
  }
}
```

轮询响应（完成）：
```json
{
  "success": true,
  "data": {
    "task_id": "task_xxx",
    "status": "Success",
    "file_id": "file_xxx"
  }
}
```

### 第三步：获取视频下载链接

将 `FILE_ID` 替换为第二步完成响应中的 `file_id`。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
FILE_ID="第二步返回的file_id"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"providerId\": \"provider-minimax-media-001\",
    \"endpoint\": \"/files/retrieve?file_id=${FILE_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

从响应中提取 `data.file.download_url`。

### 第四步：下载并上传到 media-store

下载 URL 有 24 小时时效，必须立即下载并保存到本地 media-store。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
VIDEO_URL="第三步获取的download_url"
curl -sL "$VIDEO_URL" -o /tmp/minimax-video.mp4 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-video.mp4;type=video/mp4"
```

从 JSON 响应中提取 `mediaId` 字段。

### 第五步：用 dc-media 协议展示视频

在你的回复文本中直接写 Markdown 图片语法（前端会自动识别视频扩展名并渲染播放器）：

```
![视频描述](dc-media://这里替换为mediaId)
```

### 错误处理

- `status: "Fail"`：视频生成失败，向用户说明
- `success: false` + `error: "未找到匹配的供应商"`：未配置 MiniMax Media Provider
- `success: false` + `error: "未配置 API Key"`：未填写 API Key
- **额度不足**（`statusCode: 429`、`insufficient_quota`、`balance` 相关错误）：文生视频无法降级（Fast 模型不支持 T2V），告知用户额度不足；图生视频可换用 `MiniMax-Hailuo-2.3-fast` 从第一步重试
- 轮询超过 10 分钟未完成：告知用户任务可能超时

### 注意事项

- MiniMax 视频生成是异步的，通常需要 2-10 分钟
- 轮询间隔建议 10 秒
- 下载 URL 有 24 小时时效
- 如果用户未明确要求，默认不传 duration 和 resolution（使用 API 默认值）
