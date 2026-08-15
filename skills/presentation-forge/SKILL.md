---
name: presentation-forge
description: "创建中文商业汇报，从主题、文档或 slides.md 生成原生可编辑 PPTX，提供 Markdown-first 实时画布、样式切换和同版导出，使用 image-2 辅助生成独立视觉资产，把截图或图片型幻灯片重建为可编辑 PPTX/SVG，或用原生 PPTX 模板填充新内容。用户要求制作售前方案、项目汇报、产品介绍、行业分析、培训材料、像 Markdown 一样编辑并导出、AIPPT 式可编辑演示、套用 PowerPoint 模板、图片页转可编辑 PowerPoint、重建幻灯片或输出 SVG 时使用。"
version: 0.1.0
type: procedural
risk_level: low
status: enabled
tags:
  - ppt
  - pptx
  - svg
  - presentation
  - slides
metadata:
  author: Ronnie2025
  updated_at: '2026-08-10'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: Presentation Forge
      short_desc: 中文 toB 商业汇报 PPT 工作流：整页生图、图片页重建为可编辑 PPTX/SVG、原生模板填充，适配 Codex/Claude Code
      description: >-
        面向中文 toB 商业汇报的 PPT 工作流，支持整页生图、把截图或图片型幻灯片重建为可编辑 PPTX/SVG，或用原生 PPTX
        模板直接填充新内容。制作售前方案、项目汇报、产品介绍、行业分析、培训材料，或图片页转可编辑 PowerPoint 时使用。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Presentation Forge
      short_desc: Chinese toB business-presentation workflow — image decks, rebuild slides into editable PPTX/SVG, native template filling
      description: >-
        Chinese toB business-presentation workflow: full-page image decks,
        rebuilding image/screenshot slides into editable PPTX/SVG, and native
        PPTX template filling. Use for pre-sales decks, project reports, product
        intros, industry analysis, training material, or image-to-editable
        PowerPoint. The skill body is authored in Chinese, so the en-US locale
        intentionally falls back to the shared body and is locked as
        human-maintained.
      translated_by: human
      source_hash: 'sha256:49a6a6b6867b2d1b'
      body: ./SKILL.md
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><rect x="3" y="4" width="18" height="12" rx="1.5"
    stroke="#2563EB" stroke-width="1.7"/><path d="M12 16v4M8.5 20h7"
    stroke="#2563EB" stroke-width="1.7" stroke-linecap="round"/><path d="m6.5 12
    3-3 2.2 2.2L16 7" stroke="#2563EB" stroke-width="1.7" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  short_desc: Chinese toB business-presentation workflow — image decks, editable PPTX/SVG rebuild, native template filling
  category: creative
  maintainer:
    name: Ronnie2025
    verified: false
  channel: latest
---

# Presentation Forge

本文件是给执行体使用的路由和操作规程。面向用户的项目说明、效果图和安装命令见上游仓库 <https://github.com/mashagua/presentation-forge>。

先判断输入来源、沟通任务和最终目标：

1. **新做且重视觉的 PPT 汇报**：走整页生图 PPT，生成图片型 PPTX / PDF / PNG。
2. **已有图片页、截图页、旧 PPT 渲染页，或整页生图页**：再根据目标进入拆解。
3. **要 PowerPoint 内继续改字、移元素、换图标**：走元素重组。
4. **只要 SVG、网页/文档复用，或低成本看结构**：走 SVG 拆解。
5. **提供原生 PPTX 模板和新内容，要求保留模板设计直接填充**：走原生 PPTX 模板填充。
6. **从主题或文档新做演示或可编辑 PPTX**：默认走 Markdown-first Canvas，以 `slides.md` 为人工内容源，先展示完整可编辑画布；确认后使用原生可编辑 Deck 导出 PPTX。
7. **用户明确要求直接导出、不要画布或跳过预览**：走原生可编辑 Deck 的 `direct-build`；默认使用 `native-image-assisted`，文字、结构、表格和图表保持原生。

路径可以串联：先用整页生图 PPT 形成视觉页；如果后续需要编辑或复用，再把单页 PNG 交给元素重组或 SVG 拆解继续处理。从零新做演示时默认进入 Markdown-first Canvas；已有图片页要求可编辑时走元素重组。SVG 拆解不是默认的 PPT 可编辑路线。

## 路由判断

### 使用单一权威路由

完整读取 [references/routing-workflow.md](references/routing-workflow.md)，把用户意图写成结构化 request JSON，并运行 `scripts/route_deck_workflow.py`。`reports/route-decision.json` 是唯一有效的路线决定：

