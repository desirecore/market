---
name: 前端设计
description: >-
  Create distinctive, production-grade frontend interfaces with high design
  quality. Use this skill when the user asks to build web components, pages,
  artifacts, posters, or applications (examples include websites, landing pages,
  dashboards, React components, HTML/CSS layouts, or when styling/beautifying
  any web UI). Generates creative, polished code and UI design that avoids
  generic AI aesthetics. Use when 用户提到 前端设计、网页设计、UI 设计、
  界面设计、组件、海报、Landing Page、落地页、React 组件、Vue 组件、
  CSS 样式、美化界面、设计一个、做一个网页、官网、仪表盘、Dashboard。
license: Complete terms in LICENSE.txt
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
tags:
  - frontend
  - design
  - ui
  - css
  - react
  - html
metadata:
  author: anthropic
  updated_at: '2026-04-07'
market:
  short_desc: 创建有品味、避免 AI 烂大街审美的前端界面与组件
  category: design
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Output Rule

When you create or modify HTML/CSS/JS/React/Vue files, you **MUST** tell the user the absolute path of the output file in your response. Example: "文件已保存到：`/path/to/index.html`"

If you create multiple files (e.g. HTML + CSS + JS), list each path explicitly.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

---

## Project Context Override (DesireCore Specific)

> **Note**: When working **inside the DesireCore main repository** (`desirecore-9` or any project that has `app/styles/globals.css` with the DesireCore 3+2 token system), the project's strict design system **OVERRIDES** the bold aesthetic guidance above. In that context:
>
> - Use only the 3 functional colors (Green / Blue / Purple) + 2 status colors (Orange / Red) defined in `globals.css`
> - Reference design tokens via CSS variables (`var(--accent-green)`, etc.) — never hardcoded hex
> - Follow the typography, radius, and spacing tokens already defined
> - The "avoid generic AI aesthetics" principle still applies, but expression happens through layout/composition/motion, not color expansion
>
> For **standalone artifacts, posters, landing pages, or external projects**, the full aesthetic freedom of this skill applies — go bold.
