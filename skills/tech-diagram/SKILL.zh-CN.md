<!-- locale: zh-CN -->

# tech-diagram 技能

把自然语言描述转成品牌一致的技术图。你在回复中写 **Mermaid**，DesireCore 对话会即时渲染为 SVG。本技能的核心价值是一致性：每张图都用同一套 DesireCore 3+2 配色和同一套语义形状/箭头词汇表，让所有图看起来像出自同一个产品。

## 何时使用

用于**结构、流程或关系**类的图：架构图、流程图、时序图、状态机、ER 图、类图、思维导图。

不要用它生成写实摄影或插画类图片——那类需求请转给文生图技能（如 dashscope-image-gen、minimax-image-gen）。

## 强制风格规则

以下规则不可妥协，违反会产出偏离品牌或无法渲染的图。

1. **每张图必须以某风格的 `%%{init}%%` 指令开头**（用它覆盖对话写死的暗色全局主题）。除非用户另有要求，默认用 `brand-light`（见下方**风格**）。`references/styles.md` 的预设是完整的 **flowchart** 骨架（`%%{init}%%` + `flowchart TD` + 五个 `classDef`）：画 flowchart 时整块复制；画 `sequenceDiagram` / `stateDiagram-v2` / `erDiagram` / `classDiagram` / `mindmap` 时**只复制首行 `%%{init}%%`**（这些图类型不支持 `classDef`）。
2. **flowchart 内每个节点都用这五个 `classDef` 上色，不要临时写 hex**（非 flowchart 图类型没有 `classDef`，只继承风格的 `%%{init}%%` 底色与字体）。类名——`agent` / `system` / `biz` / `warn` / `error`——在所有风格里都相同，所以换风格时 flowchart 图体完全不用改。按角色选类：系统/通用→`system`，知识/学习→`agent`，业务/执行→`biz`，项目管理/警示/决策→`warn`，错误/失败→`error`。
3. **使用下面的语义形状**，不要随意选形状。
4. **标签含标点、括号或 `/` 时必须加引号**，避免 Mermaid 解析失败，例如 `A["查询 / 检索"]`。

## 风格

六套可选视觉风格放在 `references/styles.md`，每套是一段现成的 **flowchart** 头部（`%%{init}%%` + 五个 `classDef`；非 flowchart 图类型只复制 `%%{init}%%` 首行，见规则 1）。换风格只换头部，节点/连线图体不变。

| 风格 | 外观 | 适用 |
|------|------|------|
| `brand-light`（默认） | 白底、DesireCore 3+2 强调色 | 博客、幻灯片、文档 |
| `brand-dark` | 近黑底、3+2 强调色 | 与 app 暗色模式一致 |
| `terminal` | `#0f0f1a`、霓虹强调、等宽字 | GitHub / 开发者文章 |
| `blueprint` | 深蓝底、青/白、等宽字 | 架构规范 |
| `cream` | 暖奶油底、赤褐/鼠尾草/紫 | Anthropic 风演示 |
| `mono` | 纯白、灰阶 | Notion / Wiki |

按用户措辞选（"暗色/dark"、"蓝图/blueprint"、"奶油/cream"、"极简/mono"、"极客/terminal"，或"风格 N / style N"），否则用 `brand-light`。图表是用户产物，所以非 `brand-*` 的调色板**有意**跳出 app 的 3+2 色彩规则（该规则约束产品 UI，不约束导出的图）。每套预设内部自洽。

## 语义词汇表

形状本身承载含义（完整表见 `references/semantic-vocabulary.md`）。类的颜色随风格变化，固定的只是"角色→类"映射：

| 概念 | Mermaid 形状 | classDef |
|------|-------------|----------|
| Agent / 智能体 | 六边形 `id{{...}}` | agent |
| DesireCore 核心 / 系统 | 圆角 `id(...)` | system |
| LLM / 模型 | 圆角 `id(⚡ ...)` | system |
| 业务 / 执行节点 | 矩形 `id[...]` | biz |
| 记忆 / 存储 | 圆柱 `id[(...)]` | system |
| 用户 | 体育场形 `id([...])` | biz |
| 决策 / 分支 | 菱形 `id{...}` | warn |
| 外部服务 | 虚线 `subgraph` | — |

## 箭头与流编码

| 流类型 | Mermaid 边 |
|--------|-----------|
| 主数据流 | `-->` 实线 |
| 记忆写入 / 持久化 | `-.->` 点线 |
| 异步事件 | `-.->|async|` 点线 + 标签 |
| 反馈 / 重试循环 | 指回前序节点的回边 `-->` |

## 内置模板

DesireCore 自身 Pattern 的现成 Mermaid 放在 `references/templates.md`：**Agent 架构图**、**Delegate 6 模式**、**三层对话记忆**（active → recent L0/L1 → archive L2）、**关系图谱**（6 种边：delegate / mention / co_task / hierarchy / seek_help / escalation）。请基于这些模板改写为用户的主题，而非从零开始。

## 输出约定

直接在回复中用栅栏代码块输出图，info string 为 `mermaid`（用三个反引号紧跟单词 mermaid 开启栅栏）。对话会自动渲染为 SVG；语法出错时会降级展示原始代码（`mermaid-fallback` 路径），所以源码必须合法。节点标签要短——文字过长会撑坏布局。

## 常见错误

- ❌ 漏掉风格头部 → 图会沿用全局暗色主题。
- ❌ 在节点上临时写 hex，而非用所选风格的五个 `classDef`。
- ❌ 一张图里混用两套风格的头部。
- ❌ 节点标签过长撑爆布局。
- ❌ 含 `()`、`/` 或中文标点的标签未加引号 → Mermaid 解析失败。
