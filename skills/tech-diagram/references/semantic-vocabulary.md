# Semantic Vocabulary (语义词汇表)

The full mapping from concept → Mermaid shape → DesireCore 3+2 class. Shape and
color encode meaning, so a reader understands a diagram without a legend.

## The brand header (paste verbatim as the first line of every diagram)

```
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
```

## The 5 color classes (the only allowed palette)

```
classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
classDef biz    fill:#F0FDF4,stroke:#34C759,color:#1d1d1f
classDef warn   fill:#FFFBF0,stroke:#FF9500,color:#1d1d1f
classDef error  fill:#FFF0F0,stroke:#FF3B30,color:#1d1d1f
```

`fill` = `cardBgColors`, `stroke` = the 3+2 accent, `color` = `systemColors.label`
(`#1d1d1f`). Source of truth: `app/theme/tokens/index.ts`,
`app/theme/presets/agent-colors.ts`.

### Class selection rule (mirrors agent-colors.ts)

| Domain | Class | Accent |
|--------|-------|--------|
| System / generic (DesireCore core, infra, LLM) | system | blue `#007AFF` |
| Knowledge / learning (legal, writer, memory) | agent / system | purple `#AF52DE` |
| Business / execution (data, real-estate, code) | biz | green `#34C759` |
| Project management / warning / decision | warn | orange `#FF9500` |
| Error / failure | error | red `#FF3B30` |

Decorative-only colors `yellow #FFCC00` and `teal #5AC8FA` are for background
gradients elsewhere in the product — never use them in diagrams.

## Shape table

| Concept | Mermaid syntax | Class | Note |
|---------|----------------|-------|------|
| Agent / sub-agent | `id{{Name}}` (hexagon) | agent | the signature shape for an autonomous agent |
| DesireCore core / orchestrator | `id(Name)` (rounded) | system | central coordinator |
| LLM / model | `id(⚡ Model)` (rounded + ⚡) | system | ⚡ prefix marks an LLM call |
| Service / tool / skill | `id[Name]` (rect) | biz | a callable capability |
| Business / execution step | `id[Step]` (rect) | biz | a unit of work |
| Memory / store / DB | `id[(Store)]` (cylinder) | system | persistent state |
| User / external actor | `id([User])` (stadium) | biz | the human |
| Decision / branch | `id{Choice?}` (diamond) | warn | a fork in control flow |
| External service | `subgraph Ext [External]` ... `end` + `style Ext stroke-dasharray:4 3` | — | dashed boundary = outside the system |

## Arrow / flow encoding

| Flow type | Edge syntax | Meaning |
|-----------|-------------|---------|
| Primary data flow | `A --> B` | the main path |
| Memory write / persistence | `A -.-> B` | dotted = side-effect write |
| Async event | `A -.->|async| B` | dotted + label |
| Feedback / retry | `B --> A` (back-edge) | loop |
| Hierarchy / containment | `A --o B` | circle edge |
| Hard stop / escalation | `A --x B` | cross edge |
| Co-participation (equal peers) | `A === B` | thick link |

## Diagram-type cheatsheet

| User intent | Mermaid header |
|-------------|----------------|
| Architecture / data flow | `flowchart TD` or `flowchart LR` |
| Sequence / interaction over time | `sequenceDiagram` |
| State machine | `stateDiagram-v2` |
| ER / data model | `erDiagram` |
| Class / type model | `classDiagram` |
| Mind map | `mindmap` |

For `sequenceDiagram`, `classDiagram`, etc. that do not support `classDef`, still
keep the `%%{init}%%` brand header so the theme stays light and on-brand.
