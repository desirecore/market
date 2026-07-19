# Changelog

## [2.6.2] - 2026-07-19

- 复盘补回改写压缩时误删的实质信息：create 的 AgentFS v2/git 版本管理定位、基础创建（name+description 自动填充 persona L0）、需求收集引导问题示例；update/delete/discover 的使用场景与版本管理定位。功能对齐原始意图，仍保留结构性压缩。

## [2.6.1] - 2026-07-19

- 提示词改写压缩，功能不变——与 ManageAgent 工具契约重复的说明、装饰框图、重复表改写融入流程，示例就地精简；不外置、不净删，意图全保留。

## [2.6.0] - 2026-07-18

- HTTP API 调用改为 ManageAgent 内置工具（实例鉴权后 Agent 不再直接访问本机 API）
- 声明 required_client_version 10.0.90

## [2.4.0] - 2026-02-28

- 补充"了解更多"的具体 API 实现（GET /api/agents/:id + 结构化 persona 端点）
- 匹配算法描述从伪数值权重改为语义描述，更符合 LLM 实际工作方式
- 精简上下文传递元数据

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入
