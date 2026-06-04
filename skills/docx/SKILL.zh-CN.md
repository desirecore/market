<!-- locale: zh-CN -->

# docx 技能

## L0：一句话摘要

创建、编辑和处理 Word 文档（.docx），支持新建、修改 XML、格式校验全流程。

## L1：概述与使用场景

### 能力描述

docx 是一个**流程型技能（Procedural Skill）**，提供 Word 文档的完整处理能力。支持通过 docx-js（Node.js）创建新文档，通过解包 XML 编辑现有文档，以及格式验证和 PDF 转换。

### 使用场景

- 用户需要创建新的 Word 文档（报告、备忘录、合同、信函等）
- 用户需要编辑现有 .docx 文件（修改内容、添加批注、跟踪修改）
- 用户需要从 .docx 文件中提取文本或表格数据
- 用户需要进行文档格式转换（.doc → .docx、.docx → PDF）

## L2：详细规范

### 脚本路径规则（强制）

本技能自带的 Python 脚本位于技能安装目录内。执行时**必须使用完整路径**，不能使用相对路径。

技能目录由上下文中的 `<skill-dir>` 标签提供。**所有 office Python 脚本都必须通过跨平台启动器** `scripts/with-deps.py` 运行，从而复用运行时预装的库（`defusedxml`，以及完整校验用的 `lxml`），无需 `pip install`。该启动器是纯 Python，在 **macOS / Linux / Windows 上行为一致——不依赖 `bash`**：

```bash
python "<skill-dir>/scripts/with-deps.py" office/unpack.py document.docx unpacked/
python "<skill-dir>/scripts/with-deps.py" office/pack.py unpacked/ output.docx
```

启动器会把目标脚本放到运行时自带、预装了 `lxml`/`defusedxml` 的 Python 下运行（若该自带 Python 不可用则回退系统 `python3`，此时完整 XSD 校验会被优雅跳过）。脚本路径**相对 `scripts/`**（如 `office/unpack.py`、`comment.py`）。

**禁止**用裸相对路径执行 office 脚本（如 `python scripts/office/unpack.py`）——该路径在用户工作目录下不存在，且会绕过预装的库。一律通过 `<skill-dir>/scripts/with-deps.py` 运行。

## Prerequisites

### Python 3（必需）

在执行任何 Python 脚本之前，先检测 Python 是否可用：

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

如果命令失败（Python 不可用），**必须停止并告知用户安装 Python 3**：

- **macOS**: `brew install python3` 或从 https://www.python.org/downloads/ 下载
- **Windows**: `winget install Python.Python.3` 或从 python.org 下载（安装时勾选 "Add Python to PATH"）
- **Linux (Debian/Ubuntu)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora/RHEL)**: `sudo dnf install python3 python3-pip`

如需更详细的环境配置帮助：Python 相关问题加载 `python-runtime` 技能；
其他（容器 / WSL / 系统工具）加载 `dev-environment-setup` 技能。

### Python 包依赖

本技能的 Python 脚本依赖 `defusedxml`（XML 解析）和 `lxml`（XSD 校验）。**两者均由运行时预装** —— 通过 `scripts/with-deps.py` 运行脚本时，目标会在运行时自带、已装好两者的 Python 下运行，因此**无需 `pip install`、无需联网**（离线可用，全平台、不依赖 `bash`）。

回退：若运行时自带 Python 不可用（老客户端 / 构建未烤入），启动器回退系统 `python3`。此时 `defusedxml` 仍可解析（纯 Python、单独预装），但 `lxml` 可能缺失 —— 完整 XSD 校验会被**优雅跳过**（编辑/打包仍成功）。要在该回退情形下启用完整校验：`pip install lxml`。

## Output Rule

When you create or modify a .docx file, you **MUST** tell the user the absolute path of the output file in your response. Example: "文件已保存到：`/path/to/output.docx`"

## Overview