- `PASS`：只读取并执行 `authority` 指向的路线，不并行准备其他路线的产物。
- `NEEDS_INPUT`：只询问报告中的一个 `blocking_question`，不要展示路线菜单。
- `BLOCKED`：补齐 `missing_prerequisites`，不要静默降级。

手工启发式只能用于填写 request JSON，不能覆盖脚本结果。

### 建立最低可执行简报

开始制作前，读取用户材料，并确认以下字段：

- 材料：附件、文件路径、网页内容或用户提供的事实。
- 汇报类型：售前方案、项目汇报、产品介绍、行业分析、复盘、培训或其他。
- 受众：具体角色、行业、决策层级和已有认知。
- 沟通目标：希望受众理解什么、相信什么、最终采取什么行动。
- 使用场合：现场演示、线上会议、邮件发送、留档或自行阅读。
- 篇幅：页数或汇报时长；页数是约束，不是内容目标。
- 视觉与品牌：风格、主色、模板、真实 Logo 和禁止内容。
- 编辑要求与交付：图片型 PPTX、可编辑 PPTX、PDF、PNG、SVG、提示词或 QA 文件。

如果用户要求交付 `PPTX`，但没有明确说明是否需要编辑，必须先询问并确认选择“图片型 PPTX”还是“可编辑 PPTX”；在获得回答前，不得默认进入整页生图或元素重组。

新做 PPT 时，读取 [references/planning-workflow.md](references/planning-workflow.md)，并把确认后的编辑要求写入 session 的 `metadata.json`。禁止使用含义模糊的 `pptx` 作为交付类型；只能记录 `image-pptx` 或 `editable-pptx`。

如果缺少“材料、汇报类型、受众、沟通目标”中的任意两项，先提出不超过 3 个关键问题，不要直接生成页面。若用户授权自行判断，列出明确假设后继续规划。

逐页大纲始终写入 `slides_plan.md`，但默认采用连续执行：生成大纲后直接进入后续制作，不因大纲暂停，也不把“请先判断缺失信息”“使用明确假设”视为等待确认。只有用户明确表达“先输出大纲”“等我确认”“确认后再生成”“暂时不要制作”等审阅意图时，才展示大纲并等待；将 `outline_review_mode` 记录为 `explicit`、`outline_approval` 记录为 `pending`。其他情况记录 `outline_review_mode: continuous`、`outline_approval: auto-proceed`。用户明确要求审阅时不得静默越过确认门。

不得仅凭宽泛的行业或风格描述虚构客户背景、业务数据、产品能力、案例或收益。

### 选择交付路线

确认这四类条件：

- 最终交付：图片型 PPTX / PDF / PNG / SVG / 可编辑 PPTX。
- 是否需要后续编辑：不编辑、少量替换、还是对象级编辑。
- 输入材料：文档、旧 PPT、截图、图片页、整页生图页、参考模板。
- 质量优先级：视觉观感、可编辑性、速度、token 成本、结构复用。

直接选择：

- 用户只说要 `PPTX`、未说明可编辑性：暂停路线选择，先询问需要“图片型 PPTX”还是“可编辑 PPTX”。
- 用户要新做汇报，内容偏观点表达、概念框架或方案展示，且视觉完成度优先：选择 **整页生图 PPT**。
- 用户要从主题或文档新做演示或可编辑 PPTX，且没有明确要求跳过画布：默认选择 **Markdown-first Canvas**，设置 `authoring_mode=markdown-canvas`、`editor_workflow_mode=canvas-first`，并锁定 `native-editable-deck` 构建 authority。
- 用户明确说“直接导出”“不要画布”“跳过预览”：选择 **原生可编辑 Deck** 的 `slides-plan + direct-build`。默认 `native-image-assisted`；用户明确不生图时使用 `native-only`，强视觉且仍要求可编辑时使用 `image-led-editable`。
- 用户要新做汇报，包含密集数据、财务表格、需频繁更新的数字、大量脚注或长期协作模板：选择原生可编辑 Deck 的 `native-only`，不要走整页生图。
- 用户已有图片页，且明确要可编辑 PPTX、PowerPoint 内改字、移动元素、替换图标、元素化重建或图片页转可编辑：强制选择 **元素重组**。
- 用户已有图片页，且明确要 SVG、网页/文档复用，或明确接受低成本结构样板：选择 **SVG 拆解**。
- 用户提供原生 PPTX 模板和新内容，并要求保留模板设计、直接替换文字：选择 **原生 PPTX 模板填充**；不要先转成 SVG 或整页图片。
- 用户既重视视觉又要求后续编辑：优先原生可编辑 Deck 的 `native-image-assisted`；只有明确接受图片主导并需要参考页重建时才先整页生图再元素重组。

