# Changelog

## [3.1.2] - 2026-07-19

- 提示词改写压缩，功能不变——与 ManageAgent 工具契约重复的说明、装饰框图、重复表改写融入流程，示例就地精简；不外置、不净删，意图全保留。

## [3.1.1] - 2026-07-18

- 修正示例字段名：`communicationStyle` → `communication_style`、`must` → `must_do`；`personality` 示例改为字符串数组
- `get` 返回示例对齐真实输出格式（`## persona.md` / `## principles.md` 段落含分层 markdown 原文，客户端 ≥ 10.0.90）
- 附录补充结构化字段名固定清单（persona L1.role/personality/communication_style；principles L1.must_do/must_not/priority）

## [3.1.0] - 2026-07-18

- 结构化字段（name/description/llm/persona/principles）改经进程内内置工具 **ManageAgent** 的 `update` 动作更新（白名单 + schema 校验 + 合并语义），移除对 `agent.json` / `persona.md` / `principles.md` 的直接 Write 指引
- 补充合并语义说明：结构化 persona/principles 为字段级合并（省略字段保留原值）、markdown 字符串为整体替换、config.llm 为增量浅合并；非法配置不落盘
- 补充确认行为：更新自身免确认、更新其他智能体触发用户确认、核心智能体（desirecore/core）拒绝更新
- 补充错误处理：config 非白名单字段被拒、schema 校验失败、部分字段写入失败仅重试失败字段
- 记忆、技能、工具等自由格式文件仍用 Read/Write 直接编辑（注意 `_protected-paths.yaml` 受保护路径），版本回滚按目标类型分流（结构化走 ManageAgent、自由文件直接写回）
- 声明 `required_client_version: 10.0.90`

## [3.0.0] - 2026-03-17

- **Breaking**：从 HTTP API 迁移到 AgentFS 直接文件操作
- 移除所有 HTTP API 端点引用（PUT persona/principles/files）
- 变更应用改为直接读写 `${DESIRECORE_ROOT}/agents/<agentId>/` 下的文件
- 回滚流程改用 git log/show 命令查看历史版本
- 错误处理改为文件系统错误（文件不存在、权限不足等）

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
