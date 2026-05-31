# Style Presets (风格预设)

Six style presets. A "style" = a `%%{init}%%` directive + five `classDef`s.
**The class names (`agent` / `system` / `biz` / `warn` / `error`) are identical
across all styles**, so switching styles means swapping only the header — the
diagram body (`:::agent`, `:::system`, …) never changes.

> **Flowchart vs. other diagram types.** Each preset below is a complete
> **flowchart** skeleton (`%%{init}%%` + `flowchart TD` + `classDef`s). Use it as
> follows:
> - **Flowchart / architecture / data-flow:** paste the whole block, then add nodes.
> - **sequenceDiagram / stateDiagram-v2 / erDiagram / classDiagram / mindmap:** copy
>   **only the first `%%{init}%%` line**, then write your diagram type. Those types
>   do **not** support `flowchart TD` or `classDef` — pasting the full block would
>   force a flowchart or mix incompatible declarations. The `%%{init}%%` line alone
>   still gives them the style's canvas color and font.

## How to pick a style

- **Default is `brand-light`.** Use it unless the user asks otherwise.
- The user selects a style by name or number: "暗色/dark", "极客/terminal",
  "蓝图/blueprint", "奶油/cream", "极简/mono", or "风格 N / style N".
- Diagrams are user-facing artifacts, so non-3+2 palettes are allowed here (this
  is a deliberate exception to the app's 3+2 color rule, which governs product UI,
  not exported diagrams). Each preset is internally consistent.
- Semantic shapes and arrow encoding (see `semantic-vocabulary.md`) stay the same
  in every style. `sequenceDiagram` / `classDiagram` etc. ignore `classDef`; keep
  the style's `%%{init}%%` header for a consistent canvas + font.

---

## 1. brand-light (默认 / blog · slides · docs)

```
%%{init: {'theme':'base','themeVariables':{'background':'#ffffff','primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','textColor':'#1d1d1f','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
    classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
    classDef biz    fill:#F0FDF4,stroke:#34C759,color:#1d1d1f
    classDef warn   fill:#FFFBF0,stroke:#FF9500,color:#1d1d1f
    classDef error  fill:#FFF0F0,stroke:#FF3B30,color:#1d1d1f
    %% nodes & edges here, e.g. A{{"Agent"}}:::agent --> B(["Core"]):::system
```

## 2. brand-dark (DesireCore 暗色模式一致)

Uses the app's `.dark` surface tokens (neutral-950 bg, light text) with the same
3+2 accents on dark card fills.

```
%%{init: {'theme':'base','themeVariables':{'background':'#0a0a0f','primaryColor':'#1C263A','primaryBorderColor':'#007AFF','primaryTextColor':'#f8f8fc','lineColor':'#8a8a92','textColor':'#f8f8fc','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent  fill:#261E34,stroke:#AF52DE,color:#f8f8fc
    classDef system fill:#1C263A,stroke:#007AFF,color:#f8f8fc
    classDef biz    fill:#1C2C24,stroke:#34C759,color:#f8f8fc
    classDef warn   fill:#3A2816,stroke:#FF9500,color:#f8f8fc
    classDef error  fill:#3A1E1E,stroke:#FF3B30,color:#f8f8fc
    %% nodes & edges here
```

## 3. terminal (极客暗黑 / GitHub · dev articles)

Near-black canvas, neon accents, monospace.

```
%%{init: {'theme':'base','themeVariables':{'background':'#0f0f1a','primaryColor':'#0E1726','primaryBorderColor':'#3BA0FF','primaryTextColor':'#d6f5e8','lineColor':'#00E5A0','textColor':'#d6f5e8','fontFamily':'SF Mono,JetBrains Mono,monospace'}}}%%
flowchart TD
    classDef agent  fill:#14111F,stroke:#B26BFF,color:#E6D6FF
    classDef system fill:#0E1726,stroke:#3BA0FF,color:#CFE8FF
    classDef biz    fill:#0E1F18,stroke:#00E5A0,color:#C9FFE8
    classDef warn   fill:#241A0E,stroke:#FFB000,color:#FFE8C0
    classDef error  fill:#241010,stroke:#FF4B5C,color:#FFD0D4
    %% nodes & edges here
```

## 4. blueprint (工程蓝图 / architecture specs)

Deep-blue canvas, cyan/white lines, monospace — engineering blueprint feel.

```
%%{init: {'theme':'base','themeVariables':{'background':'#0a1628','primaryColor':'#0E2A4A','primaryBorderColor':'#5AC8FA','primaryTextColor':'#E6F0FF','lineColor':'#5AC8FA','textColor':'#E6F0FF','fontFamily':'SF Mono,JetBrains Mono,monospace'}}}%%
flowchart TD
    classDef agent  fill:#10243F,stroke:#9AD0FF,color:#E6F0FF
    classDef system fill:#0E2A4A,stroke:#5AC8FA,color:#E6F0FF
    classDef biz    fill:#0E3344,stroke:#37D0E0,color:#E6F0FF
    classDef warn   fill:#2A2A12,stroke:#E0C04A,color:#FBF4D8
    classDef error  fill:#2A1420,stroke:#FF6B8A,color:#FFDDE6
    %% nodes & edges here
```

## 5. cream (暖奶油 / Anthropic-flavored)

Warm cream canvas, clay/sage/plum accents, humanist sans.

```
%%{init: {'theme':'base','themeVariables':{'background':'#f8f6f3','primaryColor':'#EDE7DF','primaryBorderColor':'#CC785C','primaryTextColor':'#2b2622','lineColor':'#8a7a6a','textColor':'#2b2622','fontFamily':'ui-sans-serif,-apple-system,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent  fill:#EFE6EC,stroke:#9C6B8E,color:#2b2622
    classDef system fill:#EDE7DF,stroke:#CC785C,color:#2b2622
    classDef biz    fill:#E9EDE4,stroke:#6E8B6E,color:#2b2622
    classDef warn   fill:#F3E6D0,stroke:#C9912E,color:#2b2622
    classDef error  fill:#F3DEDA,stroke:#B0504A,color:#2b2622
    %% nodes & edges here
```

## 6. mono (极简单色 / Notion · wiki)

Pure white, grayscale with stroke-shade distinction.

```
%%{init: {'theme':'base','themeVariables':{'background':'#ffffff','primaryColor':'#F4F4F5','primaryBorderColor':'#111111','primaryTextColor':'#111111','lineColor':'#999999','textColor':'#111111','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent  fill:#EDEDED,stroke:#333333,color:#111111
    classDef system fill:#F4F4F5,stroke:#111111,color:#111111
    classDef biz    fill:#FAFAFA,stroke:#555555,color:#111111
    classDef warn   fill:#F0F0F0,stroke:#777777,color:#111111,stroke-dasharray:4 3
    classDef error  fill:#EAEAEA,stroke:#000000,color:#111111,stroke-width:2px
    %% nodes & edges here
```