成本提示：元素重组通常更耗时、token 更高，但 PPTX 可编辑性更强；SVG 拆解通常更快更省，但复杂视觉会被简化，导入 PowerPoint 后不承诺对象级稳定可编辑。

如果用户目标是可编辑 PPTX，但当前时间、token、图像生成能力或资产素材不足以完成元素重组，必须明确说明只能交付降级草稿或改走 SVG 结构预览；不要自动把 SVG 拆解、原生形状重画或通用图标拼装称为元素重组完成。

不适配时直接说明原因，并建议改用原生可编辑 PPT、数据报表、文档或设计工具流程。

### 建立统一 Session

确定交付路线后，在生成大纲、提示词、图片或 PPTX 前，先用 `scripts/init_deck_session.py` 建立独立 session。所有源材料、大纲、结构化提示词、生成结果、渲染文件和 QA 报告都写入该 session；不要把同一任务的产物散落在工作区根目录。

Session 必须至少包含 `slides_plan.md`、`prompts.json`、`metadata.json`、`sources/`、`analysis/`、`references/`、`generated/`、`assets/`、`final/`、`render/`、`compare/` 和 `reports/`。详细约定见 [references/planning-workflow.md](references/planning-workflow.md)。

### 使用统一 Scene 与 Revision

当新做 PPT、把图片版升级为可编辑版、修改已生成页面或需要回滚时，读取 [references/scene-workflow.md](references/scene-workflow.md)。使用 `scenes/slide-NNN.scene.json` 作为页面语义事实源；图片版和可编辑版共享同一个 `metadata.json`，禁止复制成两个互相漂移的项目。

生产构建前必须：

1. 用 `scripts/compile_scenes.py` 从当前有效计划和 prompts 编译或更新 scene；`explicit` 模式下必须先获得大纲批准。
2. 用 `scripts/validate_scene.py` 校验所有 scene。
3. 用 `scripts/preflight_ppt_environment.py` 检查字体、构建依赖和渲染后端；默认 `gui_validation_mode: final-only`，中间预检不得启动 PowerPoint；`BLOCKED` 时不得宣称完成生产 QA。
4. 用 `scripts/revision_session.py snapshot` 建立 revision 后再进行正式生成或局部修改。

只改一页时使用 `scripts/rebuild_slide.py prepare` 判断该页是否失效；只重新生成目标页的昂贵资产，再用 `commit` 登记新产物。其他页必须保持原 hash 和缓存。最终 PPTX 可以整套快速重新封装，不直接修改脆弱的 OOXML 单页关系。

回滚必须使用 `scripts/revision_session.py rollback`。脚本会先保存当前状态，再恢复目标 revision 并创建新的 rollback revision；不要覆盖或删除历史版本。

### 通过统一质量门

所有路线的最后一步都运行 `scripts/run_quality_gate.py --session <session> --artifact <artifact>`。该脚本校验路线报告、session 元数据、路线专属证据和最终文件，并写入 `reports/quality-gate.json`。

- 只有 `PASS` 可以表述为正式完成。
- `WARN` 必须说明警告及人工复核结果。
- `BLOCKED` 只能报告阻塞点和已生成草稿，不得把某条子验证通过说成整套交付通过。

不要为不同路线另设互不兼容的“最终完成”标准；路线内部验证只能作为统一质量门的证据。

### 字体与渲染后端

