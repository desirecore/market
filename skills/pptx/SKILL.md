---
name: 演示文稿处理
description: >-
  Use this skill any time a .pptx file is involved in any way — as input,
  output, or both. This includes: creating slide decks, pitch decks, or
  presentations; reading, parsing, or extracting text from any .pptx file (even
  if the extracted content will be used elsewhere, like in an email or summary);
  editing, modifying, or updating existing presentations; combining or splitting
  slide files; working with templates, layouts, speaker notes, or comments.
  Trigger whenever the user mentions "deck," "slides," "presentation," or
  references a .pptx filename, regardless of what they plan to do with the
  content afterward. If a .pptx file needs to be opened, created, or touched,
  use this skill. Use when 用户提到 PPT、演示文稿、幻灯片、演讲稿、汇报材料、
  pptx、创建演示、编辑幻灯片。
version: 1.0.1
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
tags:
  - pptx
  - powerpoint
  - slides
  - presentation
  - office
metadata:
  author: anthropic
  updated_at: '2026-04-13'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="pp-a" x1="2" y1="3" x2="22"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#FF9500"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><rect x="2" y="3"
    width="20" height="15" rx="2" fill="url(#pp-a)" fill-opacity="0.1"
    stroke="url(#pp-a)" stroke-width="1.5"/><path d="M12 18v3M8 21h8"
    stroke="url(#pp-a)" stroke-width="1.5" stroke-linecap="round"/><rect
    x="5" y="6.5" width="5.5" height="1.5" rx="0.5" fill="url(#pp-a)"
    fill-opacity="0.4"/><path d="M5 10h9M5 12.5h6" stroke="url(#pp-a)"
    stroke-width="1.2" stroke-linecap="round"/><circle cx="17" cy="10" r="3"
    fill="#FF9500" fill-opacity="0.15"/><path d="M15.8 8.5v3l2.6-1.5z"
    fill="#FF9500" fill-opacity="0.85"/></svg>
  short_desc: 创建、编辑和处理 PowerPoint 演示文稿（.pptx）
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# pptx 技能

## L0：一句话摘要

创建、编辑和处理 PowerPoint 演示文稿（.pptx），支持模板编辑和从零创建。

## L1：概述与使用场景

### 能力描述

pptx 是一个**流程型技能（Procedural Skill）**，提供 PowerPoint 演示文稿的完整处理能力。支持通过 pptxgenjs（Node.js）从零创建演示文稿，通过解包 XML 编辑现有模板，以及内容提取和视觉质检。

### 使用场景

- 用户需要创建新的演示文稿（汇报材料、Pitch Deck 等）
- 用户需要编辑或修改现有 .pptx 文件
- 用户需要从 .pptx 文件中提取文本内容
- 用户需要将演示文稿转换为 PDF 或图片

## L2：详细规范

## Prerequisites

### Python 3（必需 — 读取和编辑现有 PPTX 时需要）

在执行任何 Python 脚本之前，先检测 Python 是否可用：

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

如果命令失败（Python 不可用），**必须停止并告知用户安装 Python 3**：

- **macOS**: `brew install python3` 或从 https://www.python.org/downloads/ 下载
- **Windows**: `winget install Python.Python.3` 或从 python.org 下载（安装时勾选 "Add Python to PATH"）
- **Linux (Debian/Ubuntu)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora/RHEL)**: `sudo dnf install python3 python3-pip`

注意：从零创建 PPTX 使用 pptxgenjs（Node.js），不需要 Python。

如需更详细的环境配置帮助，加载 `environment-setup` 技能。

### Python 包依赖

本技能的 Python 操作依赖以下包（按需检测）：

- `markitdown[pptx]` — PPTX 内容读取
- `Pillow` — 缩略图生成

检测方法：
```bash
python3 -c "import markitdown; import PIL" 2>/dev/null || echo "MISSING"
```

缺失时告知用户安装：`pip install "markitdown[pptx]" Pillow`

## Output Rule

When you create or modify a .pptx file, you **MUST** tell the user the absolute path of the output file in your response. Example: "文件已保存到：`/path/to/output.pptx`"

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE DELEGATE TOOL** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Delegated agents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
