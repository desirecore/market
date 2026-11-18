<!-- locale: zh-CN -->

# dashscope-image-gen 技能

## 范围与前提

使用已配置的图片生成服务生成并交付图片。本技能不提供托管模型、凭据、额度或订阅。用户需要启用 `image_gen` 供应商，并拥有所选模型的访问权限；供应商条款及单独的使用费用仍适用。目录中存在模型不代表上游通道当前可用。

## 模型与供应商选择

1. 尊重用户明确指定的模型与供应商。根据当前运行时目录和对应 API 契约核实，不凭模型家族或本技能名称猜测。
2. 用户未指定模型时，使用已保存的 `defaultServiceMap.image_gen` 绑定，包括其供应商。不要用示例中的型号覆盖默认值。如果没有可用默认，检查当前启用的图片生成能力，在用户要求内选择；选择会改变用户指定服务或费用约束时先澄清。
3. 通过可用的算力查询工具，或当前 agent-service 的 `GET /api/compute/config` 解析绑定。配置 API 对密钥做掩码；只提取请求所需的默认绑定、供应商 ID/启用状态和图片模型元数据，不索取或输出凭据。模型 `serviceType` 可以是 `image_gen`，也可以是包含它的数组。原始 API 请求的上游模型 ID 依次取 `userOverrides.apiModelId`、`apiModelId`、`modelName`。
4. 可用性以实际选中供应商和响应为准。本技能没有静态模型白名单或保证可用的默认型号。例如万相模型既可能由官方网关提供，也可能来自用户自己的 DashScope 连接；不能仅凭名称决定路由。

## 选择执行方式

选择适合本次请求的当前工具/API 契约。`GenerateImage` 可用且满足需求时，一次调用即可完成供应商适配、生成、媒体持久化与尺寸回执；必要时先发现其当前 Schema。使用已保存默认时，将其供应商 ID 作为 `provider`，省略 `model`，让工具解析已保存型号；显式指定型号时，传入已核实的模型 ID 和供应商。保留用户的提示词、参考图、数量与尺寸要求。

解析默认供应商后的工具参数示例（先替换占位符，不要原样发送）：

```json
{
  "provider": "<saved-image-provider-id>",
  "prompt": "A warm, quiet library illustration, without lettering",
  "n": 1
}
```

下方原始 API 路径仍可用于其支持的原生操作或需要它的供应商。不要把该示例理解为必须绕过适用的生成工具。

## 原始 API 路径

### 解析本机服务与请求

使用系统“本机 API”指引提供的当前 agent-service 地址与调用方认证，包括当前隔离 home。不要猜测其他实例端口，也不要获取上游密钥。本机 HTTPS 使用自签证书时，可按该本机 API 契约为 curl 使用 `-k`。

对于兼容 OpenAI 图片生成协议的供应商，向 `POST /api/media-proxy` 提交已解析的供应商 ID 和上游模型 ID，代理负责注入上游认证。下方仅为请求结构示例；模型专用端点、支持的尺寸/数量和响应字段必须遵循该供应商当前契约：

```json
{
  "providerId": "<resolved-image-provider-id>",
  "serviceType": "image_gen",
  "endpoint": "/images/generations",
  "body": {
    "model": "<resolved-upstream-model-id>",
    "prompt": "A warm, quiet library illustration, without lettering",
    "n": 1
  },
  "responseType": "json"
}
```

仅传 `serviceType` 会选择供应商，不会自动填写 `body.model`。保持已解析的供应商/模型绑定一致。如果保存的供应商或模型缺失、被禁用，或所选路径不支持它，说明实际限制，不静默另选。原生 DashScope 等协议可能需要不同的文档化请求，不要向不相干的端点发送 OpenAI 兼容载荷。

### 持久化与展示结果

将可能很大的响应保存至唯一临时文件（`mktemp` 或等价方式）。不打印原始响应、base64 图片数据、认证头或带签名下载 URL。检查代理的 `success` 与供应商实际响应，按实际格式解码 `b64_json` 或下载返回的图片 URL；可用 Python 处理本地 JSON/base64。失败请求不是图片。

通过 `POST /api/media/upload` 的 multipart `file` 字段上传每张图片，读取返回的 `mediaId`。临时路径只用于中转，不是最终交付物。用实际返回的 ID 展示持久化图片：

```text
![Image description](dc-media://<returned-mediaId>)
```

使用 `GenerateImage` 时直接使用其持久化图片内容/元数据，无需再手动上传。核对实际图片与尺寸回执后，再声明请求的尺寸、比例、无字约束或画面内容是否达成。

## 失败与恢复

- 说明本次选中的供应商/模型、失败来自本地校验还是上游响应，以及有界、脱敏的错误码/信息。不暴露凭据或原始响应体。
- 配置缺失、凭据缺失、认证失败、额度/限流、参数不支持和上游通道故障是不同情况。依据实际证据诊断，不能仅凭 HTTP 状态判定哪个模型或账号有问题。
- `model_not_found`、`model_price_error` 或“No available channel”可能表示选中的网关没有授权路由。核对当前绑定/目录，说明该服务限制；不要自动切换其他模型或供应商，包括旧示例提及的型号。
- 只有响应证据和用户授权支持时才重试或另选方案。保留显式模型/供应商和费用约束；需要不同服务时让用户选择。图片实际生成并持久化之前不得宣称成功。
