<!-- locale: zh-CN -->

# dashscope-image-gen 技能

## 强制规则（违反将导致功能失败）

1. **严格按下方步骤执行** — 禁止自行探索其他端点、尝试本文档未列出的模型、或读取配置文件
2. **必须用 HTTPS 访问 agent-service** — API 地址已在系统提示词的"本机 API"部分提供（如 `https://127.0.0.1:PORT`），直接使用，加 `-k` 跳过证书验证
3. **必须通过 `/api/media/upload` 上传到 media-store** — 禁止保存到本地路径
4. **必须使用 `dc-media://` 协议展示图片** — 唯一能让前端正确渲染的方式
5. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python
6. **使用 `/images/generations` 端点** — 同步调用，响应包含 b64_json 图片数据
7. **只能使用下方模型列表中的模型** — 禁止尝试 dall-e-3、qwen-vl 或任何未列出的模型

## 供应商与默认算力

**无需指定供应商**，只需传 `"serviceType": "image_gen"`，系统会自动路由到正确的供应商。

**禁止**尝试查询供应商列表、读取 compute.json、或通过 API 探索可用模型。下方列出的模型保证可用。

## 模型选择指南

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| gpt-image-2 | 高画质，速度快，风格多样 | **默认首选** — 用户未指定模型时使用 |
| wan2.7-image | 标准高画质（需配置阿里云 DashScope） | 仅当用户明确要求万相 / DashScope 时 |
| wan2.7-image-pro | 旗舰，4K 分辨率（需配置阿里云 DashScope） | 仅当用户明确要求最高画质万相模型时 |

**默认规则**：用户未指定模型时，使用 `gpt-image-2`。

**注意**：`wan2.7-image` 和 `wan2.7-image-pro` 仅在用户自行配置了阿里云 DashScope 供应商时可用。如果使用这些模型出错，自动降级到 `gpt-image-2`。

## 完整执行流程（严格按此步骤执行）

### 获取 API 地址

系统提示词中"本机 API"部分已包含 agent-service 的地址（如 `Agent Service: https://127.0.0.1:61000`）。直接从中提取 URL 使用。

如果无法从系统提示词中找到，使用以下兜底方式：

```bash
PORT=$(cat "${DESIRECORE_HOME:-$HOME/.desirecore}/agent-service.port")
# 然后使用 https://127.0.0.1:${PORT}
```

### 第一步：生成图片（单次 curl 调用）

通过 media-proxy 调用 `/images/generations` 端点。**必须严格使用以下请求结构** — 禁止添加 `messages`、`response_format` 或任何未在此处列出的参数：

```bash
# 将响应保存到临时文件，避免 base64 数据灌入终端
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceType": "image_gen",
    "endpoint": "/images/generations",
    "body": {
      "model": "gpt-image-2",
      "prompt": "这里替换为图片描述（建议英文效果更好）",
      "size": "1024x1024",
      "n": 1
    },
    "responseType": "json"
  }' -o /tmp/dashscope-response.json

# 检查成功并直接将 b64_json 提取为图片文件（禁止将响应内容输出到终端）
python3 -c "
import json, base64, sys
with open('/tmp/dashscope-response.json') as f:
    resp = json.load(f)
if not resp.get('success'):
    print('ERROR:', json.dumps(resp, ensure_ascii=False)[:500])
    sys.exit(1)
b64 = resp['data']['data'][0]['b64_json']
with open('/tmp/dashscope-gen.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('OK: saved to /tmp/dashscope-gen.png')
"
```

**关键警告**：响应包含大约 2MB 的 base64 图片数据。**禁止**将原始响应或 b64_json 打印到终端。始终使用 `-o` 保存到文件，再用上面的 python3 脚本提取。

**响应格式**（保存在 `/tmp/dashscope-response.json` 中）：
```json
{
  "success": true,
  "data": {
    "created": 1781060911,
    "data": [{"b64_json": "<非常大的 base64 字符串>"}],
    "size": "1024x1024"
  }
}
```

### 第二步：上传到 media-store

```bash
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/dashscope-gen.png;type=image/png"
```

从上传 JSON 响应中提取 `mediaId` 字段（格式如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`）。

### 第三步：用 dc-media 协议展示图片

在你的回复文本中直接写 Markdown 图片语法：

```
![图片描述](dc-media://这里替换为mediaId)
```

例如：`![森林中的白色狐狸](dc-media://a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6.png)`

前端会自动将 `dc-media://` 转为可访问的图片 URL 并渲染出来。

## 参数映射

### 尺寸选择

`size` 放在 `body` 对象中：

```json
{
  "model": "gpt-image-2",
  "prompt": "图片描述",
  "size": "1024x1024",
  "n": 1
}
```

| 用户意图 | size 参数 |
|---------|-----------|
| 正方形/头像/默认 | "1024x1024" |
| 横版/风景/壁纸 | "1536x1024" |
| 竖版/手机/海报 | "1024x1536" |

### 可选参数（加入请求体顶层）

| 参数 | 说明 |
|------|------|
| `n` | 生成数量 1-4，默认 1 |
| `size` | 图片尺寸，如 "1024x1024" |

## 多图生成

当 `n > 1` 时，为每张图片执行下载+上传，然后逐一展示：

```
![图片1描述](dc-media://mediaId1)
![图片2描述](dc-media://mediaId2)
```

## 错误处理

| 错误 | 含义 | 处理方式 |
|------|------|---------|
| `"未找到匹配的供应商"` | 没有启用的供应商支持 `image_gen` | 告知用户在设置中启用支持 image_gen 的供应商 |
| `"未配置 API Key"` | 未填写 API Key | 告知用户配置 API Key |
| `statusCode: 401` | API Key 无效或过期 | 告知用户检查 API Key |
| `statusCode: 429` | 频率限制 | 等待后重试一次 |
| `statusCode: 400` + `model_price_error` | 模型在当前供应商不可用 | 切换到 `gpt-image-2` 重试 |
| `statusCode: 400` | 其他参数错误 | 检查模型名和尺寸是否在上表中 |

**模型出错时**：如果 `wan2.7-image` 或 `wan2.7-image-pro` 报 `model_price_error`，自动切换到 `gpt-image-2` 重试。无需询问用户。

**其他错误时**：直接向用户清晰报告错误。禁止尝试其他端点或读取配置文件。

## 注意事项

- 图片生成调用是同步的，通常 10-60 秒返回
- 提示词建议用英文以获得最佳效果，中文也支持
- 如果用户未明确要求模型/尺寸，默认使用 `gpt-image-2` + `1024x1024`
