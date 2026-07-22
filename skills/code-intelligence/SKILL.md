---
name: code-intelligence
description: >-
  Use this skill when the user needs semantic code navigation backed by a
  Language Server: jump to definitions or implementations, find references,
  inspect hover/type information, list document or workspace symbols, or trace
  incoming and outgoing calls. Activate it for requests such as "where is this
  symbol defined", "find usages", "who calls this function", "show the file
  outline", or "search symbols in the workspace". A compatible Language Server
  must already be installed; this skill never installs one automatically. Use
  when 用户提到 跳转定义、查找引用、查找实现、类型信息、悬停信息、符号大纲、
  工作区符号、调用关系、谁调用了这个函数、这个函数调用了谁、语义代码导航。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - development
  - lsp
  - code-navigation
  - symbols
  - references
provides:
  tools:
    - Lsp
metadata:
  author: desirecore
  updated_at: '2026-07-22'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 代码智能
      short_desc: 基于 Language Server 的定义、引用、符号与调用关系导航
      description: >-
        使用已安装的 Language Server 执行语义代码导航，包括定义、引用、实现、悬停类型、符号大纲和调用层级。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:cf613ab2572810e5
      translated_by: human
    en-US:
      name: Code Intelligence
      short_desc: Language Server powered definitions, references, symbols, and call navigation
      description: >-
        Use an installed Language Server for semantic code navigation, including definitions, references, implementations, hover types, symbols, and call hierarchies.
      body: ./SKILL.md
      source_hash: sha256:cf613ab2572810e5
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ci-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="3" fill="url(#ci-a)" fill-opacity="0.1"
    stroke="url(#ci-a)" stroke-width="1.5"/><path d="M9 8l-3 4 3 4M15
    8l3 4-3 4M13 6l-2 12" stroke="url(#ci-a)" stroke-width="1.5"
    stroke-linecap="round" stroke-linejoin="round"/></svg>
  category: development
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.94
---

# code-intelligence Skill

## L0: One-line Summary

Use DesireCore's hidden `Lsp` tool for semantic code navigation through an already-installed Language Server.

## L1: When to Use

Activate this skill when the task depends on symbol meaning rather than text matching:

- Jump to a symbol's definition or implementation.
- Find all semantic references to a symbol.
- Inspect type information or documentation at a source position.
- List the symbols in one file or search symbols across the workspace.
- Find callers and callees through the LSP call hierarchy.

Use `Grep` or `Glob` instead when the task is purely textual or no compatible Language Server is installed.

## L2: Operating Procedure

### 1. Check the workspace boundary

`Lsp` starts an external indexing process that can read the authorized workspace. The target file therefore needs directory-level read access. If the tool reports that an exact-file grant is insufficient, ask the user to authorize the project directory through `ManageWorkDirs`; never widen the scope silently.

### 2. Choose one operation

| Operation | Purpose | Required input |
|---|---|---|
| `goToDefinition` | Find where a symbol is defined | file, line, character |
| `findReferences` | Find semantic references, including the declaration | file, line, character |
| `hover` | Read type information or documentation | file, line, character |
| `documentSymbol` | Outline symbols in one file | file |
| `workspaceSymbol` | Search named symbols in the current workspace | file, non-empty query |
| `goToImplementation` | Find concrete implementations | file, line, character |
| `prepareCallHierarchy` | Resolve a callable item at a position | file, line, character |
| `incomingCalls` | Find functions or methods that call the target | file, line, character |
| `outgoingCalls` | Find functions or methods called by the target | file, line, character |

`line` and `character` are 1-based, matching editor coordinates. Character offsets use UTF-16 semantics.

### 3. Treat results as bounded navigation evidence

- Results are filtered by the active read scope and workspace `.gitignore` rules.
- Use `maxResults` to keep broad reference or symbol searches focused; the maximum is 200.
- A first request may take longer while the server indexes the workspace.
- Re-run the request after source files change; DesireCore synchronizes the latest saved UTF-8 content.

### 4. Handle missing servers without modifying the system

DesireCore only discovers installed binaries and returns an installation hint when one is missing. Do not run that installation command unless the user explicitly asks you to install the dependency.

Supported built-in mappings:

- TypeScript/JavaScript: `typescript-language-server`
- Python: `pyright-langserver`
- Go: `gopls`
- Rust: `rust-analyzer`

### 5. Fallbacks

- Unsupported file type or missing server: use `Grep`, `Glob`, and `Read` for text-level investigation.
- Server does not advertise an operation: report that capability mismatch instead of guessing.
- Empty semantic result: explain that the symbol may be unresolved, excluded, or filtered by access rules; do not claim the symbol has no usages without qualification.