A .docx file is a ZIP archive containing XML files.

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `pandoc` or unpack for raw XML |
| Create new document | Use `docx-js` - see Creating New Documents below |
| Edit existing document | Unpack → edit XML → repack - see Editing Existing Documents below |

### Converting .doc to .docx

Legacy `.doc` files must be converted before editing:

```bash
python "<skill-dir>/scripts/with-deps.py" office/soffice.py --headless --convert-to docx document.doc
```

### Reading Content

```bash
# Text extraction with tracked changes
pandoc --track-changes=all document.docx -o output.md

# Raw XML access
python "<skill-dir>/scripts/with-deps.py" office/unpack.py document.docx unpacked/
```

### Converting to Images

```bash
python "<skill-dir>/scripts/with-deps.py" office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### Accepting Tracked Changes

To produce a clean document with all tracked changes accepted (requires LibreOffice):

```bash
python "<skill-dir>/scripts/with-deps.py" accept_changes.py input.docx output.docx
```

---

## Creating New Documents

Generate .docx files with JavaScript, then validate. The `docx` (docx-js) library is **pre-installed by the runtime** — no `npm install` needed. You MUST run the generator through the Node preloader (`scripts/preload-deps.cjs`, see Run below) so `require('docx')` resolves the pre-installed library.

### 编写脚本（关键 —— 避免引号/转义导致失败）

**必须用 `Write` 工具创建 `generate.js`——直接把文件写出来。**

**禁止**通过 shell 拼脚本：不要用 `bash` heredoc（`cat <<EOF`）、`echo` 或 `python3 -c "...open(...).write(...)"` 来生成 JavaScript。文档内容（尤其手册/报告）含大量 `"` 引号、撇号、中文标点；经 shell 会导致三层引号互相冲突（shell 引号 × JS 字符串引号 × heredoc 分隔符），脚本被破坏，进而陷入反复重试和命令超时。

- 用 `Write` 工具 → 内容里的引号原样写入，完全无需 shell 转义。
- 长文档把内容作为普通 JS 字符串/数组放进文件，拆成多个 `Paragraph`；单个文档很大时，分**多次较小的 `Write`/`Edit`** 写入，不要塞进一条巨大命令。

### Setup
用 **Write 工具**把生成脚本写成文件（例如 `generate.js`）：
```javascript
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');

const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer));
```

### Run
Run it with the cross-platform Node preloader (it injects `NODE_PATH` for the pre-installed `docx`; pure Node, works on **macOS / Linux / Windows**, no `bash` needed):
```bash
node -r "<skill-dir>/scripts/preload-deps.cjs" generate.js
```
**Use CommonJS `require('docx')`, NOT ESM `import`** — the pre-installed library is resolved via `NODE_PATH`, which Node **ignores for ESM**. Do not put a `"type": "module"` `package.json` in the working directory either, as it would force `.js` files to be treated as ESM and break `require`. If `require('docx')` still fails (e.g. the runtime pre-install is unavailable on an older client), fall back to `npm install -g docx` and re-run.

### Validation
After creating the file, validate it. If validation fails, unpack, fix the XML, and repack.
```bash
python "<skill-dir>/scripts/with-deps.py" office/validate.py doc.docx
```

### Page Size

```javascript
// CRITICAL: docx-js defaults to A4, not US Letter
// Always set page size explicitly for consistent results
sections: [{
  properties: {
    page: {
      size: {
        width: 12240,   // 8.5 inches in DXA
        height: 15840   // 11 inches in DXA
      },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins
    }
  },
  children: [/* content */]
}]
```

**Common page sizes (DXA units, 1440 DXA = 1 inch):**

