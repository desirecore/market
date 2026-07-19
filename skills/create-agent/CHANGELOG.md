# Changelog

## [2.5.4] - 2026-07-19

- 进一步去除追问/展示数量的软性倾向措辞（'别让用户负担'、'避免刷屏'），完全交由执行 Agent 自主判断，不带任何数量暗示。

## [2.5.3] - 2026-07-19

- 去除束缚执行 Agent 自主判断的机械数字策略（create 追问'每轮最多 2 个'、discover'最多展示 5 个候选'），改为交由 Agent 按情况自主把握节奏与数量，保留'别让用户负担/别刷屏'的原则意图。

## [2.5.2] - 2026-07-19

- 复盘补回改写压缩时误删的实质信息：create 的 AgentFS v2/git 版本管理定位、基础创建（name+description 自动填充 persona L0）、需求收集引导问题示例；update/delete/discover 的使用场景与版本管理定位。功能对齐原始意图，仍保留结构性压缩。

## [2.5.1] - 2026-07-19

- 提示词改写压缩，功能不变——与 ManageAgent 工具契约重复的说明、装饰框图、重复表改写融入流程，示例就地精简；不外置、不净删，意图全保留。

## [2.5.0] - 2026-07-18

- 创建方式从 HTTP API（`POST /api/agents`）改为 `ManageAgent` 内置工具（实例鉴权上线后 Agent 不再直接访问本机 API）
- 补充保留标识（core/desirecore）拒创、config 仅允许 llm 白名单的错误处理说明
- 声明 `required_client_version: 10.0.90`

## [2.4.0] - 2026-02-28

- 修复响应格式文档，与实际 API 返回对齐（`{ success, agentId, agent }`）
- AgentFS 背景知识提取到共享文件 `_agentfs-background.md`，消除重复
- 受保护路径统一引用 `_protected-paths.yaml`
- 补充"修改"分支的交互流程说明

## [2.2.0] - 2026-02-27

- API 改为结构化 L0/L1/L2 输入（PersonaInput / PrinciplesInput），所有字段可选
- 用户确认预览从原始 markdown 改为表格形式展示
- 支持最简创建（仅 name），自动补全所有默认值

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入；以用户阅读体验优先的 blockquote 格式呈现内容
