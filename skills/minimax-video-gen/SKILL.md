---
name: minimax-video-gen
description: >-
  Use this skill when the user wants to generate videos using MiniMax's
  Hailuo model. Supports text-to-video, image-to-video, and subject reference.
  The API is asynchronous — submit a task, poll for status, then download.
  Use when 用户提到 生成视频、文生视频、AI 视频、创建视频、视频生成、
  动画生成、MiniMax 视频、海螺、Hailuo、图片变视频、图生视频。
license: Complete terms in LICENSE.txt
version: 1.3.1
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
  updated_at: '2026-06-09'
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
      source_hash: sha256:47463799495b3fdf
      translated_by: human
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
---

# minimax-video-gen Skill

## Mandatory Rules (violation will cause failure)

1. **Must use HTTPS to access agent-service** — `https://127.0.0.1:${PORT}` with `-k` to skip certificate verification
2. **Use Bash curl throughout** — do not use the HttpRequest tool or Python
3. **Polling interval is 10 seconds** — use `sleep 10` to wait
4. **Must use `providerId`** — do not use `provider`, or requests will route to the wrong upstream

## Full Execution Flow

### Prerequisites

- The user has already configured and enabled a Provider with `video_gen` service in Resource Manager → Compute and entered the API Key
- agent-service is running

### Core Concept: Four-Step Asynchronous Flow

Video generation uses an asynchronous task model via the NewAPI gateway:

1. **Submit task**: POST `/video/generations` to create a task, receive a `task_id`
2. **Poll status**: GET `/videos/{task_id}` until `status` is `"completed"`
3. **Download & upload**: download from `data.metadata.url`, upload to media-store
4. **Display**: use `dc-media://` protocol to show the video

### Provider Selection (Important)

Use `providerId` (not `provider`) to target the correct gateway. When the provider is a NewAPI gateway (e.g. `desirecore-cloud`), use `providerId`. Do **not** use `provider: "minimax"` — this would route to the MiniMax native host, which does **not** support the NewAPI `/video/generations` path.

```json
{
  "providerId": "desirecore-cloud",
  "serviceType": "video_gen",
  "endpoint": "/video/generations",
  ...
}
```

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

**Important**: The endpoint is `/video/generations` (with an "s"), NOT `/video_generation`.

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "desirecore-cloud",
    "serviceType": "video_gen",
    "endpoint": "/video/generations",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "Video content described by the user",
      "size": "768P",
      "duration": 6
    },
    "responseType": "json"
  }'
```

Optional parameters (add to the body):
- `"duration"`: video length in seconds (6 or 10)
- `"size"`: `"768P"` or `"1080P"` (use `size`, not `resolution`)

Extract `data.task_id` from the JSON response.

Successful response example:
```json
{
  "success": true,
  "data": {
    "id": "task_xxx",
    "task_id": "task_xxx",
    "object": "video",
    "model": "MiniMax-Hailuo-2.3",
    "status": "queued",
    "progress": 0,
    "created_at": 1780995870
  },
  "statusCode": 200
}
```

### Step 1 (alternative): Image-to-Video

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "desirecore-cloud",
    "serviceType": "video_gen",
    "endpoint": "/video/generations",
    "body": {
      "model": "MiniMax-Hailuo-2.3",
      "prompt": "Describe the dynamic changes of the scene in the image",
      "first_frame_image": "https://image-URL",
      "size": "768P"
    },
    "responseType": "json"
  }'
```

### Step 2: Poll the Task Status

Call once every 10 seconds until `status` is `"completed"` or `"failed"`. Replace `TASK_ID` with the `task_id` returned in Step 1.

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
TASK_ID="task_id returned from step 1"
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"providerId\": \"desirecore-cloud\",
    \"serviceType\": \"video_gen\",
    \"endpoint\": \"/videos/${TASK_ID}\",
    \"method\": \"GET\",
    \"responseType\": \"json\"
  }"
```

In-progress statuses may be: `"queued"` or `"in_progress"`.

Polling response (in progress):
```json
{
  "success": true,
  "data": {
    "id": "task_xxx",
    "status": "in_progress",
    "progress": 42
  }
}
```

Polling response (completed):
```json
{
  "success": true,
  "data": {
    "id": "task_xxx",
    "status": "completed",
    "progress": 100,
    "metadata": {
      "url": "https://.../output_aigc.mp4?..."
    }
  }
}
```

### Step 3: Download and Upload to media-store

Extract the video download URL from `data.metadata.url` in the completed Step 2 response. The URL is valid for 24 hours; download immediately.

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
VIDEO_URL="data.metadata.url from step 2"
curl -sL "$VIDEO_URL" -o /tmp/minimax-video.mp4 && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-video.mp4;type=video/mp4"
```

Extract the `mediaId` field from the JSON response.

### Step 4: Display the Video Using the dc-media Protocol

Write Markdown image syntax directly in your reply (the frontend will automatically recognize the video extension and render a player):

```
![Video description](dc-media://replace-with-mediaId)
```

### Error Handling

- `status: "failed"`: video generation failed; explain to the user
- `success: false` + `error: "No matching provider found"`: No enabled provider with `video_gen` service found
- `success: false` + `error: "API Key not configured"`: API Key has not been entered
- **Insufficient quota** (errors related to `statusCode: 429`, `insufficient_quota`, `balance`): text-to-video cannot fall back (the Fast model does not support T2V); inform the user of insufficient quota; image-to-video can switch to `MiniMax-Hailuo-2.3-fast` and retry from Step 1
- Polling exceeds 10 minutes without completion: inform the user that the task may have timed out

### Notes

- Video generation is asynchronous and typically takes 2–10 minutes
- A polling interval of 10 seconds is recommended
- The download URL is valid for 24 hours
- If the user does not explicitly request otherwise, by default pass `"size": "768P"` and `"duration": 6`
- Do **not** proxy the download URL through media-proxy — use `curl -sL "$VIDEO_URL"` to download directly