- 新做可编辑 PPTX、原生模板填充或正式中文汇报时，完整读取 [references/typography-workflow.md](references/typography-workflow.md)。从 `styles/catalog.json` 继承 `typography_profile` 与 `table_profile`，并写入 `metadata.json`；用户模板或品牌规范优先。
- 图片型 PPT 的 PDF 必须由最终页 PNG 直接合并；禁止再经 LibreOffice 或 PowerPoint 转换。
- 可编辑 PPTX 的每个中文文本 run 必须显式写入 DrawingML `latin`、`ea`、`cs` 字体，并同步 Theme major/minor 东亚字体；构建后运行 `scripts/validate_pptx_fonts.py`。
- 可编辑 PPTX 构建后运行 `scripts/validate_pptx_typography.py`，检查语义字号 token、`0.5pt` 网格、段落设置和表格对齐；将结果写入 `reports/typography-validation.json`。`WARN` 必须说明，`NOT_CHECKED` 不得算作通过。
- `scripts/preflight_ppt_environment.py` 默认只做静态环境检查并把真实渲染推迟到最终 artifact。只有 `gui_validation_mode: eager` 才在中间执行中文真实导出探测。
- macOS PowerPoint 自动化需要系统 Automation/Apple Events 权限。代理运行真实探测时应申请 GUI/自动化执行权限；被系统拒绝时记录为 `BLOCKED`，不要循环重试或临时改写 AppleScript。
- 用 `scripts/render_pptx.py` 统一导出。默认中间调用使用 `--validation-stage intermediate --gui-validation-mode final-only` 并返回 `DEFERRED`；最终构建完成后仅调用一次 `--validation-stage final`。PowerPoint 成功标记 `PASS`；LibreOffice 只能标记 `APPROXIMATE`，不得作为正式中文可编辑 PPTX 的最终视觉证据。
- 可编辑 PPTX 的正式视觉验收以目标 PowerPoint 后端为准；LibreOffice 仅用于发现明显结构问题。
- 原生模板填充禁止用 `xml.etree.ElementTree` round-trip OOXML；必须保留 `p14`、`a14` 等原始前缀，并在交付前运行 `scripts/validate_ooxml_namespaces.py`。
- 用户指定宋体等字体时，在 `fill_plan.json.font_policy` 记录字体与作用域。默认只作用于替换文字；只有用户明确要求全局统一时才使用 `all-selected-text` 或 `theme-and-replaced`。

### 选择商业风格

新做 PPT 时读取 [references/style-library.md](references/style-library.md) 和 `styles/catalog.json`，根据受众、行业、目标和场合推荐 1–2 套风格。用户未指定且风格选择不影响内容方向时，可以采用最匹配的一套，但必须在大纲中明确标注为假设。

用户要求画布、可视化编辑、先编辑后导出或样式选择器时，强制使用 `canvas-first`：展示 24 个预设，不自动把推荐第一项确认为最终风格。AI、科技、售前等关键词只能影响推荐排序，不能强制选择深蓝。

canvas-first 必须展示用户要求的完整页数并逐页可切换：用户说 10 页，就先从 manifest 动态渲染 10 个缩略图和 10 页 scene。禁止交付固定 4 页的界面示意，禁止点击缩略图只改变边框而不载入该页对象。导出必须提交全量 scene，并从同一 scene 原生构建 PPTX，使页面数量、文字、对象、坐标、样式和层级与画布一致；不要在导出后另起一套布局或只后处理封面。完整合同见 [references/editor-ui-integration.md](references/editor-ui-integration.md)。

选定后完整读取 `styles/<style_id>/STYLE.md` 与 `layouts.json`，并执行：

- 将 `style_id` 与 `style_variant` 写入 `slides_plan.md` frontmatter、`prompts.json` 和 `metadata.json`。风格库提供 8 个家族、24 个可选预设。
- 将风格绑定的 `typography_profile` 与 `table_profile` 写入同一组文件；字号由语义 token 取得，不在页面代码中临时发明任意小数档位。
- 每页选择一个 `layout_id`，写入逐页计划与结构化 prompt；不得超过该布局的 `content_capacity`，超出时拆页。
- 冒烟页使用正式风格和正式布局。用户确认的是该风格方向，不代表允许虚构图片、案例或数字。
- 连续页面避免完全相同的构图；优先复用标记为 `reuse_friendly: true` 的内容布局。
- 用户提供真实品牌模板或品牌规范时，以用户材料为准；内置风格只补足未定义部分。

### 通过构建前设计门

所有新生成路线在正式构建或全量生图前完整读取 [references/design-quality-workflow.md](references/design-quality-workflow.md)，并运行 `scripts/validate_design_quality.py --session <session>`。禁止无意义卡片化、过量圆角矩形、无理由窄边强调条、默认阴影或渐变、形状上叠独立文本框、整页可移动图片背景，以及把设计说明或讲者提示写入正文。硬错误必须先修复；启发式警告只有在 spec 中记录页码、规则代码和明确理由后才能豁免。最终统一质量门必须读取 `reports/design-quality.json`。

## 路径 A：整页生图 PPT

适合单点沟通、重视觉、接受图片化交付的材料，例如方案汇报、售前交流、内部同步、培训讲解、复盘展示。

执行步骤：

