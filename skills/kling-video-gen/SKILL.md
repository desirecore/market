---
name: 可灵文生视频
description: >-
  Use this skill when the user wants to generate videos from text descriptions
  or images. Calls the Kling AI video generation API through the media proxy.
  Supports text-to-video and image-to-video modes. The API is asynchronous —
  submit a task, then poll for completion.
  Use when 用户提到 生成视频、文生视频、AI 视频、创建视频、视频生成、
  动画生成、可灵、Kling、把图片变成视频、图生视频。
license: Complete terms in LICENSE.txt
version: 1.1.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
provider: kling
tags:
  - media
  - video
  - generation
  - kling
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
  short_desc: 基于快手可灵 AI 的文本/图片生成视频技能
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# kling-video-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
3. **轮询间隔 10-15 秒** — 使用 `sleep 10` 等待

## 完整执行流程

### 前置条件

- 用户已在资源管理器-算力中配置可灵 Provider 并填写 API Key
- agent-service 正在运行

### 核心概念：异步任务模式

可灵 API 采用异步任务模式，分两步完成：

1. **提交任务**：POST 请求创建视频生成任务，返回 `task_id`
2. **轮询结果**：用 `task_id` 查询任务状态，直到 `task_status` 为 `succeed` 或 `failed`

### 模型选择

| 模型 | 适用场景 | 特点 |
|------|---------|------|
| kling-v2-5-turbo | 快速生成（推荐默认） | 高性价比，720p/1080p |
| kling-v2-5-turbo-pro | 高品质生成 | 1080p/4K |
| kling-v2 | 旗舰文生视频 | 高质量 |
| kling-v2-master | 最高品质 | 1080p/4K，耗时较长 |

### 第一步：提交视频生成任务（文生视频）

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "kling",
    "serviceType": "video_gen",
    "endpoint": "/videos/text2video",
    "body": {
      "model_name": "kling-v2-5-turbo",
      "prompt": "用户描述的视频内容",
      "negative_prompt": "",
      "cfg_scale": 0.5,
      "mode": "std",
      "duration": "5",
      "aspect_ratio": "16:9"
    },
    "responseType": "json"
  }'
```

从 JSON 响应中提取 `data.data.task_id`。

### 第一步（备选）：图生视频

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "kling",
    "serviceType": "video_gen",
    "endpoint": "/videos/image2video",
    "body": {
      "model_name": "kling-v2-5-turbo",
      "image": "图片URL或base64",
      "prompt": "可选的运动描述",
      "cfg_scale": 0.5,
      "mode": "std",
      "duration": "5"
    },
    "responseType": "json"
  }'
```

### 第二步：轮询任务状态

每隔 10-15 秒调用一次，直到 `task_status` 为 `succeed` 或 `failed`。将 `TASK_ID` 替换为第一步返回的 `task_id`。图生视频查询路径改为 `/videos/image2video/TASK_ID`。

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
TASK_ID="第一步返回的task_id"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"provider\": \"kling\",
    \"serviceType\": \"video_gen\",
    \"endpoint\": \"/videos/text2video/${TASK_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

轮询响应示例（进行中）：

```json
{
  "success": true,
  "data": {
    "code": 0,
    "data": {
      "task_id": "task_xxx",
      "task_status": "processing",
      "task_status_msg": "Generating video..."
    }
  }
}
```

完成响应示例：

```json
{
  "success": true,
  "data": {
    "code": 0,
    "data": {
      "task_id": "task_xxx",
      "task_status": "succeed",
      "task_result": {
        "videos": [
          {
            "id": "video_xxx",
            "url": "https://...",
            "duration": "5.0"
          }
        ]
      }
    }
  }
}
```

### 第三步：展示结果

任务完成后从 `data.data.task_result.videos[0].url` 获取视频 URL，直接展示给用户。

### 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| model_name | 模型名称 | kling-v2-5-turbo（默认）, kling-v2-5-turbo-pro, kling-v2, kling-v2-master |
| prompt | 视频描述 | 文本字符串 |
| negative_prompt | 不希望出现的内容 | 文本字符串（可选） |
| cfg_scale | 创意自由度 | 0-1，默认 0.5 |
| mode | 生成模式 | "std"（标准）, "pro"（高品质） |
| duration | 视频时长（秒） | "5" 或 "10" |
| aspect_ratio | 画面比例 | "16:9", "9:16", "1:1" |

### 错误处理

- `task_status: "failed"`：生成失败，向用户说明（可能是内容政策或参数错误）
- `success: false` + `error: "未找到匹配的供应商"`：用户未配置可灵 Provider
- `success: false` + `error: "未配置 API Key"`：用户未填写可灵 API Key
- 连续轮询超过 5 分钟未完成：告知用户任务可能超时，建议重试

### 注意事项

- 可灵视频生成是异步的，通常需要 1-5 分钟
- 轮询间隔建议 10-15 秒，不要太频繁
- 生成的视频 URL 有时效限制，建议及时保存
- 如果用户未明确要求，默认使用 `kling-v2-5-turbo` + `std` + `5秒` + `16:9`
