# AI Agent 指引

> 本文件帮助 AI Agent 快速定位项目关键文件，避免阅读无关代码。

## 项目概述

`wecom-cli` 是一个企业微信 CLI 工具（Rust），通过 JSON-RPC 调用远程 MCP 服务。CLI 结构为：

```
wecom <category> <method>          # 远程工具调用
wecom <category> +<helper_name>    # 本地 helper（+ 前缀）
```

## 任务路由

根据任务类型，阅读对应指引文件即可，**不需要阅读其他文件**：

| 任务 | 指引文件 | 你需要修改的文件 |
|------|----------|-----------------|
| 新建/维护现有 helper | [`src/helpers/AGENTS.md`](src/helpers/AGENTS.md) | 对应 helper 的 `.rs` 文件 |
| 理解人类的需求格式 | [`src/helpers/HUMANS.md`](src/helpers/HUMANS.md) | — |

## 项目结构速查

```
src/
├── main.rs                # CLI 入口，构建 clap Command
├── json_rpc.rs            # 远程调用：call_tool(category, method, args)
├── fs_util/               # 文件系统工具（atomic_write, sanitize_filename）
├── service/
│   └── handler.rs         # 调度逻辑：helper 优先 → fallback 远程调用
└── helpers/               # ⭐ Helper 子系统（详见 helpers/AGENTS.md）
    ├── mod.rs             # 模块声明
    ├── registry.rs        # Helper trait + HelperRegistry
    ├── AGENTS.md          # AI 实现指南（核心文档）
    └── <category>/        # 按 category 分目录存放 helper
```

## 注意事项

- **不要修改 `main.rs` 和 `service/` 下的文件**：helper 系统通过 registry 自动注册，无需改动调度层
- 用户的需求描述格式参考 [`src/helpers/HUMANS.md`](src/helpers/HUMANS.md)，除非用户直接声明，否则你无需阅读这篇文档
