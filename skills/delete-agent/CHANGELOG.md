# Changelog

## [2.4.0] - 2026-02-28

- 统一 frontmatter 字段顺序，与其他三个技能一致
- tags 从中文改为英文（机器可读标识符）
- 合并"前置检查"与"错误处理"为统一的"状态验证与错误处理"段落
- 补充停止活跃智能体的具体方式（Socket.IO agent:shutdown 事件）
- 精简"删除范围说明"为对照表格式

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入
