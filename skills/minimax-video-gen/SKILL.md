---
name: minimax-video-gen
description: >-
  Use this skill when the user wants to generate videos using MiniMax's
  Hailuo model. Supports text-to-video, image-to-video, and subject reference.
  The API is asynchronous — submit a task, poll for status, then download.
  Use when 用户提到 生成视频、文生视频、AI 视频、创建视频、视频生成、
  动画生成、MiniMax 视频、海螺、Hailuo、图片变视频、图生视频。
license: Complete terms in LICENSE.txt
version: 1.2.2
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
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
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: MiniMax 文生视频
      short_desc: 基于 MiniMax Hailuo 的文本/图片生成视频技能
      description: >-
        Use this skill when the user wants to generate videos using MiniMax's Hailuo model. Supports text-to-video, image-to-video, and subject reference. The API is asynchronous — submit a task, poll for status, then download. Use when 用户提到 生成视频、文生视频、AI 视频、创建视频、视频生成、 动画生成、MiniMax 视频、海螺、Hailuo、图片变视频、图生视频。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:57314c8d07d63585
      translated_by: human
    en-US:
      name: MiniMax Video Generation
      short_desc: Text/image-to-video skill powered by MiniMax Hailuo
      description: >-
        Use this skill when the user wants to generate videos using MiniMax's Hailuo model. Supports text-to-video, image-to-video, and subject reference. The API is asynchronous — submit a task, poll for status, then download. Use when the user mentions generating videos, text-to-video, AI video, creating videos, video generation, animation generation, MiniMax video, Hailuo, image-to-video.
      body: ./SKILL.md
      source_hash: sha256:3b2855b9ff2d0ef1
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3"
    stroke="#AF52DE" stroke-width="1.5" fill="#AF52DE"
    fill-opacity="0.1"/><polygon points="10,7 18,12 10,17" fill="#AF52DE"
    fill-opacity="0.6" stroke="#AF52DE" stroke-width="1.2"
    stroke-linejoin="round"/></svg>
  category: media
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
  listed: false
---

# minimax-video-gen Skill

## Mandatory Rules (violation will cause failure)

1. **Must use HTTPS to access agent-service** — `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
3. **Polling interval is 10 seconds** — use `sleep 10` to wait

## Full Execution Flow

### Prerequisites

- The user has already configured and enabled a MiniMax Provider (regular API or Token Plan) in Resource Manager → Compute and entered the API Key
- agent-service is running

### Core Concept: Three-Step Asynchronous Flow

MiniMax video generation uses an asynchronous task model:

1. **Submit task**: POST to create a video generation task and receive a `task_id`
2. **Poll status**: query the task status with `task_id` until `status` is `"Success"` or `"Fail"`
3. **Download video**: use `file_id` to obtain the download URL

### Model Selection and Fallback Strategy

| Model | Supported Modes | Characteristics | Use Case |
|------|---------|------|---------|
| MiniMax-Hailuo-2.3 | Text-to-video + image-to-video | Highest quality, default first choice | Default when the user doesn't specify |
| MiniMax-Hailuo-2.3-fast | **Image-to-video only** | Fast, 50% lower cost | Fallback when quota is insufficient in image-to-video scenarios |

**Fallback rules (mandatory)**:
1. Use `MiniMax-Hailuo-2.3` by default
2. **When text-to-video (T2V) quota is insufficient**: `MiniMax-Hailuo-2.3-fast` does not support text-to-video and cannot be used as a fallback. Inform the user directly that the quota is insufficient and suggest waiting for the quota to reset or switching to another video generation service (such as Kling)
3. **When image-to-video (I2V) quota is insufficient**: fall back to `MiniMax-Hailuo-2.3-fast` and inform the user "switched to the fast model for generation"
4. If the user is doing image-to-video and explicitly requests fast generation, use `MiniMax-Hailuo-2.3-fast` directly

### Step 1: Submit a Text-to-Video Task

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "minimax",
    "serviceType": "video_gen",
    "endpoint": "/video_generation",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "Video content described by the user"
    },
    "responseType": "json"
  }'
```

Optional parameters (add to the body):
- `"duration"`: video length in seconds (6 or 10)
- `"resolution"`: `"768P"` or `"1080P"`

Extract `data.task_id` from the JSON response.

### Step 1 (alternative): Image-to-Video

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "minimax",
    "serviceType": "video_gen",
    "endpoint": "/video_generation",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "Describe the dynamic changes of the scene in the image",
      "first_frame_image": "https://image-URL"
    },
    "responseType": "json"
  }'
```

### Step 2: Poll the Task Status

Call once every 10 seconds until `status` is `"Success"` or `"Fail"`. Replace `TASK_ID` with the `task_id` returned in Step 1.

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
TASK_ID="task_id returned from step 1"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"provider\": \"minimax\",
    \"serviceType\": \"video_gen\",
    \"endpoint\": \"/query/video_generation?task_id=${TASK_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

Polling response (in progress):
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

Polling response (completed):
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

### Step 3: Get the Video Download URL

Replace `FILE_ID` with the `file_id` from the completed response in Step 2.

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
FILE_ID="file_id returned from step 2"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"provider\": \"minimax\",
    \"serviceType\": \"video_gen\",
    \"endpoint\": \"/files/retrieve?file_id=${FILE_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

Extract `data.file.download_url` from the response.

### Step 4: Download and Upload to media-store

The download URL is valid for 24 hours; you must download immediately and save it to the local media-store.

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
VIDEO_URL="download_url obtained in step 3"
curl -sL "$VIDEO_URL" -o /tmp/minimax-video.mp4 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-video.mp4;type=video/mp4"
```

Extract the `mediaId` field from the JSON response.

### Step 5: Display the Video Using the dc-media Protocol

Write Markdown image syntax directly in your reply (the frontend will automatically recognize the video extension and render a player):

```
![Video description](dc-media://replace-with-mediaId)
```

### Error Handling

- `status: "Fail"`: video generation failed; explain to the user
- `success: false` + `error: "No matching provider found"`: No enabled MiniMax provider with `video_gen` service found
- `success: false` + `error: "API Key not configured"`: API Key has not been entered
- **Insufficient quota** (errors related to `statusCode: 429`, `insufficient_quota`, `balance`): text-to-video cannot fall back (the Fast model does not support T2V); inform the user of insufficient quota; image-to-video can switch to `MiniMax-Hailuo-2.3-fast` and retry from Step 1
- Polling exceeds 10 minutes without completion: inform the user that the task may have timed out

### Notes

- MiniMax video generation is asynchronous and typically takes 2–10 minutes
- A polling interval of 10 seconds is recommended
- The download URL is valid for 24 hours
- If the user does not explicitly request otherwise, by default do not pass `duration` or `resolution` (use API defaults)
