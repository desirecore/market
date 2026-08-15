# 可视化 PPT 编辑器接入规范

当外部 UI 需要像 Codex 一样展示任务状态、页面预览并允许修改可编辑 PPTX 时使用本规范。Skill 是生成与验证后端；UI 是 adapter。两者只通过 editor manifest、patch 和事件文件交互，不让 UI 直接改 OOXML。

## 稳定 seam

UI 只依赖两个命令：

```bash
python scripts/editor_bridge.py export --session <session>
python scripts/editor_bridge.py apply --session <session> --patch <patch.json>
python scripts/editor_bridge.py approve-export --session <session>
```

`export` 写入 `reports/editor-manifest.json`。v3 manifest 提供 session revision、文档 hash、画布 hash、页面缩略图、完整 scene element、当前风格和 24 个可选视觉预设。每个 element 自带 `capabilities`；UI 不自行猜测哪些字段可改。

## 画布与 PPTX 同版合同

canvas-first 不是示意界面。画布和最终 PPTX 必须使用同一份完整 scene 集合：

- 用户要求 N 页时，`native_deck_spec.json.slides`、`scenes/`、editor manifest、画布缩略图和最终 PPTX 必须都是 N 页；不得用 4 页静态 Demo 代替。
- 使用 `editor_bridge.py export` 的 `slides` 动态创建全部缩略图；不得在 HTML 中硬编码页面标题或页数。
- 点击任一缩略图必须装载该页 `elements`，而不是只切换 active 边框。
- 导出必须提交所有页面的 `slide_number`、`canvas` 和 `elements`。只提交封面状态视为导出失败。
- 最终构建只读取当前 `scenes/`。画布已有而基础 archetype 没有的文本、形状与 connector，由构建器原生 materialize；禁止再写一个仅在导出后运行的封面后处理脚本。
- 质量门前比较 `manifest.slide_count`、scene 文件数和 PPTX 页数；任一不一致即 `BLOCKED`。

生成真实画布：

```bash
python scripts/editor_bridge.py export --session <session>
cp assets/editor/render_editor_canvas.py <session>/analysis/render_editor_canvas.py
python scripts/render_editor_canvas.py \
  --manifest <session>/reports/editor-manifest.json \
  --out <session>/reports/editor-canvas.html
```

对话中展示的是该 `editor-canvas.html`，不要手写固定 4 页的 HTML 示例。

`apply` 接收 `schemas/editor-patch.schema.json` 约定的 patch。桥接脚本负责：

- revision、文档 hash 与画布 hash 冲突检测；
- 修改前自动 snapshot；
- 更新原生 Deck spec；
- 同步 scene 标题和消息；
- 标记受影响页面缓存为 stale；
- 写入 `reports/editor-events.jsonl`；
- 返回新 manifest。

## Canvas-first 工作流

用户明确要求“先在画布编辑，确认后再输出 PPTX”时，建立 session 必须传入：

```bash
python scripts/init_deck_session.py ... --editor-workflow-mode canvas-first
```

该模式不是“先生成最终 PPTX 再打开”。正确顺序是：

```text
建立 slides_plan / native_deck_spec / scene
-> export manifest
-> 画布展示 24 个样式预设与逐页 scene
-> 用户选择整套风格（style_selection_status=confirmed）
-> 用户逐页编辑文字、位置和对象样式
-> 预览构建只写 cache/editable/，不得写 final/
-> 用户点击导出
-> approve-export
-> 构建、验证并写入 final/*.pptx
```

在 `editor_export_approval=approved` 之前，构建器会拒绝把文件写进 session 的 `final/`。UI 可以直接按 scene element 渲染画布，不需要先创建临时 PPTX；需要核对 PowerPoint 排版时，预览 PPTX 只能写到 `cache/editable/preview.pptx`。

画布采用“主画布优先”的可折叠三栏结构：左侧页面缩略图默认窄栏，中间 16:9 可编辑 scene 占据主要可用空间，右侧对象属性与样式面板默认收起。当前页面不得因展示 24 个预设而缩小到文字不可读；页面显示尺寸不得小于约 `746×420` CSS 像素，空间不足时让中间区域滚动。顶部必须提供页面列表、对象编辑和专注画布开关，不显示 Markdown 按钮、标签页或编辑框。点击页面中的文字对象时展开右侧面板，宽度约 `320px`；样式预设在面板内滚动，不能永久挤占主画布，也不能只显示当前深蓝主题。用户没有选定样式时，应显示“待选择”，不能把推荐样式冒充用户选择。Markdown 仅保留为内部内容源和导出回写数据。

首次打开画布前，先从已构建的原生 PPTX 同步 element：

```bash
python scripts/sync_canvas_scene.py --session <session> --pptx <session>/final/deck.pptx
```

该 adapter 不启动 PowerPoint。它通过 `python-pptx` 提取原生对象的 ID、位置、尺寸、旋转、图层、文字和基础样式，写入 scene element v2。

## UI 运行循环