| Paper | Width | Height | Content Width (1" margins) |
|-------|-------|--------|---------------------------|
| US Letter | 12,240 | 15,840 | 9,360 |
| A4 (default) | 11,906 | 16,838 | 9,026 |

**Landscape orientation:** docx-js swaps width/height internally, so pass portrait dimensions and let it handle the swap:
```javascript
size: {
  width: 12240,   // Pass SHORT edge as width
  height: 15840,  // Pass LONG edge as height
  orientation: PageOrientation.LANDSCAPE  // docx-js swaps them in the XML
},
// Content width = 15840 - left margin - right margin (uses the long edge)
```

### Styles (Override Built-in Headings)

Use Arial as the default font (universally supported). Keep titles black for readability.

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt default
    paragraphStyles: [
      // IMPORTANT: Use exact IDs to override built-in styles
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // outlineLevel required for TOC
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Title")] }),
    ]
  }]
});
```

### Lists (NEVER use unicode bullets)

```javascript
// ❌ WRONG - never manually insert bullet characters
new Paragraph({ children: [new TextRun("• Item")] })  // BAD
new Paragraph({ children: [new TextRun("\u2022 Item")] })  // BAD

// ✅ CORRECT - use numbering config with LevelFormat.BULLET
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 },
        children: [new TextRun("Numbered item")] }),
    ]
  }]
});

// ⚠️ Each reference creates INDEPENDENT numbering
// Same reference = continues (1,2,3 then 4,5,6)
// Different reference = restarts (1,2,3 then 1,2,3)
```

### Tables

**CRITICAL: Tables need dual widths** - set both `columnWidths` on the table AND `width` on each cell. Without both, tables render incorrectly on some platforms.

```javascript
// CRITICAL: Always set table width for consistent rendering
// CRITICAL: Use ShadingType.CLEAR (not SOLID) to prevent black backgrounds
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 9360, type: WidthType.DXA }, // Always use DXA (percentages break in Google Docs)
  columnWidths: [4680, 4680], // Must sum to table width (DXA: 1440 = 1 inch)
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA }, // Also set on each cell
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, // CLEAR not SOLID
          margins: { top: 80, bottom: 80, left: 120, right: 120 }, // Cell padding (internal, not added to width)
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

**Table width calculation:**

Always use `WidthType.DXA` — `WidthType.PERCENTAGE` breaks in Google Docs.

```javascript
// Table width = sum of columnWidths = content width
// US Letter with 1" margins: 12240 - 2880 = 9360 DXA
width: { size: 9360, type: WidthType.DXA },
columnWidths: [7000, 2360]  // Must sum to table width
```

**Width rules:**
- **Always use `WidthType.DXA`** — never `WidthType.PERCENTAGE` (incompatible with Google Docs)
- Table width must equal the sum of `columnWidths`
- Cell `width` must match corresponding `columnWidth`
- Cell `margins` are internal padding - they reduce content area, not add to cell width
- For full-width tables: use content width (page width minus left and right margins)

### Images

```javascript
// CRITICAL: type parameter is REQUIRED
new Paragraph({
  children: [new ImageRun({
    type: "png", // Required: png, jpg, jpeg, gif, bmp, svg
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Title", description: "Desc", name: "Name" } // All three required
  })]
})
```

### Page Breaks

