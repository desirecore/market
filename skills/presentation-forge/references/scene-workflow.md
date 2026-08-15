# Scene、局部重建与版本工作流

Scene 是每页唯一的结构化渲染事实源。普通模式由 `slides_plan.md` 决定内容；Markdown-first 模式由 `slides.md` 决定内容。scene 固化页面语义、对象和几何，图片版、画布和可编辑版都从 scene 派生，不再各自维护一套页面描述。

## Session v2

```text
session/
├── slides_plan.md
├── prompts.json
├── metadata.json
├── scenes/slide-001.scene.json
├── versions/r0001/
├── cache/image/slide-001/
├── cache/editable/slide-001/
├── generated/
├── assets/
├── final/
├── render/
└── reports/
```

`metadata.json` 只保存共享身份、当前 revision、环境报告和两个交付 variant 的状态。逐页细节留在 scene，构建报告留在 `reports/`。

## 执行顺序

```text
slides_plan.md + prompts.json
-> compile_scenes.py
-> validate_scene.py
-> preflight_ppt_environment.py
-> revision_session.py snapshot
-> rebuild_slide.py prepare
-> imagegen 或 editable builder 生成目标页
-> rebuild_slide.py commit
-> 重新封装整套 PPTX
```

局部重建只让目标页的昂贵依赖失效。最终 PPTX 可以整套快速封装，不直接修改 OOXML 中的单页关系。

`prepare` 会生成后端输入：图片版写入 `cache/image/slide-NNN/prompt.json`；可编辑版写入 `cache/editable/slide-NNN/visual_inventory.json`。其中未解析的 `semantic_visual` 会被标成 `unresolved`，必须完成资产绑定后才能进入正式可编辑构建。

全套可编辑构建使用 `compile_scenes.py --emit-editable-inventory` 生成 `cache/editable/visual_inventory.json`，再交给现有 semantic builder。该派生文件不会覆盖旧项目手工维护的根目录 `visual_inventory.json`。

## Scene 规则

- `slide_id` 永久稳定，使用 `slide-001` 格式；改标题不能改 ID。
- 每个 element ID 在页内唯一，bbox 使用像素坐标 `[x, y, width, height]`。
- `semantic_visual` 是尚未绑定来源的语义视觉；进入可编辑正式构建前转换为 `imagegen_asset` 或有来源记录的 `provided_asset`。
- `scene_hash` 排除自身和构建状态后计算；它决定页面是否失效。
- 普通版使用 `generation.prompt` 生成整页图；可编辑版读取 `elements` 生成原生文字、容器和独立资产。

## Revision 规则

- snapshot 保存 metadata、计划、prompts、scenes 和核心 manifest，不复制大体积生成图。
- revision manifest 保存所有被追踪文件的 SHA-256，资产继续由 session 中的稳定路径或内容 hash 引用。
- rollback 先自动 snapshot 当前状态，再恢复目标 revision，并创建新的 rollback revision；不得删除历史 revision。

## 向后兼容

旧 session 首次运行 `compile_scenes.py` 时自动把 metadata 提升为 schema v2，并从 `slides_plan.md`、`prompts.json` 生成 scene。旧的 `visual_inventory.json`、`asset_manifest.json` 仍可被现有 builder 使用，但新项目应逐步改为从 scene 派生。
