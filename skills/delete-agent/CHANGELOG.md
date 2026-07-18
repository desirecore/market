# Changelog

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