1. 按“最低可执行简报”确认材料、汇报类型、受众、沟通目标、使用场合、篇幅、风格、品牌、输出格式和禁止内容。
2. 建立 session；选择或确认商业风格；读取用户材料，按 [references/planning-workflow.md](references/planning-workflow.md) 写 `slides_plan.md`。它是内容 source of truth，必须包含 `style_id`、页面类型、`layout_id`、标题、页面目标、核心信息、事实边界、素材和布局意图。
3. 根据 `outline_review_mode` 处理计划：`continuous` 直接继续；`explicit` 将 `slides_plan.md` 交给用户并等待确认。需要修改文案时只修改 Markdown；任何 JSON 都是派生产物，不作为人工编辑源。
4. 按 [references/prompt-patterns.md](references/prompt-patterns.md) 将计划编译为结构化 `prompts.json`。每页记录 `slide_number`、`page_type`、`style_id`、`layout_id`、`layout_intent`、完整 `prompt`、参考图和生成状态；禁止只保存无法映射回页码的散装 prompt 文本。
5. 先生成 1 页视觉冒烟：默认封面；如果封面信息简单而其他页面风险更高，选择架构页、数据页或信息最密集的代表页。向用户展示样张并等待确认后再生成全量。只有用户明确要求跳过、或整套只有 1 页时，才可跳过确认。
6. 用户确认冒烟页后，调用 imagegen 生成其余 16:9 整页图。中文少而大，避免密集表格和小字号脚注；已通过的页面不要因局部问题一起重生。
7. 可以使用用户提供或明确授权的真实公司 Logo。用透明 PNG 或 SVG 原文件在后处理阶段叠加，不交给 imagegen 生成或仿造；未提供 Logo 时只预留位置。
8. 用 `scripts/package_image_deck.py` 或 `make pack` 封装 PPTX；PDF 由最终页 PNG 直接合并，可选输出每页 PNG 和 contact sheet。
9. 检查页数、尺寸、文字可读性、Logo 位置、伪 Logo、敏感信息和明显错字，并把结果写入 session 的 `reports/` 与 `metadata.json`。

默认交付：

- 图片型 PPTX
- PDF 或每页 PNG，按用户要求
- contact sheet
- 逐页提示词和 QA 记录

边界：图片型 PPT 不等于可编辑 PPT。正文、图表和版式在图片里，不能承诺 PowerPoint 内逐字逐对象编辑。

## 路径 B：元素重组

适合用户已经有图片页、截图页、图片型 PPT，或路径 A 生成的页图，并且希望重建为实用级可编辑 PPTX。

路径 B 是参考图驱动的语义资产重组，不是 SVG 反编译，也不是只用 PPT 原生形状画一张可编辑草稿。

核心判断：

- 文本、标题、卡片、容器、分隔线、普通结构箭头：优先做 PPT 原生对象。
- 图标、徽章、3D 装饰、复杂箭头、插画、设备图、UI 装饰：必须用 Codex 的 `imagegen` 技能生成独立透明资产。
- 原图、截图、硬裁 crop 只能作为参考和中间素材，不能作为最终整页背景或带残边的最终对象。
- 生产级元素重组默认只接受 `imagegen_asset`。`api_generated_asset` 仅在用户明确指定外部图像 API 时使用；`provided_asset` 只用于用户已提供素材、合规素材库或明确标注的 synthetic/demo 试跑。
- 只有在资产有合规来源记录，并且一语义单元一透明 PNG 插入 PPT 后，才算元素重组资产；不能把程序化近似图标、通用图标库、原图 crop 或提示词占位图当成正式元素重组资产。

完整跑触发规则：

- 用户说“完整跑”“正式跑”“完整 imagegen 元素重组”“不要试跑版”“不要 provided_asset”“高保真元素拆解”等表达时，必须进入完整元素重组模式。
- 完整元素重组模式下，所有语义视觉资产必须通过 Codex `imagegen` 基于整页参考图 + 局部 crop/residual crop 生成，并在 `asset_manifest.json` 中标记为 `imagegen_asset`。
- 完整元素重组模式下，禁止静默降级为 `provided_asset`、程序画图、SVG 重画、图标库拼装或原图 crop。若 imagegen 调用失败、资产不合格、切图失败或无法继续，直接报告阻塞点、已完成文件和下一步，不要把降级版说成完整完成。
- 如果用户只是说“试试”“验证链路”“跑通工具链”“先看结构”，可以交付明确标注的结构预览或 synthetic demo；报告里必须写清它不是完整 imagegen 元素重组。

图片生成硬规则：

