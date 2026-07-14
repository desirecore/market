---
name: markdown
description: >-
  Use this skill whenever the user wants to create, write, organize, or draft
  Markdown documents (.md files). Triggers include: any mention of
  "md", ".md", "markdown", or requests to produce written deliverables such
  as reports, summaries, plans, outlines, meeting notes, lists, tables,
  contracts, memos, weekly reports, or any text-based document without a
  specific format requirement (Word/PDF/Excel/PPT). When the user asks to
  "write a report", "organize a table", "draft a plan", "make a list", or
  similar — and does not specify a particular file format — default to
  Markdown. Do NOT use for binary document formats (.docx, .pdf, .xlsx,
  .pptx) — use the corresponding skill instead.
  Use when 用户提到 整理、准备、汇总、梳理、归纳、制作、生成、起草、编写、
  创建、文档、报告、表格、清单、方案、计划、总结、大纲、合同、纪要、周报、
  月报、邮件、对比分析、会议记录、散文、文章、作文、md、markdown、report、
  summary、plan、outline、memo、table、list、draft、document、notes、
  write、create、organize。
version: 1.0.1
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - markdown
  - md
  - document
  - text
metadata:
  author: desirecore
  updated_at: '2026-07-14'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: Markdown 文档处理
      short_desc: 创建、编辑 Markdown 文档（.md），默认文本文档格式
      description: >-
        当用户要求创建、撰写、整理任何书面产物且未指定特定格式时，使用此技能。
        确保使用 Write 工具写入文件、告知绝对路径、并通过 SendUserMessage 发送附件。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:0000000000000000
      translated_by: human
    en-US:
      name: Markdown Document Processing
      short_desc: Create and edit Markdown documents (.md), the default text format
      description: >-
        Use when the user requests any written deliverable without specifying a
        particular format. Ensures files are written via Write tool, absolute
        path is reported, and attachment is sent via SendUserMessage.
      body: ./SKILL.md
      source_hash: sha256:2434b01b42d751c0
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="md-a" x1="4" y1="2" x2="20"
    y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><path d="M14
    2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
    fill="url(#md-a)" fill-opacity="0.1" stroke="url(#md-a)"
    stroke-width="1.5"/><path d="M14 2v6h6" stroke="url(#md-a)"
    stroke-width="1.5" stroke-linejoin="round"/><text x="7" y="17"
    font-size="7" font-weight="bold" fill="url(#md-a)"
    font-family="Arial">MD</text></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# markdown Skill

## L0: One-line Summary

Create Markdown documents (.md) using the Write tool, with proper file output and delivery to the user.

## L1: Overview and Use Cases

### Capability

markdown is a **Procedural Skill** that serves as the default document format when users request written deliverables without specifying Word/PDF/Excel/PPT. Markdown files can be directly opened and edited in DesireCore's built-in SuperDoc editor.

### Use Cases

- The user asks to create a report, summary, plan, outline, or any written document
- The user asks to organize information into a table or list
- The user asks to draft a memo, meeting notes, weekly report, etc.
- The user asks to "write something" or "make a document" without specifying format
- The user explicitly mentions "md", "markdown", or ".md"

## L2: Detailed Specification

### Output Rule (CRITICAL — violation = task failure)

After you create a .md file using the Write tool, you **MUST** complete these **two** final steps:

**Final Step 1:** Output a text reply containing:
- A brief summary of what was created or changed
- The file's full absolute path (copied from the Write tool result)

Template:
```
已为你创建「文档标题」，简要说明内容。

📄 文件位置：`/full/absolute/path/filename.md`
```

**Final Step 2:** Call `SendUserMessage` with the file as attachment. This **MUST** be your very last action. Do NOT output any text after this call.

```
SendUserMessage({
  message: "📄 点击下方附件打开文件",
  attachments: ["/full/absolute/path/filename.md"]
})
```

#### Correct vs Wrong

- ✅ Write → text reply (with absolute path) → SendUserMessage (with attachment) → done
- ❌ Write → text reply without absolute path
- ❌ Write → no SendUserMessage
- ❌ Write → SendUserMessage → more text output (e.g. "任务完成")
- ❌ No Write at all, content output directly in chat

#### Forbidden

- Outputting the full document content directly in the chat reply instead of writing to a file
- Saying "好的，已完成" / "整理好了" / "以下是内容" without calling Write tool
- Only giving a filename (e.g. "报告.md") without the full absolute path
- Not calling SendUserMessage to deliver the file attachment
- Outputting any text after SendUserMessage
- Writing memory files about the document creation task — creating/editing a document is a one-time task, NOT a user preference or fact to remember

### Overview

Markdown (.md) is a lightweight text format. The Write tool accepts the content directly — no compilation, no external dependencies. The file is immediately available for viewing in DesireCore's SuperDoc editor.

### Creating New Documents

#### Workflow

1. Determine content structure (headings, sections, tables)
2. Choose file path: user specified > workspace directory
3. Call Write tool with full absolute path + complete content
4. Output text reply with summary + absolute path
5. Call SendUserMessage with file attachment (last action)

#### File Naming

- Use descriptive names: `2026-05-11-项目进度表.md`, `会议纪要-产品评审.md`
- Avoid generic names like `output.md` or `document.md`
- Use the workspace directory as default location

#### Complete Example

User: "帮我整理一份项目进度表"

**Write:**
```
Write({
  file_path: "/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md",
  content: "# 项目进度表\n\n| 模块 | 状态 | 负责人 | 截止日期 |\n|------|------|--------|----------|\n| 认证模块 | 已完成 | 张三 | 2026-05-01 |\n| 支付模块 | 进行中 | 李四 | 2026-05-15 |"
})
```

**Final Step 1** — Text reply:
```
已为你整理好「项目进度表」，包含各模块的当前状态、负责人和截止日期。

📄 文件位置：`/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md`
```

**Final Step 2** — SendUserMessage (last action):
```
SendUserMessage({
  message: "📄 点击下方附件打开文件",
  attachments: ["/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md"]
})
```
