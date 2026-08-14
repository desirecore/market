# 原生可编辑 Deck 工作流

从主题、文档或逐页计划新建可编辑 PPTX 时使用本规范。该路线类似 AIPPT 的组件化生成：文字、形状、流程、表格和 Office 图表保持原生可编辑；image-2 负责高价值视觉资产，不生成整页底图。

## 三档视觉资产策略

在 request、`metadata.json` 和 `analysis/native_deck_spec.json` 中使用同一个 `visual_asset_policy`：

| 策略 | 用途 | image-2 规则 |
|---|---|---|
| `native-only` | 财务、制度、密集数据、长期维护模板 | 不生成 image-2 资产；页面使用原生对象和用户提供素材 |
| `native-image-assisted` | 默认；售前、技术方案、项目汇报 | 按页需要生成封面主视觉、插画、3D 元素或复杂装饰 |
| `image-led-editable` | 强视觉发布、品牌故事、概念表达 | 至少包含一个 image-2 主视觉，但标题、正文、结构和数据仍必须原生可编辑 |

不要把 `native-image-assisted` 理解为每页强制生图。数据页、表格页和普通流程页默认不用 image-2；封面、章节、产品场景和概念页优先评估视觉资产槽。

## 内容与组件合同

按 `outline_review_mode` 处理 `slides_plan.md`：`continuous` 写完即继续，`explicit` 等待用户批准。随后建立 `analysis/native_deck_spec.json`，结构遵循 `schemas/native-editable-deck.schema.json`。支持以下 v1 页面原型：

- `cover`
- `content-structured`
- `process-flow`
- `comparison-two-zone`
- `data-callouts`
- `table`
- `architecture`
- `closing-action`

最小示例：

```json
{
  "schema_version": 1,
  "title": "企业 AI 知识库解决方案",
  "style_id": "enterprise-tech-dark",
  "style_variant": "tech-blue",
  "typography_profile": "zh-business-present",
  "table_profile": "presentation-data-table",
  "visual_asset_policy": "native-image-assisted",
  "slides": [
    {
      "slide_number": 1,
      "archetype": "cover",
      "title": "企业 AI 知识库解决方案",
      "subtitle": "让可信知识进入业务工作流",
      "visual_slot": {
        "backend": "image-2",
        "source_type": "imagegen_asset",
        "status": "generated",
        "asset_path": "../assets/generated/cover-hero.png",
        "prompt_record": "../analysis/image-prompts/cover-hero.md"
      }
    }
  ]
}
```

## image-2 资产槽

需要视觉资产时，先把 `visual_slot` 写入 spec，再使用 Codex `imagegen` 技能生成。提示词和结果必须满足：

- 只生成主视觉、插画、3D 元素、装饰或场景图片，不生成整页 PPT。
- 不在图片中生成标题、正文、真实数字、表格、页码、Logo、二维码或认证标识。
- 记录 prompt 文件、输出文件、来源类型和生成状态。
- `backend=image-2` 时，`source_type` 必须是 `imagegen_asset`，状态必须达到 `generated` 或 `validated`。
- 非封面页如果使用视觉资产，显式填写 `bbox_in`，避免覆盖原生内容。
- 生成失败时标记 `blocked`；不要用程序绘图、原图裁片或占位图冒充 image-2 正式资产。

## 构建与验证

构建前先运行 `validate_design_quality.py --session <session>`。构建器也会在创建 PowerPoint 对象前自动执行同一检查；`FAIL` 时停止，`WARN` 写入报告并要求人工复核或带理由豁免。

执行：

```bash
python scripts/build_native_editable_deck.py \
  --spec <session>/analysis/native_deck_spec.json \
  --base-dir <session>/analysis \
  --scene-dir <session>/scenes \
  --session <session> \
  --out-pptx <session>/final/deck.pptx \
  --report <session>/reports/native-editable-build.json
```

构建器输出原生文本、形状、线条、表格、Office 图表和独立图片对象。完成后依次执行：

首次构建后运行 `sync_canvas_scene.py`，将 PPTX 原生对象同步为 scene element v2。UI 修改 element 后，使用同一构建命令和 `--scene-dir` 重建；构建器按对象 ID 应用位置、尺寸、文字、样式、旋转与图层覆盖。

1. `validate_pptx_fonts.py`
2. `validate_pptx_typography.py`
3. `audit_pptx_editability.py`
4. 中间阶段只生成 PNG/结构预览，不打开 PPTX；最终 artifact 完成后运行一次 `render_pptx.py --validation-stage final --gui-validation-mode final-only`
5. 人工检查逐页预览或 contact sheet
6. `run_quality_gate.py`

画布风格切换使用 editor v3 的 `apply-style`。整套切换可跨风格家族；单页切换只允许同一家族内的变体。`preserve-layout` 保留几何和文字并清除旧样式覆盖，`replace-theme` 清空目标页 canvas override 后完整重建。

用户要求先画布后 PPTX 时使用 `editor_workflow_mode=canvas-first`。此时不要先把初稿写入 `final/`：直接从 scene manifest 渲染页面；需要构建中间预览时写入 `cache/editable/preview.pptx`。只有收到画布导出动作、风格已确认且 `editor_bridge.py approve-export` 成功后，才能执行最终构建和质量门。

画布导出后不得重新解释布局。必须把画布提交的全部页面 scene 写回 session，再用同一 scene 构建 PPTX。禁止只读取 `cover` 字段、用临时脚本后处理封面，或让未在画布出现的模板布局覆盖画布对象。页数按用户要求建立；例如用户要求 10 页，画布必须先显示并可切换 10 页，然后才能批准导出 10 页 PPTX。

`reports/native-editable-build.json` 必须记录原生形状、connector、表格、Office 图表、图片对象和 image-2 资产数量。`image-led-editable` 没有 image-2 资产时构建必须失败。

## 能力边界

- v1 不生成 SmartArt、对象级动画、音频和讲者备注。
- Python figure、复杂研究图和照片可以作为独立图片插入，但不能宣称其内部可编辑。
- Office 图表的数据和图表对象可编辑；复杂视觉优先保证表达质量，不强制全部原生化。
- image-2 是视觉资产后端，不是事实、数字、Logo 或中文正文后端。
