# Changelog

## [2.5.2] - 2026-07-19

- 复盘补回改写压缩时误删的实质信息：create 的 AgentFS v2/git 版本管理定位、基础创建（name+description 自动填充 persona L0）、需求收集引导问题示例；update/delete/discover 的使用场景与版本管理定位。功能对齐原始意图，仍保留结构性压缩。

## [2.5.1] - 2026-07-19

- 提示词改写压缩，功能不变——与 ManageAgent 工具契约重复的说明、装饰框图、重复表改写融入流程，示例就地精简；不外置、不净删，意图全保留。

## [2.5.0] - 2026-07-18

- HTTP API 调用改为 ManageAgent 内置工具（实例鉴权后 Agent 不再直接访问本机 API，会 401）
- 删除路径改为 `ManageAgent(action='delete', id, deleteRuns)`；列出/查详情改为 `action='list' | 'get'`
- 错误处理由 HTTP 状态码改为工具返回的拒绝语义（核心智能体/自删/活跃状态/不存在）
- 补充团队级联说明（组长删除→解散、成员删除→移除）
- 声明 required_client_version 10.0.90

## [2.4.0] - 2026-02-28

- 统一 frontmatter 字段顺序，与其他三个技能一致
- tags 从中文改为英文（机器可读标识符）
- 合并"前置检查"与"错误处理"为统一的"状态验证与错误处理"段落
- 补充停止活跃智能体的具体方式（Socket.IO agent:shutdown 事件）
- 精简"删除范围说明"为对照表格式

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入
