---
name: tech-diagram
description: >-
  Use this skill when the user wants to turn a description into a technical
  diagram — architecture diagrams, flowcharts, sequence diagrams, state
  machines, ER diagrams, class diagrams, or mind maps. Generates brand-consistent
  Mermaid that the DesireCore chat renders inline as SVG, with a semantic
  shape/arrow vocabulary and 6 selectable visual styles (brand-light, brand-dark,
  terminal, blueprint, cream, mono). Use this for diagrams of structure, flow, or
  relationships — NOT for photographic or illustrative images (use an
  image-generation skill for those).
  Use when 用户提到 画架构图、架构图、流程图、时序图、序列图、状态图、状态机、
  ER图、类图、思维导图、出图、画图、可视化、画一张图、画个图、风格、暗色风格、
  蓝图风格、奶油风格、draw diagram、architecture diagram、flowchart、sequence diagram。
version: 1.1.0
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
  updated_at: '2026-05-31'
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
        当用户希望把描述转成技术图时使用此技能——架构图、流程图、时序图、状态机、ER 图、类图或思维导图。生成带语义形状/箭头词汇表的 Mermaid，对话内即时渲染为 SVG，并提供 6 套可选视觉风格（brand-light/brand-dark/terminal/blueprint/cream/mono）。用于结构、流程或关系类图，而非写实摄影/插画类图片（后者请用文生图技能）。用户提到 画架构图、架构图、流程图、时序图、序列图、状态图、状态机、ER图、类图、思维导图、出图、画图、可视化、画一张图、画个图、风格、暗色风格、蓝图风格、奶油风格。
      body: ./SKILL.zh-CN.md
      source_hash: 'sha256:9f72c79fe36aa8c8'
      translated_by: human
    en-US:
      name: Tech Diagram Generator
      short_desc: Draw brand-consistent architecture/flow/sequence diagrams with Mermaid, rendered inline in chat
      description: >-
        Use this skill when the user wants to turn a description into a technical diagram — architecture diagrams, flowcharts, sequence diagrams, state machines, ER diagrams, class diagrams, or mind maps. Generates Mermaid with a semantic shape/arrow vocabulary that the DesireCore chat renders inline as SVG, with 6 selectable visual styles (brand-light/brand-dark/terminal/blueprint/cream/mono). Use this for diagrams of structure, flow, or relationships — not for photographic or illustrative images.
      body: ./SKILL.md
      source_hash: 'sha256:9f72c79fe36aa8c8'
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

Turn a natural-language description into a polished technical diagram. You write
**Mermaid** in your reply; the DesireCore chat renders it inline as SVG. The point
of this skill is consistency: a fixed semantic shape/arrow vocabulary plus a set
of six self-contained visual styles (default `brand-light`), so every diagram is
coherent and on-style.

## When to Use

Use this skill for diagrams of **structure, flow, or relationships**:
architecture, flowchart, sequence, state machine, ER, class diagram, mind map.

Do NOT use it for photographic or illustrative pictures — route those to an
image-generation skill (e.g. dashscope-image-gen, minimax-image-gen).

## Mandatory Style Rules

These are non-negotiable. Violating them produces off-brand or unrendered diagrams.

1. **Every diagram MUST start with a style header.** A style header is a
   `%%{init}%%` directive plus five `classDef`s, copied verbatim from
   `references/styles.md`. This matters because the chat's global Mermaid theme is
   hardcoded to dark; the `%%{init}%%` header overrides it per diagram. Default to
   the `brand-light` style unless the user asks for another (see **Styles** below).
2. **Color every node via the five `classDef`s, never with ad-hoc hex.** The class
   names — `agent` / `system` / `biz` / `warn` / `error` — are identical across all
   styles, so the diagram body never changes when the style does. Pick a node's
   class by its role: system/generic → `system`, knowledge/learning → `agent`,
   business/execution → `biz`, project-management/warning/decision → `warn`,
   error/failure → `error`.
3. **Use the semantic shapes below**, not arbitrary ones.
4. **Quote any node label that contains punctuation, parentheses, or `/`** to avoid
   Mermaid parse errors, e.g. `A["Query / Retrieve"]`.

## Styles

Six selectable visual styles live in `references/styles.md`; each is a
ready-to-paste header (`%%{init}%%` + five `classDef`s). Switching style swaps
only the header — the node/edge body stays the same.

| Style | Look | Good for |
|-------|------|----------|
| `brand-light` (default) | white canvas, DesireCore 3+2 accents | blogs, slides, docs |
| `brand-dark` | near-black canvas, 3+2 accents | matches the app's dark mode |
| `terminal` | `#0f0f1a`, neon accents, monospace | GitHub / dev articles |
| `blueprint` | deep-blue canvas, cyan/white, monospace | architecture specs |
| `cream` | warm cream canvas, clay/sage/plum | Anthropic-flavored decks |
| `mono` | pure white, grayscale | Notion / wiki |

Pick by the user's words ("暗色/dark", "蓝图/blueprint", "奶油/cream",
"极简/mono", "极客/terminal", or "风格 N / style N"); otherwise use `brand-light`.
Diagrams are user-facing artifacts, so the non-`brand-*` palettes intentionally
step outside the app's 3+2 color rule (which governs product UI, not exported
diagrams). Each preset is internally consistent.

## Semantic Vocabulary

Shape carries meaning (see `references/semantic-vocabulary.md` for the full table):

Class colors vary by style; only the role-to-class mapping is fixed.

| Concept | Mermaid shape | classDef |
|---------|---------------|----------|
| Agent / 智能体 | hexagon `id{{...}}` | agent |
| DesireCore core / system | rounded `id(...)` | system |
| LLM / model | rounded `id(⚡ ...)` | system |
| Business / execution node | rect `id[...]` | biz |
| Memory / store | cylinder `id[(...)]` | system |
| User | stadium `id([...])` | biz |
| Decision / branch | diamond `id{...}` | warn |
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

Emit the diagram directly in your reply inside a fenced code block whose info
string is `mermaid` (open the fence with three backticks immediately followed by
the word mermaid). The chat renders it to SVG automatically; on a syntax error it
falls back to showing the raw code (the `mermaid-fallback` path), so the source
MUST be valid. Keep node labels short — long text breaks the layout.

## Common Mistakes

- ❌ Omitting the style header → the diagram inherits the global dark theme.
- ❌ Ad-hoc hex on nodes instead of the chosen style's five `classDef`s.
- ❌ Mixing two styles' headers in one diagram.
- ❌ Overlong node labels that overflow the layout.
- ❌ Unquoted labels with `()`, `/`, or CJK punctuation → Mermaid parse failure.