```javascript
// CRITICAL: PageBreak must be inside a Paragraph
new Paragraph({ children: [new PageBreak()] })

// Or use pageBreakBefore
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### Table of Contents

```javascript
// CRITICAL: Headings must use HeadingLevel ONLY - no custom styles
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })
```

### Headers/Footers

```javascript
sections: [{
  properties: {
    page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } // 1440 = 1 inch
  },
  headers: {
    default: new Header({ children: [new Paragraph({ children: [new TextRun("Header")] })] })
  },
  footers: {
    default: new Footer({ children: [new Paragraph({
      children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
    })] })
  },
  children: [/* content */]
}]
```

### Critical Rules for docx-js

- **Set page size explicitly** - docx-js defaults to A4; use US Letter (12240 x 15840 DXA) for US documents
- **Landscape: pass portrait dimensions** - docx-js swaps width/height internally; pass short edge as `width`, long edge as `height`, and set `orientation: PageOrientation.LANDSCAPE`
- **Never use `\n`** - use separate Paragraph elements
- **Never use unicode bullets** - use `LevelFormat.BULLET` with numbering config
- **PageBreak must be in Paragraph** - standalone creates invalid XML
- **ImageRun requires `type`** - always specify png/jpg/etc
- **Always set table `width` with DXA** - never use `WidthType.PERCENTAGE` (breaks in Google Docs)
- **Tables need dual widths** - `columnWidths` array AND cell `width`, both must match
- **Table width = sum of columnWidths** - for DXA, ensure they add up exactly
- **Always add cell margins** - use `margins: { top: 80, bottom: 80, left: 120, right: 120 }` for readable padding
- **Use `ShadingType.CLEAR`** - never SOLID for table shading
- **TOC requires HeadingLevel only** - no custom styles on heading paragraphs
- **Override built-in styles** - use exact IDs: "Heading1", "Heading2", etc.
- **Include `outlineLevel`** - required for TOC (0 for H1, 1 for H2, etc.)

---

## Editing Existing Documents

**Follow all 3 steps in order.**

### Step 1: Unpack
```bash
python "<skill-dir>/scripts/with-deps.py" office/unpack.py document.docx unpacked/
```
Extracts XML, pretty-prints, merges adjacent runs, and converts smart quotes to XML entities (`&#x201C;` etc.) so they survive editing. Use `--merge-runs false` to skip run merging.

### Step 2: Edit XML

Edit files in `unpacked/word/`. See XML Reference below for patterns.

**Use "Claude" as the author** for tracked changes and comments, unless the user explicitly requests use of a different name.

**Use the Edit tool directly for string replacement. Do not write Python scripts.** Scripts introduce unnecessary complexity. The Edit tool shows exactly what is being replaced.

**CRITICAL: Use smart quotes for new content.** When adding text with apostrophes or quotes, use XML entities to produce smart quotes:
```xml
<!-- Use these entities for professional typography -->
<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>
```
| Entity | Character |
|--------|-----------|
| `&#x2018;` | ‘ (left single) |
| `&#x2019;` | ’ (right single / apostrophe) |
| `&#x201C;` | “ (left double) |
| `&#x201D;` | ” (right double) |

**Adding comments:** Use `comment.py` to handle boilerplate across multiple XML files (text must be pre-escaped XML):
```bash
python "<skill-dir>/scripts/with-deps.py" comment.py unpacked/ 0 "Comment text with &amp; and &#x2019;"
python "<skill-dir>/scripts/with-deps.py" comment.py unpacked/ 1 "Reply text" --parent 0  # reply to comment 0
python "<skill-dir>/scripts/with-deps.py" comment.py unpacked/ 0 "Text" --author "Custom Author"  # custom author name
```
Then add markers to document.xml (see Comments in XML Reference).

### Step 3: Pack
```bash
python "<skill-dir>/scripts/with-deps.py" office/pack.py unpacked/ output.docx --original document.docx
```
Validates with auto-repair, condenses XML, and creates DOCX. Use `--validate false` to skip.

**Auto-repair will fix:**
- `durableId` >= 0x7FFFFFFF (regenerates valid ID)
- Missing `xml:space="preserve"` on `<w:t>` with whitespace

**Auto-repair won't fix:**
- Malformed XML, invalid element nesting, missing relationships, schema violations

### Common Pitfalls

- **Replace entire `<w:r>` elements**: When adding tracked changes, replace the whole `<w:r>...</w:r>` block with `<w:del>...<w:ins>...` as siblings. Don't inject tracked change tags inside a run.
- **Preserve `<w:rPr>` formatting**: Copy the original run's `<w:rPr>` block into your tracked change runs to maintain bold, font size, etc.

---

## XML Reference

### Schema Compliance

