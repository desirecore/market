# Changelog

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
