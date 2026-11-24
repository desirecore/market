# 查表、选色和导出交接单

命令中的`<skill>`换成当前Skill目录。脚本只用Python标准库，不联网，不生成封面或调用其他Skill。

## 查表

```text
python3 <skill>/scripts/palette.py vocabulary
python3 <skill>/scripts/palette.py show 30
```

## 根据文章判断选色

先由助手读文章，把摘要、用途与情绪写进brief。脚本只负责查表排序：

```json
{
  "title": "软件的成本花在哪里",
  "article_summary": "拆解一款软件的成本构成与使用限制",
  "message": "帮助读者理解取舍",
  "topics": ["科技", "商业"],
  "moods": ["冷静", "克制"],
  "purpose": "解释",
  "intensity": 2,
  "background": "深底"
}
```

```text
python3 <skill>/scripts/palette.py select --brief brief.json --limit 3
```

可用`palette_id`指定编号；`required_colors`、`excluded_colors`接HEX列表；`color_count`限制颜色数量；`background`用“浅底”“深底”或“不限”。`background_hex`须属于当前组。互相冲突或没有满足条件的组合时，脚本会报错，不偷偷换条件。

`custom_colors`接2—6个HEX，或带`name`、`hex`的对象列表；`palette_name`可自定义。这些不会写进原100套。

## 导出配色方案

```text
python3 <skill>/scripts/palette.py handoff --id 65 --brief brief.json --out palette-065
python3 <skill>/scripts/palette.py handoff --custom "#003049" "#FDF0D5" "#D62828" --name "我的配色" --title "我的文章标题" --out my-palette
```

输出`palette-handoff.md`与`plan.json`，包括原始HEX、颜色分工、字色对比和保留要求。`selection_only: true`、`image_generated: false`表明这是选色方案，没有生成图片。

底色优先采用命令行明确给出的`--background`和`--background-hex`；没给时沿用brief，再没有才用目录默认值。指定编号与brief编号冲突时会报错。

brief可另写`style_context`（现有风格背景）、`palette_scope`（允许改色的范围）、`preserve`（须保留的要求列表）。这些只是交接背景，本Skill不会据此设计版式。

导出的方案可以交给Punk或其他封面工具。旧试作版的`prompt`命令已撤掉，统一使用`handoff`，避免把本包误当成封面生成器。

## 更新表格

只维护`references/catalog.json`，再同步导出：

```text
python3 <skill>/scripts/export_table.py --csv <skill>/references/palette-table.csv --cards <skill>/references/color-cards.md
```

图表按001—100排序、十张一组，引用包内色卡。所有图片仍以目录HEX为原始色值。
