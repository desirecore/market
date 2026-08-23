# Markdown 画布与原生 PPTX 工作流

从主题或文档新建演示时默认使用本规范。只有用户明确要求直接导出、不要画布或跳过预览时，才改用 `slides-plan + direct-build`。

## 单一事实源

`slides.md` 是人工编辑的内容源；`analysis/native_deck_spec.json` 与 `scenes/*.scene.json` 都是派生产物。画布读取 scene，PPTX 构建器也读取同一 scene。禁止让 HTML/CSS 和 PPTX 构建器分别计算布局。

```text
slides.md
-> compile_slides_markdown.py
-> native_deck_spec.json + scenes/
-> editor manifest + SVG/DOM scene canvas
-> editor patch 回写 spec、scene 和 slides.md
-> approve-export
-> build_native_editable_deck.py --scene-dir
-> PPTX / PDF
```

## 初始化

```bash
python scripts/init_deck_session.py \
  --title "企业 AI 知识库解决方案" \
  --delivery-type editable-pptx \
  --style-id consulting-blue-white \
  --editor-workflow-mode canvas-first \
  --authoring-mode markdown-canvas \
  --out-root ./outputs
```

初始化会创建 `slides.md`。不要同时手工维护 `slides_plan.md`；编译器会从 `slides.md` 重建逐页计划和 prompts。

## Markdown 语法

- YAML frontmatter：`title`、`style`、`variant`、`ratio`、`fontCN`、`visualAssetPolicy`。
- 使用单独一行 `---` 分隔页面。
- 每页第一个 `#` 是页面标题。
- `>` 是副标题或页面关键信息。
- `::layout{type="..."}` 选择版式。
- `##` 与其后的正文构成卡片、步骤、对比区或架构层。
- 普通 `-` 列表用于行动项或普通内容。
- Markdown 表格用于 `table` 页面。

支持的布局映射：

| Markdown layout | 原生 archetype |
|---|---|
| `cover`、`cover-left` | `cover` |
| `content`、`cards`、`columns` | `content-structured` |
| `timeline`、`process` | `process-flow` |
| `comparison` | `comparison-two-zone` |
| `data`、`metrics` | `data-callouts` |
| `table` | `table` |
| `architecture` | `architecture` |
| `closing`、`action` | `closing-action` |

不在语法内的任意 CSS、HTML、JavaScript 和浏览器滤镜不得进入生产画布。需要绝对定位时，通过 scene element 的稳定 ID 和 `bbox` 覆盖，不把像素坐标写进正文。

## 编译并打开画布

```bash
python scripts/compile_slides_markdown.py \
  --session <session> \
  --build-preview \
  --render-canvas
```

该命令：

1. 解析 `slides.md`；
2. 写入原生 deck spec、逐页计划、prompts 和完整 scene 集合；
3. 只在 `cache/editable/preview.pptx` 构建结构预览；
4. 将预览中的原生对象同步为 scene element；
5. 导出 editor manifest；
6. 生成 `reports/editor-canvas.html`。

对话中必须展示生成的 HTML 画布，不得手写静态 4 页示意。用户要求 N 页时，Markdown 页面数、spec、scene、manifest、画布缩略图和最终 PPTX 都必须为 N 页。

画布必须以可读编辑为首要布局目标：默认收起右侧检查器，让当前页面占据主要可用区域；页面不得小于约 `746×420` CSS 像素，空间不足时允许主区域滚动，不能继续缩小到文字不可读。顶部提供页面列表、对象编辑和专注画布按钮；点击页面中的文字对象时，展开约 `320px` 宽的对象属性栏。Markdown 仍作为内部内容源和导出回写数据，但不在画布界面暴露按钮、标签页或编辑框。样式预设不得永久占据主画布空间，应放在可收起检查器中。

## 修改与回写

- 用户直接编辑 `slides.md`：重新运行编译命令。
- 用户在画布改字或对象样式：使用 `editor_bridge.py apply`；桥接器更新 spec 和 scene，并把受支持内容规范化回写 `slides.md`。
- 用户拖动对象：只更新 scene `bbox`；Markdown 保留内容和结构，几何覆盖留在 scene。
- 用户切换风格：同步 frontmatter、spec、scene、metadata 和 prompts。

画布中的 Markdown 面板用于内容修改。浏览器不能直接写本地文件时，导出动作必须把完整 `slides_markdown` 与完整 scene 状态一起提交给 Skill，再由 Skill 落盘、编译和构建。

## 导出

用户点击导出后：

```bash
python scripts/editor_bridge.py approve-export --session <session>
python scripts/build_native_editable_deck.py \
  --spec <session>/analysis/native_deck_spec.json \
  --scene-dir <session>/scenes \
  --session <session> \
  --out-pptx <session>/final/deck.pptx
```

随后执行字体、排版、可编辑性、最终 PowerPoint 渲染和统一质量门。不得在导出阶段重新选择模板或重新解释布局。

## v1 边界

- Markdown 负责内容、页面结构和组件；自由拖拽几何保存在 scene。
- 画布可以实时修改已有页面内容；在浏览器中新增或删除整页后，需要重新编译 Markdown。
- PPTX 与画布共享对象、文字、坐标、样式和层级，但浏览器与 PowerPoint 的字体抗锯齿可能存在轻微像素差异。
- 复杂 image-2 视觉仍是独立图片对象，其内部不可编辑。