```text
打开 session
-> export manifest
-> 显示页面缩略图与可编辑字段
-> 用户提交 patch
-> apply patch
-> build_native_editable_deck.py --scene-dir <session>/scenes --session <session>
-> 更新 PNG 缩略图
-> export 新 manifest
-> 最终一次 PowerPoint 渲染
```

UI 可以轮询或 tail `reports/editor-events.jsonl` 展示 `planning`、`generating`、`rebuild_required`、`rendering`、`validated` 等状态。未来接入 WebSocket 时，只需写一个读取同一事件和 manifest 的 adapter，不改变 Skill interface。

Markdown-first session 的 manifest 额外提供 `authoring.markdown`、`authoring.markdown_sha256` 和 round-trip capability。UI 必须把完整 Markdown 源显示在可编辑面板中；导出时同时提交完整 Markdown 和完整 scene。浏览器无法直接写本地文件时，由 follow-up 请求交给 Skill 写回并重新编译，不得只保存在页面内存。

## Patch 示例

```json
{
  "schema_version": 3,
  "request_id": "ui-0001",
  "base_revision": "r0003",
  "document_sha256": "<manifest 中的值>",
  "canvas_sha256": "<manifest 中的值>",
  "operations": [
    {
      "op": "update-element",
      "slide_number": 1,
      "element_id": "s001_hero",
      "changes": {
        "bbox": [180, 220, 720, 190],
        "text": "新的封面标题",
        "style": {"font_size_pt": 30, "font_color": "C62828"},
        "rotation": 0,
        "z_index": 4
      }
    }
  ]
}
```

v3 支持 `replace`、`update-element` 和受保护的 `apply-style`。element 只接受自身 `capabilities` 允许的 `text/geometry/style/rotation/z-order`。禁止通过通用 `replace` 修改页码、archetype、风格、字体策略、视觉资产来源和安全状态。旧 revision、document hash 或 canvas hash 必须返回冲突，不覆盖新版本。

### 风格切换

UI 用三个标签呈现风格能力：`整套风格 / 本页变体 / 对象样式`。前两者使用 `apply-style`，对象样式继续使用 `update-element`。

```json
{
  "schema_version": 3,
  "request_id": "style-0001",
  "base_revision": "r0003",
  "document_sha256": "<manifest 中的值>",
  "canvas_sha256": "<manifest 中的值>",
  "operations": [{
    "op": "apply-style",
    "scope": "deck",
    "style_id": "executive-minimal",
    "variant_id": "charcoal-gold",
    "mode": "preserve-layout"
  }]
}
```

- `scope=deck` 可以切换主风格家族和变体，并同步 typography/table profile。
- `scope=slide` 只允许选择当前主风格家族内的变体，避免随机混搭。
- `replace-theme` 清空目标页的手工 canvas override，按新主题完整重建。
- `preserve-layout` 保留位置、尺寸、文字、旋转和层级，清除旧颜色/字体覆盖后换肤。
- 风格卡片使用 manifest `style_catalog[].design_tokens` 生成预览；每张卡显示家族、变体名、主背景、主色、辅助色和文字色。
- 推荐顺序不得等同于自动应用。AI、技术或售前主题可以把企业科技、咨询商务、极简高管列为候选，但必须等待画布选择后才能在 `canvas-first` 模式确认风格。

## Scene element v2

```json
{
  "id": "s001_hero",
  "type": "text",
  "bbox": [122.4, 194.4, 979.2, 208.8],
  "rotation": 0,
  "z_index": 1,
  "editable": true,
  "locked": false,
  "capabilities": ["text", "geometry", "style", "rotation", "z-order"],
  "role": "hero",
  "text": "企业 AI 知识库",
  "style": {"font_size_pt": 34, "font_color": "111827", "bold": true},
  "source_binding": {"document": "analysis/native_deck_spec.json", "path": "/slides/0/title"}
}
```

画布固定使用 `1920 × 1080 px` 逻辑坐标。UI 可以自由缩放显示，但提交 patch 时必须转换回逻辑坐标。文本 element 的 `source_binding` 让画布文字和 Deck spec 同步，避免两个事实源漂移。

## PowerPoint GUI 策略

默认 `gui_validation_mode: final-only`：

- 中间冒烟只展示 PNG；
- 中间预检不启动 PowerPoint；
- UI 编辑后只重建页面与缩略图；
- 最终 artifact 完成后才调用一次 `render_pptx.py --validation-stage final`；
- `reports/final-render.json` 必须绑定最终 PPTX 和 PowerPoint 生成的 PDF。

`eager` 允许中间真实渲染；`never` 完全禁止 GUI，但统一质量门只能给出带警告的结果。

## v3 边界

- v3 面向 `native-editable-deck`，支持文本对象移动、缩放、旋转、图层、基础字体/颜色样式和风格预设切换。
- 图片、图表和表格支持几何、旋转和图层；内部数据编辑继续走 Deck spec，不直接拆 OOXML。
- v3 还不支持组合/取消组合、自由曲线路径编辑、动画时间轴和图片裁剪手柄。
- 真正的多人协作、评论和实时光标属于 UI/协作 adapter，不写进 PPT 生成 Skill。
