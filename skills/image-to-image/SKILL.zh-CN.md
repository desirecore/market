<!-- locale: zh-CN -->

# image-to-image 技能

## 强制规则（违反将导致功能失败）

1. **严格按下方步骤执行** — 禁止自行探索其他端点、尝试本文档未列出的模型、或读取配置文件
2. **必须用 HTTPS 访问 agent-service** — API 地址已在系统提示词的"本机 API"部分提供（如 `https://127.0.0.1:PORT`），直接使用，加 `-k` 跳过证书验证
3. **必须通过 `/api/media/upload` 上传到 media-store** — 禁止保存到本地路径
4. **必须使用 `dc-media://` 协议展示图片** — 唯一能让前端正确渲染的方式
5. **全程使用 Bash curl** — 不要使用 HttpRequest 工具或 Python（b64 提取脚本除外）
6. **使用 `/images/generations` 端点并附带 `image` 字段** — 与文生图相同的端点，`image` 字段触发图生图模式
7. **只使用 `gpt-image-2` 模型** — 禁止尝试 dall-e-3、wan2.7-image 或任何其他模型进行图生图

## 供应商与默认算力

本技能通过 DesireCore Cloud 供应商使用 `gpt-image-2` 模型。**无需指定供应商**，只需传 `"serviceType": "image_gen"`，系统会自动路由到正确的供应商。

- **DesireCore Cloud**（默认，始终可用）：内置算力供应商已支持 `gpt-image-2` 图生图。用户无需任何配置即可直接使用。

**禁止**尝试查询供应商列表、读取 compute.json、或通过 API 探索可用模型。上方列出的模型保证可用。

## 何时使用此技能

当用户出现以下情况时触发此技能：
- 发送了一张图片并要求修改/编辑/变换
- 要求更换图片的风格、背景或内容
- 想基于参考图片生成新图片
- 使用了关键词：图生图、修改图片、编辑图片、基于这张图、img2img

**不要在以下情况使用此技能**：用户仅要求"生成图片"或"画一张"而没有提供参考图 — 此时应使用 `dashscope-image-gen` 技能。

## 如何识别用户的输入图片

用户的输入图片可能来自以下来源：

1. **当前对话中的图片**：用户在聊天中上传了图片，它在对话中以 `dc-media://<mediaId>` 或图片附件形式出现。提取 `mediaId`（格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`）。

2. **之前生成的图片**：用户引用了之前生成的图片（如"修改上面那张图"、"把那张小猪图改一下"）。回溯对话找到最近的 `dc-media://<mediaId>` 引用。

3. **图片 URL**：用户提供了外部 URL。先用 `curl -sL "<url>" -o /tmp/input-image.png` 下载。

## 完整执行流程（严格按此步骤执行）

### 获取 API 地址

系统提示词中"本机 API"部分已包含 agent-service 的地址（如 `Agent Service: https://127.0.0.1:61000`）。直接从中提取 URL 使用。

如果无法从系统提示词中找到，使用以下兜底方式：

```bash
PORT=$(cat "${DESIRECORE_HOME:-$HOME/.desirecore}/agent-service.port")
# 然后使用 https://127.0.0.1:${PORT}
```

### 第一步：下载输入图片并转为 base64

从 media-store 下载用户图片并转为 base64 data URL：

```bash
# 从 media-store 下载（将 <mediaId> 替换为实际的 media ID）
curl -sk "https://127.0.0.1:${PORT}/api/media/<mediaId>" -o /tmp/input-image.png

# 转为 base64 data URL（禁止将 base64 打印到终端）
python3 -c "
import base64, sys
with open('/tmp/input-image.png', 'rb') as f:
    data = f.read()
b64 = base64.b64encode(data).decode()
# 通过魔数检测 MIME 类型
mime = 'image/png'
if data[:2] == b'\xff\xd8':
    mime = 'image/jpeg'
elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
    mime = 'image/webp'
data_url = f'data:{mime};base64,{b64}'
with open('/tmp/input-image-dataurl.txt', 'w') as f:
    f.write(data_url)
print(f'OK: data URL saved, image size: {len(data)} bytes, mime: {mime}')
"
```

**关键警告**：base64 data URL 可能非常大（1-5MB）。**禁止**将其打印到终端。始终保存到文件。

### 第二步：生成编辑后的图片（单次 curl 调用）

