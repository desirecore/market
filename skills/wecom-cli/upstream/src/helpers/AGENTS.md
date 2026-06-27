# Helpers — AI Agent 实现指南

> 本文件面向 AI Agent。当你需要**创建、修改或维护** helper 时，阅读此文件即可完成任务。
> **无需阅读** `main.rs`、`service/` 或其他无关文件。

---

## 关键文件速查

你只需要关注以下文件：

| 文件 | 作用 | 何时需要 |
|------|------|---------|
| `src/helpers/registry.rs` | `Helper` trait 定义 + `HelperRegistry::new()` 注册表 | 新建 helper 时添加注册 |
| `src/helpers/mod.rs` | category 模块声明 | 新建 category 时添加 `mod` |
| `src/helpers/<category>/mod.rs` | 该 category 下的 helper 模块声明 | 新建 helper 时添加 `pub mod` |
| `src/helpers/<category>/<name>.rs` | helper 实现 | 新建或修改 helper |
| `src/json_rpc.rs` | `call_tool(category, method, args)` — 调用远程 MCP 工具 | helper 需要远程调用时参考 |
| `src/fs_util/` | 文件系统工具（`atomic_write`, `sanitize_filename`） | helper 需要安全写文件或处理文件名时使用 |

**不要修改**：`main.rs`、`service/handler.rs`、`service/command.rs` — helper 通过 registry 自动注册到 CLI，无需改动调度层。

---

## 现有 Helpers

> **维护要求**：新增或删除 helper 后，请同步更新此表。

| command | category | struct | 文件 | 说明 |
|---------|----------|--------|------|------|
| `+smartsheet_add_records_auto_file` | `doc` | `SmartsheetAddRecordsAutoFileHelper` | `doc/smartsheet_add_records_auto_file.rs` | 添加智能表格记录（自动上传文件/图片） |
| `+smartsheet_update_records_auto_file` | `doc` | `SmartsheetUpdateRecordsAutoFileHelper` | `doc/smartsheet_update_records_auto_file.rs` | 更新智能表格记录（自动上传文件/图片） |
| `+smartpage_create` | `doc` | `SmartpageCreateHelper` | `doc/smartpage_create.rs` | 创建智能文档（自动读取本地文件内容作为子页面） |

---

## 什么是 Helper

Helper 是一个**本地子命令**，挂载在某个 service category（如 `doc`、`msg`）下，用于实现无法由远程 MCP 工具完成的**客户端侧逻辑**（文件处理、多步编排等）。

CLI 调用形式：`wecom <category> +<helper_name> [args]`

Helper 名称以 `+` 前缀与远程 method 区分。

---

## 架构概览

```
src/helpers/
├── mod.rs              # 模块声明 + pub use HelperRegistry
├── registry.rs         # Helper trait 定义 + HelperRegistry（注册表）
├── AGENTS.md           # ← 你正在读的文件
├── HUMANS.md           # 人类需求模板（你无需阅读）
└── <category>/         # 按 category 分目录
    ├── mod.rs           # pub mod 声明
    └── <name>.rs        # 具体 helper 实现
```

### Helper trait

```rust
// src/helpers/registry.rs
pub trait Helper: Send + Sync {
    /// 所属 category（必须匹配 service::categories 中的 name）
    fn category(&self) -> &'static str;

    /// clap::Command 定义（名称必须以 + 开头）
    fn command(&self) -> clap::Command;

    /// 异步执行逻辑
    fn execute<'a>(
        &'a self,
        matches: &'a ArgMatches,
    ) -> Pin<Box<dyn Future<Output = Result<()>> + Send + 'a>>;
}
```

### 调度流程

1. `main.rs` 构建 CLI，将 helper command 注册为 category 的子命令
2. 用户输入匹配到 `<category> +<name>` 时，`handle_service_cmd` 优先查找 helper
3. 找到 helper → 调用 `helper.execute(matches)`；未找到 → 按远程 JSON-RPC 调用处理

---

## 添加新 Helper — 逐步操作

### 命名规范

| 项目 | 规范 | 示例 |
|------|------|------|
| 文件名 | `<category>_<功能描述>.rs`（snake_case） | `doc_upload_image.rs` |
| command 名 | `+<category>_<功能描述>` | `+doc_upload_image` |
| Args struct | `<Name>Args`（PascalCase） | `DocUploadImageArgs` |
| Helper struct | `<Name>Helper`（PascalCase） | `DocUploadImageHelper` |

### 1. 创建文件

在 `src/helpers/<category>/` 下新建 `<name>.rs`。如果该 category 目录不存在，同时创建目录和 `mod.rs`。

### 2. 实现 Helper trait

