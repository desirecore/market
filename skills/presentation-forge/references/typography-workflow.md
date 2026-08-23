# 中文排版与表格策略

新做可编辑 PPTX、原生模板填充或检查正式中文汇报时读取本规范。目标是把字体、字号、段落和表格对齐变成可执行策略，而不是依赖页面级临时判断。

## 选择 Profile

内置配置位于 `styles/typography-profiles.json`。风格在 `styles/catalog.json` 中绑定默认 `typography_profile` 与 `table_profile`；用户模板、品牌规范或明确指定字体始终优先。

| Profile | 适用场景 | 主要特点 |
|---|---|---|
| `zh-formal-reading` | 研报、政府专项材料、邮件阅读型正式汇报 | 标题黑体、正文宋体、西文 Times New Roman；正文和表格密度较高 |
| `zh-business-present` | 售前、项目汇报、技术说明、会议投屏 | 中文无衬线；正文与表格字号适合会议屏幕 |
| `zh-executive-stage` | 高管演讲、董事会重点页、品牌发布 | 更大字号、低密度、强页面节奏 |

宋体、12pt 和 1.5 倍行距不是全局默认值，只属于正式阅读型 profile。存在模板真实字号系统时，以模板为准并把例外写入 review note。

## Token 纪律

构建前在 `metadata.json` 锁定 `typography_profile` 和 `table_profile`。文本对象使用语义角色，不直接发明任意字号：

- `hero`、`section_title`、`page_title`
- `subtitle`、`minor_title`
- `body`、`label`、`caption`
- `table`

字号使用 `0.5pt` 网格。超出容量时优先精简、扩大文本框或拆页；不要把正文持续缩到 profile token 以下。用户确有模板或品牌字号要求时允许偏离，但必须记录原因。

构建器会把语义角色写入 shape name 的 `[pf-role=<role>]` 标记，供 `validate_pptx_typography.py` 回读。手工或模板对象缺少标记时，验证器只能根据 placeholder、名称和内容做有限推断；无法判断必须报告 `NOT_CHECKED`，不能算作通过。

## 表格策略

- 单元格默认上下居中。
- 表头居中；索引或类目列居左；普通文本列居左；数值列居右。
- 表格段前段后为 0、单倍行距、无首行缩进或异常层级。
- 百分比、单位、负数和小数位数在同列保持一致；单位优先写入表头。
- 无法可靠识别列语义时记录 `NOT_CHECKED`，不要猜测后强制改写。

## 验证

先运行字体声明检查，再运行语义排版检查：

```bash
python scripts/validate_pptx_fonts.py final/deck.pptx --font "微软雅黑"
python scripts/validate_pptx_typography.py final/deck.pptx \
  --profile zh-business-present \
  --table-profile presentation-data-table \
  --out reports/typography-validation.json
```

结果语义：

- `PASS`：已检查项符合策略。
- `WARN`：可交付但应修复或解释，例如字号偏离 token、表格对齐不一致。
- `NOT_CHECKED`：没有足够的角色或格式信息完成判断。
- `FAIL`：配置、文件或检查过程无效。

统一质量门把 `WARN` 和 `NOT_CHECKED` 作为显式警告，把 `FAIL` 作为阻断项。
