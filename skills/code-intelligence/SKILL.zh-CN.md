<!-- locale: zh-CN -->

# code-intelligence 技能

## L0：一句话摘要

通过用户已经安装的 Language Server，使用 DesireCore 默认隐藏的 `Lsp` 工具完成语义代码导航。

## L1：何时使用

当任务依赖符号语义而不是文本匹配时激活本技能：

- 跳转到符号的定义或具体实现。
- 查找符号的全部语义引用。
- 查看源码位置上的类型信息或文档。
- 列出单个文件的符号大纲，或在工作区内搜索符号。
- 通过 LSP 调用层级查找调用者与被调用者。

如果需求只是文本搜索，或者没有兼容的 Language Server，改用 `Grep` 或 `Glob`。

## L2：操作流程

### 1. 检查工作区权限边界

`Lsp` 会启动能够读取授权工作区的外部索引进程，因此目标文件必须具备目录级读取权限。如果工具提示精确文件授权不足，应让用户通过 `ManageWorkDirs` 授权项目目录；不得静默扩大访问范围。

### 2. 选择一个 operation

| Operation | 用途 | 必需输入 |
|---|---|---|
| `goToDefinition` | 查找符号定义 | 文件、行、列 |
| `findReferences` | 查找语义引用，包含声明 | 文件、行、列 |
| `hover` | 查看类型信息或文档 | 文件、行、列 |
| `documentSymbol` | 获取单个文件的符号大纲 | 文件 |
| `workspaceSymbol` | 在当前工作区搜索具名符号 | 文件、非空 query |
| `goToImplementation` | 查找具体实现 | 文件、行、列 |
| `prepareCallHierarchy` | 解析当前位置的可调用符号 | 文件、行、列 |
| `incomingCalls` | 查找谁调用了目标符号 | 文件、行、列 |
| `outgoingCalls` | 查找目标符号调用了谁 | 文件、行、列 |

`line` 和 `character` 都是与编辑器一致的 1-based 坐标；列偏移使用 UTF-16 语义。

### 3. 把结果作为有边界的导航证据

- 返回位置会经过当前读取范围和工作区 `.gitignore` 过滤。
- 引用或符号过多时使用 `maxResults` 收敛结果，最大值为 200。
- 首次调用时 Language Server 可能需要索引工作区，因此耗时会更长。
- 源码文件变化后重新调用；DesireCore 会同步最新的已保存 UTF-8 内容。

### 4. 缺少 Server 时不得擅自修改系统

DesireCore 只探测用户已经安装的二进制，缺失时返回安装提示。除非用户明确要求安装依赖，否则不得执行该安装命令。

内置支持映射：

- TypeScript/JavaScript：`typescript-language-server`
- Python：`pyright-langserver`
- Go：`gopls`
- Rust：`rust-analyzer`

### 5. 降级策略

- 文件类型不支持或 Server 未安装：使用 `Grep`、`Glob`、`Read` 做文本级调查。
- Server 未声明某项能力：如实报告 capability 不匹配，不得猜测结果。
- 语义结果为空：说明符号可能未解析、被排除或被访问规则过滤；不能直接断言“没有引用”。

