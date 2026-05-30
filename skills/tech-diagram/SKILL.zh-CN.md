<!-- locale: zh-CN -->

# tech-diagram 技能

把自然语言描述转成品牌一致的技术图。你在回复中写 **Mermaid**，DesireCore 对话会即时渲染为 SVG。本技能的核心价值是一致性：每张图都用同一套 DesireCore 3+2 配色和同一套语义形状/箭头词汇表，让所有图看起来像出自同一个产品。

## 何时使用

用于**结构、流程或关系**类的图：架构图、流程图、时序图、状态机、ER 图、类图、思维导图。

不要用它生成写实摄影或插画类图片——那类需求请转给文生图技能（如 dashscope-image-gen、minimax-image-gen）。

## 强制风格规则

以下规则不可妥协，违反会产出偏离品牌或无法渲染的图。

1. **每张图必须以品牌 `%%{init}%%` 指令开头。** 对话的全局 Mermaid 主题写死为暗色；init 指令按图覆盖它，从而输出浅色且品牌一致。固定使用：
   ```
   %%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
   ```
2. **配色只能取自 DesireCore 3+2 体系，通过 `classDef` 绑定。** 禁止使用 Mermaid 默认色或任何非 3+2 色值。下面五个 class 是唯一允许的色板：
   ```
   classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
   classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
   classDef biz    fill:#F0FDF4,stroke:#34C759,color:#1d1d1f
   classDef warn   fill:#FFFBF0,stroke:#FF9500,color:#1d1d1f
   classDef error  fill:#FFF0F0,stroke:#FF3B30,color:#1d1d1f
   ```
   色值来自 DesireCore app 代码库（`app/theme/tokens/index.ts`：green `#34C759` / blue `#007AFF` / purple `#AF52DE` / orange `#FF9500` / red `#FF3B30`，以及 `cardBgColors` / `cardBorderColors`；这些 app 路径不在本 market 仓库内）。选 class 的规则与 `agent-colors.ts` 一致：系统/通用→blue，知识/学习→purple，业务/执行→green，项目管理/警示→orange，错误→red。
3. **使用下面的语义形状**，不要随意选形状。
4. **标签含标点、括号或 `/` 时必须加引号**，避免 Mermaid 解析失败，例如 `A["查询 / 检索"]`。

## 语义词汇表

形状本身承载含义（完整表见 `references/semantic-vocabulary.md`）：

| 概念 | Mermaid 形状 | classDef |
|------|-------------|----------|
| Agent / 智能体 | 六边形 `id{{...}}` | agent (purple) |
| DesireCore 核心 / 系统 | 圆角 `id(...)` | system (blue) |
| LLM / 模型 | 圆角 `id(⚡ ...)` | system (blue) |
| 业务 / 执行节点 | 矩形 `id[...]` | biz (green) |
| 记忆 / 存储 | 圆柱 `id[(...)]` | system (blue) |
| 用户 | 体育场形 `id([...])` | biz (green) |
| 决策 / 分支 | 菱形 `id{...}` | warn (orange) |
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

- ❌ 漏掉 `%%{init}%%` → 图会沿用全局暗色主题。
- ❌ 硬编码非 3+2 色值或 Tailwind 默认色，而非用 `classDef`。
- ❌ 节点标签过长撑爆布局。
- ❌ 含 `()`、`/` 或中文标点的标签未加引号 → Mermaid 解析失败。
