# markdown Skill

## L0: 一句话摘要

使用 Write 工具创建 Markdown 文档（.md），确保文件正确输出并交付给用户。

## L1: 概述与使用场景

### 能力

markdown 是一个**程序化技能**，作为用户请求书面产物时的默认文档格式（当用户未指定 Word/PDF/Excel/PPT 时）。Markdown 文件可在 DesireCore 内置的 SuperDoc 编辑器中直接打开和编辑。

### 使用场景

- 用户要求创建报告、总结、方案、大纲或任何书面文档
- 用户要求整理信息为表格或清单
- 用户要求起草备忘录、会议纪要、周报等
- 用户说"写一份"、"整理一下"、"做一个文档"但未指定格式
- 用户明确提到"md"、"markdown"、".md"

## L2: 详细规范

### Output Rule（关键规则 — 违反 = 任务失败）

当你使用 Write 工具创建 .md 文件后，**必须**完成以下两个最终步骤：

**最终步骤 1：** 输出一段文字回复，包含：
- 内容简要说明（创建了什么 / 修改了什么）
- 文件的完整绝对路径（从 Write 工具返回结果中复制）

模板：
```
已为你创建「文档标题」，简要说明内容。

📄 文件位置：`/完整绝对路径/文件名.md`
```

**最终步骤 2：** 调用 `SendUserMessage` 将文件作为附件发送。**必须是最后一个动作，之后不再输出任何文字。**

```
SendUserMessage({
  message: "📄 点击下方附件打开文件",
  attachments: ["/完整绝对路径/文件名.md"]
})
```

#### 正确 vs 错误

- ✅ Write → 文字回复（含绝对路径）→ SendUserMessage（含附件）→ 结束
- ❌ Write → 文字回复中没有绝对路径
- ❌ Write → 没有调用 SendUserMessage
- ❌ Write → SendUserMessage → 又输出文字（如"任务完成"）
- ❌ 没有调用 Write，内容直接输出在对话中

#### 禁止行为

- 将完整文档内容直接输出在回复中，不调用 Write 工具
- 回复"好的，已完成"、"整理好了"、"以下是内容"但未调用 Write
- 只给文件名（如"报告.md"）不给完整绝对路径
- 不调用 SendUserMessage 发送附件
- 在 SendUserMessage 之后再输出任何文字
- 为文档创建/编辑任务写入记忆文件——创建或编辑文档是一次性任务，不是用户偏好或需要记住的事实

### 概述

Markdown（.md）是轻量级文本格式。Write 工具直接接受内容写入——无需编译、无需外部依赖。文件写入后可立即在 DesireCore 的 SuperDoc 编辑器中查看。

### 创建新文档

#### 工作流

1. 确定内容结构（标题、章节、表格）
2. 确定文件路径：用户指定 > 工作目录
3. 调用 Write 工具，使用完整绝对路径 + 完整内容
4. 输出文字回复：内容摘要 + 绝对路径
5. 调用 SendUserMessage 发送文件附件（最后一步）

#### 文件命名

- 使用描述性名称：`2026-05-11-项目进度表.md`、`会议纪要-产品评审.md`
- 避免泛用名称如 `output.md`、`document.md`
- 默认保存到工作目录

#### 完整示例

用户："帮我整理一份项目进度表"

**Write：**
```
Write({
  file_path: "/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md",
  content: "# 项目进度表\n\n| 模块 | 状态 | 负责人 | 截止日期 |\n|------|------|--------|----------|\n| 认证模块 | 已完成 | 张三 | 2026-05-01 |\n| 支付模块 | 进行中 | 李四 | 2026-05-15 |"
})
```

**最终步骤 1** — 文字回复：
```
已为你整理好「项目进度表」，包含各模块的当前状态、负责人和截止日期。

📄 文件位置：`/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md`
```

**最终步骤 2** — SendUserMessage（最后一步）：
```
SendUserMessage({
  message: "📄 点击下方附件打开文件",
  attachments: ["/Users/zhangxinyuan/.desirecore-dev/users/.../workspace/2026-05-11-项目进度表.md"]
})
```