- **Element order in `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- **Whitespace**: Add `xml:space="preserve"` to `<w:t>` with leading/trailing spaces
- **RSIDs**: Must be 8-digit hex (e.g., `00AB1234`)

### Tracked Changes

**Insertion:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

**Deletion:**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**Inside `<w:del>`**: Use `<w:delText>` instead of `<w:t>`, and `<w:delInstrText>` instead of `<w:instrText>`.

**Minimal edits** - only mark what changes:
```xml
<!-- Change "30 days" to "60 days" -->
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Claude" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Claude" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

**Deleting entire paragraphs/list items** - when removing ALL content from a paragraph, also mark the paragraph mark as deleted so it merges with the next paragraph. Add `<w:del/>` inside `<w:pPr><w:rPr>`:
```xml
<w:p>
  <w:pPr>
    <w:numPr>...</w:numPr>  <!-- list numbering if present -->
    <w:rPr>
      <w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>Entire paragraph content being deleted...</w:delText></w:r>
  </w:del>
</w:p>
```
Without the `<w:del/>` in `<w:pPr><w:rPr>`, accepting changes leaves an empty paragraph/list item.

**Rejecting another author's insertion** - nest deletion inside their insertion:
```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Claude" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

**Restoring another author's deletion** - add insertion after (don't modify their deletion):
```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

### Comments

After running `comment.py` (see Step 2), add markers to document.xml. For replies, use `--parent` flag and nest markers inside the parent's.

**CRITICAL: `<w:commentRangeStart>` and `<w:commentRangeEnd>` are siblings of `<w:r>`, never inside `<w:r>`.**

```xml
<!-- Comment markers are direct children of w:p, never inside w:r -->
<w:commentRangeStart w:id="0"/>
<w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted</w:delText></w:r>
</w:del>
<w:r><w:t> more text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>

<!-- Comment 0 with reply 1 nested inside -->
<w:commentRangeStart w:id="0"/>
  <w:commentRangeStart w:id="1"/>
  <w:r><w:t>text</w:t></w:r>
  <w:commentRangeEnd w:id="1"/>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="1"/></w:r>
```

### Images

1. Add image file to `word/media/`
2. Add relationship to `word/_rels/document.xml.rels`:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. Add content type to `[Content_Types].xml`:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. Reference in document.xml:
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>  <!-- EMUs: 914400 = 1 inch -->
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

---

## Dependencies

运行时预装（免安装、离线、跨平台 —— 下列启动器都不需要 `bash`）：

- **docx** (docx-js): 新建文档 —— **由运行时预装**（`runtime-deps/node_modules`）；生成器通过 `node -r "<skill-dir>/scripts/preload-deps.cjs" generate.js` 运行，无需 `npm install`。
- **defusedxml** + **lxml**: XML 解析与完整 XSD 校验 —— **由运行时预装**在自带 Python 中（`runtime-deps/python-runtime`）；脚本通过 `python "<skill-dir>/scripts/with-deps.py" <脚本> ...` 运行即可离线使用。自带 Python / `lxml` 不可用时回退系统 `python3`，并优雅跳过 XSD 校验。

外部系统工具（仅读取/转换需要，**生成不需要**；如使用请按平台安装）：

- **pandoc**: 文本提取。macOS `brew install pandoc` · Windows `winget install --id JohnMacFarlane.Pandoc` · Linux `sudo apt install pandoc`
- **LibreOffice**（`soffice`）: `.doc`→`.docx`、PDF 转换、接受修订。macOS `brew install --cask libreoffice` · Windows `winget install --id TheDocumentFoundation.LibreOffice`（确保 `soffice` 在 `PATH`）· Linux `sudo apt install libreoffice`。`scripts/office/soffice.py` 里的 Linux 沙箱 `AF_UNIX` shim 在 macOS/Windows 上会自动跳过。
- **Poppler**（`pdftoppm`，页→图片）: macOS `brew install poppler` · Windows `winget install --id oschwartz10612.Poppler` 或 `choco install poppler` · Linux `sudo apt install poppler-utils`
