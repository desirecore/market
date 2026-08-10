# 确定性路由

本文件是路线选择的唯一权威。先把用户意图写成结构化 request JSON，再运行 `scripts/route_deck_workflow.py`。一旦得到 `PASS`，本次任务只能读取和执行 `authority` 指向的路线；不得把多条生产链混在一起。

## 路由矩阵

| 路线 | 触发条件 | 必要输入 | 输出承诺 |
|---|---|---|---|
| `image-generation` | 图片型 PPTX、PDF、PNG，且不要求对象级编辑 | 内容简报 | 整页图片、图片型 PPTX/PDF |
| `element-rebuild` | 明确要求可编辑 PPTX，或把已有页面重建为可编辑对象 | 新做时需要内容；复刻时需要参考页 | 原生文本/形状与独立视觉资产组成的 PPTX |
| `svg-redraw` | 明确要求 SVG | 参考页图片 | SVG 与预览，不承诺 PowerPoint 对象级编辑 |
| `native-template-fill` | 原生 PPTX 模板加新内容，要求保留模板设计并填充 | 源 PPTX、新内容 | 直接修改 OOXML 的新 PPTX，不经过整页生图或 SVG |

`operation=enhance`（备注、音频、动画增强）当前必须返回 `BLOCKED`，留给后续阶段实现。

## Request JSON

```json
{
  "delivery_type": "editable-pptx",
  "operation": "fill",
  "input_kind": "pptx-template",
  "editability": "editable",
  "has_source_pptx": true,
  "has_new_content": true,
  "has_reference_slides": false,
  "preserve_native_design": true,
  "explicit_template_fill": true
}
```

允许的核心值：

- `delivery_type`: `image-pptx`、`editable-pptx`、`pdf`、`png`、`svg`、`pptx`、`unspecified`
- `operation`: `create`、`fill`、`rebuild`、`enhance`
- `input_kind`: `topic`、`document`、`pptx-template`、`pptx-finished`、`slide-images`、`mixed`
- `editability`: `image`、`editable`、`unspecified`

用户只说 `PPTX` 时保留 `delivery_type=pptx`，脚本会返回 `NEEDS_INPUT` 和唯一问题。不要在脚本外自行猜测。

## 命令

```bash
python3 scripts/route_deck_workflow.py \
  --request <session>/route-request.json \
  --session <session>
```

结果写入 `reports/route-decision.json` 并同步到 `metadata.json`：

- `PASS`：进入且只进入所选路线。
- `NEEDS_INPUT`：只询问 `blocking_question`，不得开始生产。
- `BLOCKED`：报告 `missing_prerequisites`，不得静默降级。

## 失败恢复

修复结构化 request 或补齐必要输入后重新运行路由。不要通过手改 `metadata.json.route` 绕过路由报告；统一质量门会校验两者一致。
