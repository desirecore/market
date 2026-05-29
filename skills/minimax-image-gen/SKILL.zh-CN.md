<!-- locale: zh-CN -->

# minimax-image-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须使用 `"response_format": "url"`** — 禁止 `"base64"`，base64 会导致输出截断
2. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
3. **必须通过 `/api/media/upload` 上传到 media-store** — 禁止保存到本地路径
4. **必须使用 `dc-media://` 协议展示图片** — 唯一能让前端正确渲染的方式
5. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python

## 完整执行流程（严格按此三步执行）

### 第一步：调用 API 生成图片

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "providerId": "provider-minimax-media-001",
    "endpoint": "/image_generation",
    "body": {
      "model": "image-01",
      "prompt": "这里替换为英文图片描述",
      "aspect_ratio": "1:1",
      "response_format": "url",
      "n": 1
    },
    "responseType": "json"
  }'
```

从 JSON 响应中提取 `data.data.image_urls[0]` 得到图片 URL。

### 第二步：下载并上传到 media-store

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
IMAGE_URL="第一步拿到的图片URL"
curl -sL "$IMAGE_URL" -o /tmp/minimax-gen.png && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/minimax-gen.png;type=image/png"
```

从 JSON 响应中提取 `mediaId` 字段（格式如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`）。

### 第三步：用 dc-media 协议展示图片

在你的回复文本中直接写 Markdown 图片语法：

```
![图片描述](dc-media://这里替换为mediaId)
```

例如：`![白色的猫坐在书桌上](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.png)`

前端会自动将 `dc-media://` 转为可访问的图片 URL 并渲染出来。

## 参数映射

| 用户意图 | aspect_ratio |
|---------|-------------|
| 正方形/头像 | "1:1" |
| 横版/风景/壁纸 | "16:9" |
| 竖版/手机/海报 | "9:16" |
| 标准照片 | "4:3" |
| 竖版照片 | "3:4" |

## 主体参考（角色一致性）

在 body 中添加 `subject_reference`：

```json
"subject_reference": [
  { "type": "character", "image_file": { "url": "参考图片URL" } }
]
```

## 错误处理

- `"error": "未找到匹配的供应商"`：未配置 MiniMax Media Provider
- `statusCode: 401`：API Key 无效
- `statusCode: 429`：频率限制，稍后重试
