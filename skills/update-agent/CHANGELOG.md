# Changelog

## [2.2.0] - 2026-02-27

- 新增结构化 persona/principles API 端点（GET/PUT）说明
- 推荐使用结构化 API 替代原始文件写入

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入；新增 PUT /api/agents/:id/files/* 端点说明