- 所有涉及图片生成、视觉资产生成、透明资产生成的步骤，默认且优先使用 Codex 的 `imagegen` 技能；不要用 LibreOffice、SVG 重画、程序画图、图标库拼装或其他渲染工具冒充生图。
- `api_generated_asset` 只保留为兼容字段，除非用户明确要求指定外部 API，否则不要主动选择。
- `provided_asset` 只适合用户已提供的合规素材、明确授权素材库或 synthetic demo；不能把程序化图标、通用图标库或原图硬裁片当作生产级视觉复刻资产。
- LibreOffice / PowerPoint / soffice 这类工具只能用于把已生成的 PPTX 渲染成 PDF/PNG 做验收预览，不能用于生成图片资产。使用时要明确标记为“渲染 QA”，不是“图片生成”。
- 大尺寸中心视觉、跨格 3D 元素、复杂箭头、装饰性底座和高风险关键资产必须单独调用 `imagegen` 生成；不要塞进一个大 asset grid 再等分切。

能力预检：开始完整元素重组前，确认 imagegen 可用、所有参考图可读取、目标目录可写、Pillow 与 python-pptx 可导入，并确认存在 PPTX 渲染工具。任一生产级依赖缺失时，先报告缺口和可执行的修复方式，不要静默改成交付标准更低的路线。

执行步骤采用 v4/v5 验证过的生产链路：

1. 建立项目目录，保存参考图为 `reference_page_*.png`。
2. 建立 `visual_inventory.json`，按文本、容器、图标、箭头、装饰、3D 元素等对象做页面清单。
3. 建立 `asset_anchors.json` 和 `layout_rules.json`，记录每个待生成资产的 bbox、含义、目标尺寸、层级、字体策略、禁用媒体和 diff 阈值。
4. 为资产写 `prompts/assets_cycle_*.jsonl` 或 prompt pack。每条 prompt 必须绑定整页 reference 和相关 crop/residual crop，明确对象顺序、grid 行列、纯色背景、无文字、无数字、无标签、无水印、无卡片框、无周边页面碎片；完整元素重组时必须实际调用 Codex `imagegen` 生成独立资产或 isolated asset grid。小图标可以成组生成；中心大视觉和复杂元素必须单独生成。
5. 用 `scripts/grid_cut.py` 或 `make cut` 从合格 generated grid 切成一个元素一个透明 PNG，并生成 `asset_manifest.json`。如果切出的资产贴边、被截断、带绿边、含相邻元素，必须废弃并重新用 `imagegen` 单独生成。
6. 必要时用 `scripts/clean_assets.py` 清理透明边缘、小碎片和残留底色。不能把带残字、残框、硬边的 crop 直接插入 PPT。
7. 用 `scripts/validate_semantic_inputs.py` 或 `make semantic-preflight` 做 build 前校验，确认 inventory、manifest、anchors 和资产文件对齐。
8. 用 `scripts/build_semantic_deck.py` 从 `visual_inventory.json` 和 `asset_manifest.json` 构建 PPTX：文本、卡片、容器和结构走 PPT 原生对象；图标、箭头和装饰元素走独立透明资产。构建时必须输出 `build_report.json`，其中包含每个文本框的原始字号、自动适配后字号、估算溢出比例、bbox、父容器、z-index 和图片 fit 结果。
9. 渲染 PPTX，再用 `scripts/compare_render.py` 或 `make compare` 输出 contact sheet / diff heatmap。
10. 用 `scripts/validate_semantic_deck.py` 或 `make validate` 检查没有整页原图、参考图 hash、SVG 和不合规媒体，并传入 `--build-report` 做文字适配、碰撞检测和布局 QA。
11. 如果出现标题断行、文字溢出、文本互相覆盖、文字压住非装饰图片，先调 `visual_inventory.json` 的 bbox/role/parent_id/fit_mode，或调整 `layout_rules.json` 的字体策略，再重建、重渲染、重对比。不能只看 PPTX 对象数就宣布完成。

验收标准：

- PPTX 可以打开并正常渲染。
- 文本可选中、可编辑，不用隐藏透明文本冒充可编辑。
- 重要图标、箭头、装饰元素可单独选中、移动、替换。
- 没有整页参考图作为最终媒体。
- 没有带残字、残框、硬边的原图裁片。
- 没有用非 Codex imagegen 的方式生成生产级图片资产；LibreOffice 等仅可作为渲染验收工具。
- 输出 manifest、渲染预览、对比图和验证报告。
- `visual_inventory.json` 与 `asset_manifest.json` 对齐：每个语义视觉资产都有合规来源、真实文件和 PPT 插入对象。
- 完整元素重组模式下，`asset_manifest.json` 中的语义视觉资产应为 `imagegen_asset`；除用户显式提供素材外，出现 `provided_asset` 必须降级标注为结构预览或 demo。
- `build_report.json` 中 `layout_qa.error_count = 0`；可接受少量 micro label 字号或设计性文字压图 warning，但必须人工看过预览。
- `compare_render.py` 输出的视觉回归状态为 `PASS` 或明确标记为需要人工复核；contact sheet 要能直接看出标题、卡片和关键流程没有重叠。
- 最终 PPTX 不包含 SVG 媒体、整页或近整页参考图、raw crop、prompt-only 占位图或手绘低保真语义视觉。
- 生产级复刻必须有 `generated/`、`assets/`、`prompts/`、`asset_anchors.json`、`layout_rules.json`、渲染对比和验证报告；只有 synthetic `provided_asset` 的样例只能证明闭环可运行，不能当作视觉复刻效果验收。

