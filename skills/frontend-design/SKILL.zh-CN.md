<!-- locale: zh-CN -->

# frontend-design 技能

## L0：一句话摘要

创建有品味、避免 AI 烂大街审美的高质量前端界面与组件。

## L1：概述与使用场景

### 能力描述

frontend-design 是一个**流程型技能（Procedural Skill）**，引导创建独特、生产级的前端界面，避免千篇一律的 AI 生成审美。输出真实可运行的代码，注重美学细节和创意选择。

### 使用场景

- 用户需要创建网页组件、页面或应用（Landing Page、仪表盘、React 组件等）
- 用户需要为现有 Web UI 进行样式美化
- 用户需要创建海报、视觉设计等前端产出物

### 核心价值

- **反 AI 审美**：拒绝 Inter 字体 + 紫色渐变的烂大街风格
- **设计思维驱动**：先确定美学方向，再编写代码
- **生产级质量**：输出可直接使用的完整代码

## L2：详细规范

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