```rust
// src/helpers/<category>/<name>.rs
use std::future::Future;
use std::pin::Pin;

use anyhow::Result;
use clap::{ArgMatches, Args, Command, FromArgMatches};

use crate::helpers::registry::Helper;

/// 参数定义（clap derive）
#[derive(Args, Debug)]
pub struct MyArgs {
    /// 参数说明
    #[arg(long)]
    pub some_param: String,

    /// 可选参数
    #[arg(long)]
    pub optional_param: Option<String>,
}

pub struct MyHelper;

impl Helper for MyHelper {
    fn category(&self) -> &'static str {
        "<category>"  // 如 "doc", "msg", "schedule" 等
    }

    fn command(&self) -> clap::Command {
        MyArgs::augment_args(Command::new("+<name>"))
    }

    /// 在此简要描述 helper 的逻辑
    fn execute<'a>(
        &'a self,
        matches: &'a ArgMatches,
    ) -> Pin<Box<dyn Future<Output = Result<()>> + Send + 'a>> {
        Box::pin(async {
            let args = MyArgs::from_arg_matches(matches)?;
            // 实现逻辑，请注意提供对应注释...
            Ok(())
        })
    }
}
```

### 3. 注册

**a)** 在 `src/helpers/<category>/mod.rs` 中声明模块：

```rust
pub mod <name>;
```

**b)** 在 `src/helpers/mod.rs` 中声明 category 模块（如果是新 category）：

```rust
mod <category>;
```

**c)** 在 `src/helpers/registry.rs` 的 `HelperRegistry::new()` 中添加：

- 顶部添加 use：`use crate::helpers::<category>::<name>::<HelperStruct>;`
- `vec![]` 中添加：`Box::new(<HelperStruct>)`

### 4. 更新本文档

在上方「现有 Helpers」表中添加新行。

完成。无需修改 `main.rs` 或 `service/` 下的任何文件。

---

## 修改现有 Helper

1. 在「现有 Helpers」表中找到目标 helper 的文件路径
2. 直接修改对应的 `.rs` 文件
3. 如果修改了 command 名称或 category，需同步更新 `registry.rs` 中的 use 和注册，以及本文档的「现有 Helpers」表
4. 如果删除 helper，需从 `registry.rs`、`<category>/mod.rs` 中移除相关声明，并更新本文档

---

## 查询远程工具的参数格式

当你需要了解某个远程 MCP 工具的参数 schema 时，可以执行：

```bash
wecom <category> <method> --schema
```

这会输出该工具的完整定义（包含 `name`、`description`、`inputSchema`），例如：

```bash
wecom doc upload_doc_image --schema
```

在 helper 实现中，你可以根据 schema 构造正确的 `json_rpc::call_tool` 调用参数。

---

## 理解人类的接口描述

人类会用 `<category>.<method>` 简写来说明需要调用的远程接口，并用大括号描述其**请求/响应结构**。例如：

```
调用 example.example_upload {
	"content": "base64",  // 要上传的文件 base64
} {
	"url": "URL",
	"height": 234,
	"width": 234,
	"size": 81259,
}
```

你需要自行理解接口的参数和返回结构，并将其转化成对应的 JSON-RPC 调用：

```rust
let res = json_rpc::call_tool(
    "example",
    "example_upload",
    json!({
        "content": base64_of_image_file,
    }),
).await?;
```

如果人类没有提供接口描述，你可以用 `wecom <category> <method> --schema` 自行查询。

---

## 调用远程 MCP 工具 — `json_rpc` 使用

Helper 内部经常需要调用远程 MCP 工具。使用 `crate::json_rpc`：

```rust
use crate::json_rpc;
use serde_json::json;

// 标准调用（30s 超时）
let res = json_rpc::call_tool(
    "doc",                    // category
    "get_doc_content",        // method name
    json!({
        "docid": "xxx"
    }),
).await?;

// 结果在 res["result"] 中
let data = &res["result"];
```

### 错误处理

- JSON-RPC error code ≠ 0 → `JsonRpcError::Api(Value)`
- 其他错误 → `anyhow::Error`

Notes:

- 所有错误均可用 `?` 传播
- 所有错误信息均使用**中文**描述

---

## 可用 categories

| category | 说明 |
|---|---|
| `contact` | 通讯录 — 成员查询和搜索 |
| `doc` | 文档 — 文档/智能表格创建和管理 |
| `meeting` | 会议 — 创建/管理/查询视频会议 |
| `msg` | 消息 — 聊天列表、发送/接收消息、媒体下载 |
| `schedule` | 日程 — 日程增删改查和可用性查询 |
| `todo` | 待办事项 — 创建/查询/编辑待办项 |

---

## 新建 Helper Checklist

- [ ] helper 文件位于 `src/helpers/<category>/<name>.rs`
- [ ] 实现 `Helper` trait，command 名称以 `+` 开头
- [ ] `category()` 返回值匹配上方「可用 categories」表
- [ ] 在 `<category>/mod.rs` 中 `pub mod <name>`
- [ ] 在 `helpers/mod.rs` 中 `mod <category>`（如果是新 category）
- [ ] 在 `registry.rs` 顶部添加 `use` 并在 `HelperRegistry::new()` 的 vec 中添加 `Box::new(...)`
- [ ] 使用 `json_rpc::call_tool` 调用远程工具（如需要）
- [ ] 错误使用 `anyhow::Result` + `?` 传播，错误信息使用中文
- [ ] 更新本文档「现有 Helpers」表