不满足以上条件时，只能标记为“可编辑草稿”或“结构预览”，不能标记为元素重组合格。

详细执行规则见 [references/semantic-replica-workflow.md](references/semantic-replica-workflow.md)；局限性见 [references/limitations.md](references/limitations.md)。

## 路径 C：SVG 拆解

适合用户明确要 `.svg`，或要把图片页转换成网页/文档可复用的轻量结构。它可以接收原图、截图、图片页，也可以接收路径 A 生成的单页 PNG。

执行步骤：

1. 读取参考图，识别文本、容器、背景、线条、箭头、简单图标和装饰层。
2. 用原生 SVG 重建页面结构，文本、色块、线条和图形尽量成为独立 SVG 对象。
3. 输出 `.svg` 和 PNG 预览。
4. 用 `scripts/validate_svg_slide.py` 检查画布比例、外部资源、脚本、`foreignObject` 和过小文字。
5. 简短说明哪些对象是 SVG 原生对象，哪些复杂视觉被简化，是否适合继续进入元素重组。

边界：SVG 适合结构复用，但导入 PowerPoint 后不保证内部对象稳定可编辑。用户要对象级 PPTX 编辑时，转回路径 B。

## 路径 D：原生 PPTX 模板填充

适合用户提供原生 `.pptx` 模板和新内容，要求保留模板主题、版式和原有 PowerPoint 对象并直接替换文字。

进入后完整读取 [references/native-template-fill-workflow.md](references/native-template-fill-workflow.md)，并严格执行：

1. 用 `scripts/native_template_fill.py analyze` 提取页面、文本框和表格单元格版式库。
2. 建立 `analysis/fill_plan.json`，按目标故事选择、删除和重排源页面；记录每页 `layout_rationale`。
3. 用 `check-plan` 校验精确 slot、文本容量和 v1 能力边界。
4. 向用户展示页序、删页和内容到版式的映射；确认后才把计划改为 `confirmed`。
5. 用 `apply` 直接修改 OOXML；需要宋体时传入 `--font 宋体 --font-scope replaced-text`。禁止覆盖源 PPTX，也禁止中途转成 SVG 或整页图片。
6. 用 `validate` 回读文字，并用 `validate_ooxml_namespaces.py` 检查兼容性前缀，再进入统一质量门。

v1 不支持重复克隆同一源页、替换图片、编辑图表/SmartArt、改写对象级动画；不得把保留原对象说成已经编辑这些对象。

## 路径 E：原生可编辑 Deck

适合从主题、文档或逐页计划新建可编辑 PPTX，提供类似 AIPPT 的组件化生成体验。进入后完整读取 [references/native-editable-workflow.md](references/native-editable-workflow.md)。

1. 建立 session，确认 `visual_asset_policy`：默认 `native-image-assisted`，可选 `native-only` 或 `image-led-editable`。
2. 按 `outline_review_mode` 处理 `slides_plan.md`；连续模式直接建立 `analysis/native_deck_spec.json`，显式审阅模式等待确认后再建立。每页选择一个 v1 原型并登记原生组件和可选 `visual_slot`。
3. 需要视觉资产时，调用 Codex `imagegen` 技能使用 image-2 生成独立图片；禁止让 image-2 生成整页、正文、真实数字、表格、Logo 或页码。
4. 先通过 Anti-AI-slop 设计门，再用 `scripts/build_native_editable_deck.py` 生成原生文本、形状、流程、表格、Office 图表和独立图片对象。首次构建后运行 `scripts/sync_canvas_scene.py`，把原生对象同步为 scene element v2。
5. 依次完成字体、排版、可编辑性、渲染预览和人工视觉检查，再进入统一质量门。

`native-image-assisted` 不等于每页强制生图：封面、章节和概念页优先使用 image-2；流程、表格和数据页默认优先原生对象。`image-led-editable` 必须至少包含一个有 prompt 记录的 image-2 资产，但仍不得用整页图片冒充可编辑页面。

