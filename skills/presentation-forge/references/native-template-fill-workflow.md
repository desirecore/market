# 原生 PPTX 模板填充

当用户提供原生 `.pptx` 模板和新内容，并要求保留 PowerPoint 设计、直接填字时使用。本路线直接修改 OOXML；不经过整页生图、SVG 或元素重组。

## 能力边界

v1 支持：

- 分析原生文本框、占位符和表格单元格。
- 根据几何尺寸与字号估算文本容量。
- 选择、删除和重排源页面。
- 替换文本框和普通表格单元格文字。
- 为替换文字显式设置宋体等指定字体，并可选择作用于全部选中页面或同步主题字体。
- 保留源主题、版式、图片、图表、SmartArt、动画和页面切换的原始包部件。

v1 不支持：

- 重复克隆同一源页面。
- 替换图片、编辑图表数据、改写 SmartArt。
- 改写对象级动画。
- 自动缩小字体来容纳超长文字。

遇到不支持的需求时返回 `BLOCKED` 或保留原对象；不要宣称已经编辑。

## 固定目录

在统一 session 内使用：

```text
sources/source-template.pptx
analysis/slide-library.json
analysis/fill_plan.json
analysis/check_report.json
final/filled-deck.pptx
reports/native-template-validation.json
reports/quality-gate.json
```

## 1. 分析模板

```bash
python3 scripts/native_template_fill.py analyze \
  <session>/sources/source-template.pptx \
  --out <session>/analysis/slide-library.json
```

把 `slide-library.json` 当作版式库读取。按页面的文本框角色、几何尺寸、容量和原有修辞结构选择页面，不按源页面顺序机械替换。

## 2. 建立填充计划

```bash
python3 scripts/native_template_fill.py scaffold \
  <session>/analysis/slide-library.json \
  --slides 1,3,5 \
  --out <session>/analysis/fill_plan.json
```

在 `fill_plan.json` 中为每页填写：

- `purpose`：该页在目标故事中的作用。
- `layout_rationale`：为什么源版式适合这段内容，以及主要风险。
- `replacements`：使用分析结果中的精确 `slot_id` 和新文字。

需要指定字体时，在计划顶层加入：

```json
"font_policy": {
  "font_face": "宋体",
  "scope": "replaced-text"
}
```

`scope` 支持：

- `replaced-text`：只给本次替换的新文字显式设置字体，最适合保留模板设计。
- `all-selected-text`：给选中页面内全部中文 run 设置字体。
- `theme-and-replaced`：设置替换文字，并同步 Theme major/minor 的东亚字体；可能影响模板中继承主题字体的其他文字。

 substantive claim 必须来自用户材料。标题和短标签优先改写压缩，不默认缩小字号。

## 3. 容量与目标校验

```bash
python3 scripts/native_template_fill.py check-plan \
  <session>/analysis/slide-library.json \
  <session>/analysis/fill_plan.json \
  --out <session>/analysis/check_report.json
```

`error_count > 0` 时必须修复。`text_capacity` 是需要人工复核的警告；优先缩短、拆页或换版式。

## 4. 用户确认门

向用户展示目标页序、删除页面、内容到版式的映射和容量警告。只有用户确认后，才把计划顶层 `status` 从 `draft` 改为 `confirmed`。

不得使用调试参数绕过确认门。

## 5. 原生填充

```bash
python3 scripts/native_template_fill.py apply \
  <session>/sources/source-template.pptx \
  <session>/analysis/slide-library.json \
  <session>/analysis/fill_plan.json \
  --out <session>/final/filled-deck.pptx \
  --font 宋体 \
  --font-scope replaced-text
```

禁止覆盖源 PPTX。脚本会保留源包并修改页面顺序与目标文本节点。

## 6. 回读与统一质量门

```bash
python3 scripts/native_template_fill.py validate \
  <session>/final/filled-deck.pptx \
  <session>/analysis/fill_plan.json \
  --out <session>/reports/native-template-validation.json

python3 scripts/validate_ooxml_namespaces.py \
  <session>/final/filled-deck.pptx \
  --out <session>/reports/ooxml-namespace-validation.json

python3 scripts/run_quality_gate.py \
  --session <session> \
  --artifact <session>/final/filled-deck.pptx
```

只有 `reports/quality-gate.json.status=PASS` 才能宣称正式完成。视觉渲染仍按 `scripts/render_pptx.py` 的 PowerPoint/LibreOffice 等级执行；回读通过不等于视觉溢出已人工确认。

禁止使用 `xml.etree.ElementTree` round-trip 模板中的 slide、presentation、theme 或 layout XML。它会把 `p14`、`a14` 等命名空间改成 `ns*`，但不会同步 `mc:Choice Requires` 等属性值，PowerPoint 会提示修复文件。统一质量门必须检查这些兼容性前缀。
