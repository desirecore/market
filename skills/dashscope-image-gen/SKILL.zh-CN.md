<!-- locale: zh-CN -->

# dashscope-image-gen 技能

## 强制规则（违反将导致功能失败）

1. **必须用 HTTPS 访问 agent-service** — `https://127.0.0.1:${PORT}` 加 `-k` 跳过证书验证
2. **必须通过 `/api/media/upload` 上传到 media-store** — 禁止保存到本地路径
3. **必须使用 `dc-media://` 协议展示图片** — 唯一能让前端正确渲染的方式
4. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
5. **使用 compatible-mode（/chat/completions）** — 同步调用，响应直接包含图片 URL

## 模型选择指南

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| wan2.7-image-pro | 旗舰，4K 分辨率，thinking_mode | 用户要求最高画质、4K、细节丰富 |
| wan2.7-image | 标准高画质，thinking_mode | **默认首选**，无特殊要求时使用 |

**默认规则**：用户未指定模型时，使用 `wan2.7-image`。

## 完整执行流程（严格按此两步执行）

### 前置条件

- 用户已在资源管理器-算力中配置阿里云 DashScope Provider 并填写 API Key
- agent-service 正在运行

### 第一步：调用文生图 API（同步）

通过 media-proxy 的 compatible-mode 端点生成图片，响应直接包含图片 URL：

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "dashscope",
    "serviceType": "image_gen",
    "endpoint": "/chat/completions",
    "body": {
      "model": "wan2.7-image",
      "messages": [
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "这里替换为图片描述（建议英文效果更好）"}
          ]
        }
      ]
    },
    "responseType": "json"
  }'
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "request_id": "...",
    "output": {
      "choices": [
        {
          "message": {
            "role": "assistant",
            "content": [
              {
                "type": "image",
                "image": "https://dashscope-result.oss.aliyuncs.com/..."
              }
            ]
          },
          "finish_reason": "stop"
        }
      ]
    }
  },
  "statusCode": 200
}
```

从 `data.output.choices[0].message.content` 中找到 `type: "image"` 的项，提取其 `image` URL。

### 第二步：下载并上传到 media-store

图片 URL 有时效，必须立即下载并保存到本地 media-store：

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
IMAGE_URL="第一步响应中的 image URL"
curl -sL "$IMAGE_URL" -o /tmp/dashscope-gen.png && \
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/dashscope-gen.png;type=image/png"
```

从 JSON 响应中提取 `mediaId` 字段（格式如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`）。

### 第三步：用 dc-media 协议展示图片

在你的回复文本中直接写 Markdown 图片语法：

```
![图片描述](dc-media://这里替换为mediaId)
```

例如：`![森林中的白色狐狸](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.png)`

前端会自动将 `dc-media://` 转为可访问的图片 URL 并渲染出来。

## 参数映射

### 尺寸选择

通义万相通过 compatible-mode 调用时，尺寸通过 `size` 参数传入（放在请求体顶层）：

```json
{
  "model": "wan2.7-image",
  "size": "1024x1024",
  "messages": [...]
}
```

| 用户意图 | size 参数 |
|---------|-----------|
| 正方形/头像/默认 | "1024x1024" |
| 横版/风景/壁纸 | "1792x1024" |
| 竖版/手机/海报 | "1024x1792" |

### 可选参数（加入请求体顶层）

| 参数 | 说明 |
|------|------|
| `n` | 生成数量 1-4，默认 1 |
| `size` | 图片尺寸，如 "1024x1024" |

## 多图生成

当 `n > 1` 时，`choices` 数组会有多个元素，每个 `message.content` 中都有一张图片。需要为每张图片执行下载+上传，然后逐一展示：

```
![图片1描述](dc-media://mediaId1)
![图片2描述](dc-media://mediaId2)
```

## 错误处理

- `success: false` + `error: "未找到匹配的供应商"`：未配置 DashScope Provider 或未启用
- `success: false` + `error: "未配置 API Key"`：未填写 API Key
- `statusCode: 401`：API Key 无效或已过期
- `statusCode: 429`：频率限制，稍后重试
- `statusCode: 400` + `InvalidParameter`：参数错误（如尺寸不支持）
- `statusCode: 403` + `AccessDenied.Unpurchased`：模型未开通，需要在阿里云控制台开通

## 注意事项

- 通过 compatible-mode 调用是同步的，通常 10-60 秒返回（wan2.7-image-pro 可能更长）
- 结果图片 URL 有时效，必须及时下载
- 提示词建议用英文以获得最佳效果，中文也支持
- 如果用户未明确要求模型/尺寸，默认使用 `wan2.7-image` + `1024x1024`
