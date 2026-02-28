# Changelog

## [2.4.0] - 2026-02-28

- 阶段 5"变更应用"统一为 HTTP API 调用，移除所有 Git 操作示例
- AgentFS 背景知识提取到共享文件 `_agentfs-background.md`，消除重复
- 受保护路径统一引用 `_protected-paths.yaml`
- 新增 Persona 修改示例（GET → 修改字段 → PUT 流程）
- 精简版本回滚流程，移除 Git 命令示例
- 错误处理移除 Git 相关条目，改为 API 错误码

## [2.2.0] - 2026-02-27

- 新增结构化 persona/principles API 端点（GET/PUT）说明
- 推荐使用结构化 API 替代原始文件写入

## [2.1.0] - 2026-02-26

- 移除 fetch_api 依赖，改为通过 Bash/curl 调用 HTTP API；API 地址由 system prompt 注入；新增 PUT /api/agents/:id/files/* 端点说明
