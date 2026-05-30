---
name: tech-diagram
description: >-
  Use this skill when the user wants to turn a description into a technical
  diagram — architecture diagrams, flowcharts, sequence diagrams, state
  machines, ER diagrams, class diagrams, or mind maps. Generates brand-consistent
  Mermaid that the DesireCore chat renders inline as SVG, styled with the
  DesireCore 3+2 design tokens and a semantic shape/arrow vocabulary. Use this
  for diagrams of structure, flow, or relationships — NOT for photographic or
  illustrative images (use an image-generation skill for those).
  Use when 用户提到 画架构图、架构图、流程图、时序图、序列图、状态图、状态机、
  ER图、类图、思维导图、出图、画图、可视化、画一张图、画个图、draw diagram、
  architecture diagram、flowchart、sequence diagram。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
tags:
  - diagram
  - mermaid
  - architecture
  - flowchart
  - visualization
metadata:
  author: desirecore
  updated_at: '2026-05-30'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 技术架构图生成
      short_desc: 用 Mermaid 画品牌一致的架构图/流程图/时序图，对话内即时渲染
      description: >-
        当用户希望把描述转成技术图时使用此技能——架构图、流程图、时序图、状态机、ER 图、类图或思维导图。生成符合 DesireCore 3+2 设计令牌与语义形状/箭头词汇表的 Mermaid，对话内即时渲染为 SVG。用于结构、流程或关系类图，而非写实摄影/插画类图片（后者请用文生图技能）。用户提到 画架构图、架构图、流程图、时序图、序列图、状态图、状态机、ER图、类图、思维导图、出图、画图、可视化、画一张图、画个图。
      body: ./SKILL.zh-CN.md
      source_hash: 'sha256:e3792548a07e86ac'
      translated_by: human
    en-US:
      name: Tech Diagram Generator
      short_desc: Draw brand-consistent architecture/flow/sequence diagrams with Mermaid, rendered inline in chat
      description: >-
        Use this skill when the user wants to turn a description into a technical diagram — architecture diagrams, flowcharts, sequence diagrams, state machines, ER diagrams, class diagrams, or mind maps. Generates brand-consistent Mermaid that the DesireCore chat renders inline as SVG, styled with the DesireCore 3+2 design tokens and a semantic shape/arrow vocabulary. Use this for diagrams of structure, flow, or relationships — not for photographic or illustrative images.
      body: ./SKILL.md
      source_hash: 'sha256:e3792548a07e86ac'
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1.5"
    stroke="#007AFF" stroke-width="1.5" fill="#007AFF"
    fill-opacity="0.12"/><rect x="14" y="3" width="7" height="7" rx="1.5"
    stroke="#AF52DE" stroke-width="1.5" fill="#AF52DE" fill-opacity="0.12"/><rect
    x="8.5" y="15" width="7" height="6" rx="1.5" stroke="#34C759"
    stroke-width="1.5" fill="#34C759" fill-opacity="0.12"/><path d="M6.5 10v2.5h11V10"
    stroke="#6e6e73" stroke-width="1.2"/><path d="M12 12.5V15" stroke="#6e6e73"
    stroke-width="1.2"/></svg>
  short_desc: Draw brand-consistent architecture/flow/sequence diagrams with Mermaid
  category: development
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# tech-diagram Skill

Turn a natural-language description into a brand-consistent technical diagram.
You write **Mermaid** in your reply; the DesireCore chat renders it inline as SVG.
The point of this skill is consistency: every diagram uses the same DesireCore
3+2 palette and the same semantic shape/arrow vocabulary, so diagrams look like
they belong to one product.

## When to Use

Use this skill for diagrams of **structure, flow, or relationships**:
architecture, flowchart, sequence, state machine, ER, class diagram, mind map.

Do NOT use it for photographic or illustrative pictures — route those to an
image-generation skill (e.g. dashscope-image-gen, minimax-image-gen).

## Mandatory Style Rules

These are non-negotiable. Violating them produces off-brand or unrendered diagrams.

1. **Every diagram MUST start with the brand `%%{init}%%` directive.** The chat's
   global Mermaid theme is hardcoded to dark; the init directive overrides it per
   diagram so output is light and brand-consistent. Use exactly:
   ```
   %%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
   ```
2. **Color ONLY from the DesireCore 3+2 system via `classDef`.** Never use Mermaid
   default colors or any non-3+2 hex. The five classes below are the only palette:
   ```
   classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
   classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
   classDef biz    fill:#F0FDF4,stroke:#34C759,color:#1d1d1f
   classDef warn   fill:#FFFBF0,stroke:#FF9500,color:#1d1d1f
   classDef error  fill:#FFF0F0,stroke:#FF3B30,color:#1d1d1f
   ```
   Values come from `app/theme/tokens/index.ts` (green `#34C759` / blue `#007AFF`
   / purple `#AF52DE` / orange `#FF9500` / red `#FF3B30`) and `cardBgColors` /
   `cardBorderColors`. Pick the class by the same rule as `agent-colors.ts`:
   system/generic → blue, knowledge/learning → purple, business/execution → green,
   project-management/warning → orange, error → red.
3. **Use the semantic shapes below**, not arbitrary ones.
4. **Quote any node label that contains punctuation, parentheses, or `/`** to avoid
   Mermaid parse errors, e.g. `A["Query / Retrieve"]`.

## Semantic Vocabulary

Shape carries meaning (see `references/semantic-vocabulary.md` for the full table):

| Concept | Mermaid shape | classDef |
|---------|---------------|----------|
| Agent / 智能体 | hexagon `id{{...}}` | agent (purple) |
| DesireCore core / system | rounded `id(...)` | system (blue) |
| LLM / model | rounded `id(⚡ ...)` | system (blue) |
| Business / execution node | rect `id[...]` | biz (green) |
| Memory / store | cylinder `id[(...)]` | system (blue) |
| User | stadium `id([...])` | biz (green) |
| Decision / branch | diamond `id{...}` | warn (orange) |
| External service | dashed `subgraph` | — |

## Arrow / Flow Encoding

| Flow | Mermaid edge |
|------|--------------|
| Primary data flow | `-->` solid |
| Memory write / persistence | `-.->` dotted |
| Async event | `-.->|async|` dotted + label |
| Feedback / retry loop | back-edge `-->` to an earlier node |

## Built-in Templates

Ready-to-use Mermaid for DesireCore's own patterns lives in
`references/templates.md`: **Agent architecture**, **Delegate 6 modes**,
**three-tier conversation memory** (active → recent L0/L1 → archive L2), and the
**relation graph** (6 edge types: delegate / mention / co_task / hierarchy /
seek_help / escalation). Adapt them to the user's subject instead of starting
from scratch.

## Output Convention

Emit the diagram directly in your reply inside a ` ```mermaid ` fenced block.
The chat renders it to SVG automatically; on a syntax error it falls back to
showing the raw code (the `mermaid-fallback` path), so the source MUST be valid.
Keep node labels short — long text breaks the layout.

## Common Mistakes

- ❌ Omitting `%%{init}%%` → the diagram inherits the global dark theme.
- ❌ Hardcoding non-3+2 hex or Tailwind default colors instead of the `classDef`s.
- ❌ Overlong node labels that overflow the layout.
- ❌ Unquoted labels with `()`, `/`, or CJK punctuation → Mermaid parse failure.