## 可视化编辑器接入

用户要开发可视化 PPTX 编辑 UI、浏览器内修改页面或接入类似 Codex 的任务界面时，完整读取 [references/editor-ui-integration.md](references/editor-ui-integration.md)。以 scene element v2 和 `scripts/editor_bridge.py export/apply` 作为唯一 editor seam：UI 读取 v3 manifest，提供“整套风格 / 本页变体 / 对象样式”，通过受保护的 `apply-style` 或 element capability 修改画布；Skill 负责 snapshot、冲突检测、scene/spec 同步、页面缓存失效，并用 `build_native_editable_deck.py --scene-dir` 把覆盖值写回原生 PPTX。禁止让 UI 直接修改 OOXML 或自行猜测可编辑字段。

新建演示默认建立 `canvas-first` session，不要求用户额外写“先显示画布”。最终导出前只写 `slides.md`、scene、manifest、缩略图和 `cache/editable/` 预览；不得提前写入 `final/`。只有用户明确要求直接导出、不要画布或跳过预览时才使用 `direct-build`。画布中确认样式并完成编辑后，运行 `editor_bridge.py approve-export`，再构建和验证最终 PPTX。

### Markdown-first Canvas

从主题或文档新建演示时默认完整读取 [references/markdown-canvas-workflow.md](references/markdown-canvas-workflow.md)，并强制使用；无需用户额外声明 Markdown-first：

```bash
python scripts/init_deck_session.py ... \
  --delivery-type editable-pptx \
  --editor-workflow-mode canvas-first \
  --authoring-mode markdown-canvas
python scripts/compile_slides_markdown.py --session <session> --build-preview --render-canvas
```

`slides.md` 是人工编辑源，`native_deck_spec.json`、`slides_plan.md`、`prompts.json` 和 scene 是派生产物。画布修改文字后必须回写 Markdown；自由拖拽只写 scene 几何覆盖。对话中展示 `reports/editor-canvas.html`，不得用静态示意代替。最终只在用户点击导出后批准并构建 `final/*.pptx`。

## 输出纪律

- 先确定输入来源：新做汇报先生成；已有图片页或生成后的页图再拆解。
- 再确定路径和交付承诺，不把生成、元素重组和 SVG 拆解混成同一种能力。
- 新做 PPT 必须以 `slides_plan.md` 作为内容源、以 `prompts.json` 作为逐页生成记录，并在独立 session 内工作。
- Markdown-first Canvas 例外：`slides.md` 是人工内容源，`slides_plan.md` 与 `prompts.json` 由编译器派生，禁止同时手工维护三份内容。
- 大纲默认连续执行；只有用户明确要求审阅或等待确认时才展示并暂停。必须在 metadata 记录 `outline_review_mode` 与 `outline_approval`，不得把没有要求确认的用户默认拦在大纲阶段。
- 新做可编辑 PPTX 必须记录 `visual_asset_policy`；image-2 资产必须登记为独立 `visual_slot` 并保留 prompt 记录。
- 可编辑 PPTX 默认记录 `gui_validation_mode: final-only`；中间只输出 PNG 预览和静态报告，最终 artifact 完成后才允许一次 PowerPoint 真实渲染。用户明确要求逐轮渲染时才使用 `eager`；`never` 必须在交付中说明未做真实 PowerPoint 验收。
- 全量生图前必须完成单页视觉冒烟并获得确认，除非用户明确要求跳过或整套只有 1 页。
- 每次交付都说明最终文件、可编辑范围、已知限制和 QA 结果。
- 每次正式交付必须附带 `reports/quality-gate.json` 的最终状态；没有统一质量门 PASS 不得宣称完成。
- 用户只给出主题、页数等少量信息时，先建立最低可执行简报，不要自行补造业务背景。
- 能运行脚本时优先运行脚本并保留输出；不能运行时说明环境缺口。
- 公开复用或发布仓库前，按 [references/publication-boundaries.md](references/publication-boundaries.md) 检查边界，并运行：

```bash
python scripts/audit_public_skill.py --root .
```

## 硬性规则

- 不编造数字、来源、标准、客户名或证据。
- 不把图片型 PPT 说成可编辑 PPT。
- 不把 SVG 嵌入说成 PowerPoint 对象级可编辑。
- 不让 imagegen 生成真实 Logo、二维码、证书、印章或品牌标识。
- 原生可编辑模式下，不让 image-2 生成整页 PPT、中文正文、表格和可追责数据；image-2 只作为独立视觉资产后端。
- 元素重组模式下，原图 crop 只能是中间参考，不是最终资产。
