# 新 PPT 的计划、Session 与 Prompt 规范

新做 PPT 时使用本规范。目标是让内容可审阅、生成过程可追踪、失败页面可单独重做。

## 执行顺序

```text
确认 PPTX 可编辑性与最低简报
-> 建立 session
-> 运行确定性路由并锁定唯一 authority
-> 编写 slides_plan.md
-> 按 outline_review_mode 连续执行或显式等待确认
-> 编译 prompts.json
-> 生成单页视觉冒烟
-> 用户确认视觉冒烟
-> 生成全量
-> 打包与 QA
```

大纲默认不构成阻塞门：没有明确审阅意图时记录 `outline_review_mode: continuous` 和 `outline_approval: auto-proceed`，写完计划后直接继续。用户明确说“先输出大纲”“等我确认”“确认后再生成”“暂时不要制作”等表达时，记录 `outline_review_mode: explicit` 和 `outline_approval: pending`，展示大纲并暂停；确认后改为 `approved`。用户明确要求跳过已经触发的确认门时记录 `outline_approval: waived`。冒烟仍是独立确认门；用户明确要求跳过时记录 `smoke_approval: waived`。

## Session 目录

使用：

```bash
python scripts/init_deck_session.py \
  --title "企业 AI 知识库解决方案" \
  --delivery-type image-pptx \
  --outline-review-mode continuous \
  --gui-validation-mode final-only \
  --style-id enterprise-tech-dark \
  --out-root ./outputs
```

目录结构：

```text
outputs/<session-id>/
├── slides_plan.md
├── slides_plan.json       # 可选；Markdown 计划稳定后再派生
├── prompts.json
├── metadata.json
├── sources/
├── analysis/
├── scenes/
├── versions/
├── cache/image/
├── cache/editable/
├── references/
├── generated/
├── assets/
├── final/
├── render/
├── compare/
└── reports/
```

`slides_plan.json` 是可选派生文件；只有脚本明确需要时才生成。不要手改派生 JSON。

用户选择 Markdown-first Canvas 时，session 额外包含 `slides.md`，并将 `metadata.authoring_mode` 设为 `markdown-canvas`、`metadata.content_source` 设为 `slides.md`。此时 `slides_plan.md` 与 `prompts.json` 都由 `compile_slides_markdown.py` 派生；人工只编辑 `slides.md`。完整规则见 [markdown-canvas-workflow.md](markdown-canvas-workflow.md)。

建立 session 后按 [routing-workflow.md](routing-workflow.md) 生成 `reports/route-decision.json`。路线未达到 `PASS` 前，不得编译 scene、生成图片或填充 PPTX。

`continuous` 模式写完 `slides_plan.md` 和 `prompts.json` 后直接运行 `scripts/compile_scenes.py`；`explicit` 模式等待大纲批准后再运行。后续图片版与可编辑版都使用这些 scene；详细规则见 [scene-workflow.md](scene-workflow.md)。

## slides_plan.md

Markdown 是内容 source of truth。推荐格式：

```markdown
---
title: 企业 AI 知识库解决方案
delivery_type: image-pptx
style_id: enterprise-tech-dark
typography_profile: zh-business-present
table_profile: presentation-data-table
visual_asset_policy: native-image-assisted
audience: CIO、IT 负责人、知识管理负责人
goal: 同意开展四周 PoC
---

## 1. [cover] 企业 AI 知识库解决方案

布局：cover-hero

页面目标：建立方案定位并提出 PoC 行动。

核心信息：
- 让企业知识真正可用
- 四周验证价值与落地条件

事实边界：
- 不使用客户案例、准确率或 ROI 数据

素材：
- 无真实 Logo，右上角预留区域

布局意图：左文右图的企业科技封面
```

每页必须包含：

- 页码与 `page_type`：`cover`、`agenda`、`section`、`content`、`data`、`architecture`、`process`、`closing` 或 `other`。
- `layout_id`：从所选风格的 `layouts.json` 选择；若没有完全匹配，选最接近的布局并在“布局意图”说明调整。
- 标题、页面目标和 2-4 组核心信息。
- 事实边界：禁止虚构、待确认信息、不可生成内容。
- 素材：真实图片、Logo、截图、图表或“无素材”。
- 布局意图：一句话说明页面形态，不写像素坐标。

## prompts.json

`prompts.json` 是逐页生成记录，不是内容源。最小结构：

```json
{
  "schema_version": 1,
  "session_id": "20260809-083000-enterprise-ai-knowledge-base",
  "delivery_type": "image-pptx",
  "style_id": "enterprise-tech-dark",
  "typography_profile": "zh-business-present",
  "table_profile": "presentation-data-table",
  "visual_asset_policy": "native-image-assisted",
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "style_id": "enterprise-tech-dark",
      "layout_id": "cover-hero",
      "layout_intent": "左文右图的企业科技封面",
      "prompt": "完整的逐页生成提示词",
      "reference_images": [],
      "asset_reference_images": [],
      "status": "planned",
      "output_image": null,
      "qa": {
        "status": "pending",
        "notes": []
      }
    }
  ]
}
```

生成前检查页码连续且与 `slides_plan.md` 一致。生成后更新 `status`、`output_image` 和 `qa`；不要删除失败记录。

## 单页视觉冒烟

- 默认选择封面；封面不能验证主体风格或信息密度时，选择风险最高的代表页。
- 冒烟页必须使用正式风格、正式提示词和正式尺寸，不能用低质量占位稿冒充。
- 向用户展示样张，并明确询问是否继续全量生成。
- 用户要求修改时，只重编译和重生成该页；确认前不生成其他页面。
- 用户确认后，在 `metadata.json` 记录页码、时间和 `smoke_approval: approved`。

## metadata.json 状态

至少记录：

```json
{
  "session_id": "...",
  "title": "...",
  "delivery_type": "image-pptx",
  "style_id": "enterprise-tech-dark",
  "typography_profile": "zh-business-present",
  "table_profile": "presentation-data-table",
  "visual_asset_policy": "native-image-assisted",
  "editability_confirmed": true,
  "route": "image-generation",
  "route_status": "PASS",
  "status": "planning",
  "outline_review_mode": "continuous",
  "outline_approval": "auto-proceed",
  "gui_validation_mode": "final-only",
  "final_powerpoint_validation": "pending",
  "smoke_slide": null,
  "smoke_approval": "pending",
  "final_qa": "pending"
}
```

`delivery_type` 只允许：`image-pptx`、`editable-pptx`、`pdf`、`png`、`svg`。用户只说 PPTX 时，先询问，不得写入模糊值。

正式交付前运行 `scripts/run_quality_gate.py`；该脚本负责把 `final_qa` 更新为 `pass`、`warn` 或 `blocked`。
