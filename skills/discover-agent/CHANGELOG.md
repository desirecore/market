# Changelog

## [2.6.0] - 2026-07-18

- HTTP API 调用改为 ManageAgent 内置工具（实例鉴权后 Agent 不再直接访问本机 API）
- 声明 required_client_version 10.0.90

## [2.4.0] - 2026-02-28

- 补充"了解更多"的具体 API 实现（GET /api/agents/:id + 结构化 persona 端点）
- 匹配算法描述从伪数值权重改为语义描述，更符合 LLM 实际工作方式
- 精简上下文传递元数据

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入