通过 media-proxy 调用 `/images/generations` 并附带 `image` 字段。**必须严格使用以下请求结构**：

```bash
# 从文件读取 data URL 并构建请求
IMAGE_DATA_URL=$(cat /tmp/input-image-dataurl.txt)

# 将响应保存到临时文件，避免 base64 数据灌入终端
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media-proxy" \
  -H "Content-Type: application/json" \
  -d "{
    \"serviceType\": \"image_gen\",
    \"endpoint\": \"/images/generations\",
    \"body\": {
      \"model\": \"gpt-image-2\",
      \"prompt\": \"这里替换为编辑描述（建议英文效果更好）\",
      \"image\": \"${IMAGE_DATA_URL}\",
      \"size\": \"1024x1024\",
      \"n\": 1
    },
    \"responseType\": \"json\"
  }" -o /tmp/img2img-response.json

# 检查成功并将 b64_json 提取为图片文件（禁止将响应内容输出到终端）
python3 -c "
import json, base64, sys
with open('/tmp/img2img-response.json') as f:
    resp = json.load(f)
if not resp.get('success'):
    print('ERROR:', json.dumps(resp, ensure_ascii=False)[:500])
    sys.exit(1)
b64 = resp['data']['data'][0]['b64_json']
with open('/tmp/img2img-output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('OK: saved to /tmp/img2img-output.png')
"
```

**关键警告**：响应包含大约 2MB 的 base64 图片数据。**禁止**将原始响应或 b64_json 打印到终端。始终使用 `-o` 保存到文件，再用上面的 python3 脚本提取。

**重要**：尽量将第一步和第二步合并到单次 Bash 工具调用中，减少往返次数。完整脚本应：下载图片 → 转 base64 → 构建 curl 请求 → 提取结果。

**响应格式**（保存在 `/tmp/img2img-response.json` 中）：
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

### 第三步：上传到 media-store

```bash
curl -sk -X POST "https://127.0.0.1:${PORT}/api/media/upload" \
  -F "file=@/tmp/img2img-output.png;type=image/png"
```

从上传 JSON 响应中提取 `mediaId` 字段（格式如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.png`）。

### 第四步：用 dc-media 协议展示图片

在你的回复文本中直接写 Markdown 图片语法：

```
![图片描述](dc-media://这里替换为mediaId)
```

前端会自动将 `dc-media://` 转为可访问的图片 URL 并渲染出来。

## 参数映射

### 尺寸选择

`size` 放在 `body` 对象中：

| 用户意图 | size 参数 |
|---------|-----------|
| 正方形/默认 | "1024x1024" |
| 横版/宽屏 | "1536x1024" |
| 竖版/高图 | "1024x1536" |
| 自动（让模型决定） | "auto" |

### 图生图的提示词建议

- **明确说明要改什么**："将背景换成海滩" 比 "编辑这张图" 更好
- **描述期望的结果**："一只穿着宇航服的小猪在太空中" 而不是 "改成太空主题"
- **英文提示词通常效果更好**，中文也支持
- **说明要保留什么**："保持主体不变，只更换背景" 有助于保持原图特征

## 错误处理

| 错误 | 含义 | 处理方式 |
|------|------|---------|
| `"未找到匹配的供应商"` | 没有启用的供应商支持 `image_gen` | 告知用户在设置中启用支持 image_gen 的供应商 |
| `"未配置 API Key"` | 未填写 API Key | 告知用户配置 API Key |
| `statusCode: 401` | API Key 无效或过期 | 告知用户检查 API Key |
| `statusCode: 429` | 频率限制 | 等待后重试一次 |
| `statusCode: 400` | 参数错误 | 检查模型名和尺寸；确保图片是有效的 base64 |
| 图片下载失败 | mediaId 不存在或已过期 | 请用户重新上传图片 |

**遇到任何错误时**：禁止尝试其他模型、其他端点、或读取配置文件。直接向用户清晰报告错误即可。

## 注意事项

- 图生图调用是同步的，通常 15-60 秒返回
- 输入图片以 base64 形式放在请求体中，会显著增加请求大小
- `gpt-image-2` 模型支持多种编辑类型：风格迁移、背景替换、对象修改、艺术变换
- 如果用户未明确要求尺寸，默认使用 `1024x1024`
- 如果用户的输入图片很大，可以提示处理时间可能较长
