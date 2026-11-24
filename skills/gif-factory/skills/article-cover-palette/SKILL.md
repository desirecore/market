---
name: article-cover-palette
description: 根据文章内容、情绪和表达目的，从100套配色中推荐底色、标题字色和点缀色，支持指定编号、自定义HEX与现有配色评估，输出可交给Punk等封面Skill的配色方案。负责选色，不设计版式或生成封面。
---

# 文章配色 · 100套

这套Skill只负责选配色：读懂文章，推荐颜色，写清底色、标题字、小字和点缀怎么分。100套是颜色库，不是100种文章或版式。安装与示例见[大白话说明](README.md)。

## 包里有什么

- [100套配色表](references/palette-table.md)、[CSV](references/palette-table.csv)和[色卡＋色号图表](references/color-cards.md)。原始数据在[目录](references/catalog.json)，100张现成色卡在`assets/cards/`。
- [选色判断规则](references/article-to-palette.md)：文章先按少数用途判断，再结合具体题材、情绪和已有风格。
- [配色方案交接模板](templates/palette-handoff.md)：将选好的颜色交给Punk等封面Skill，不承担封面构图、字体设计或图片生成。

## 工作范围

用户只问配色时，给一套主推，必要时再给最多两套有明显区别的备选；说明对应文章的内容依据和用法，到此结束。用户指定编号、HEX、品牌色或已有素材时优先执行；用户需要现成色卡时返回对应文件，不重新画图。

先看用户已有风格、材料和允许改色的范围。原配色更合适时可以保留，说明理由；不要为了使用100套而强行换色，也不要把AI题材固定成蓝灰色。

用户要求继续做封面时，将本次配色方案交给负责封面的Skill或工具，由其继续完成构图、字体和成图。本Skill自身不生成封面，也不把配色卡的块字版式套给文章。

## 选色流程

1. 读文章或用户摘要，提炼讲什么、核心落点、表达目的、题材、情绪和视觉强度。只有标题时说明判断暂定；链接读不到时不假装读过全文。
2. 按[判断规则](references/article-to-palette.md)从目录找候选，用文章里的具体内容解释选择。可先运行`scripts/palette.py vocabulary`查看标签，再用结构化brief查表：

```text
python3 <当前Skill目录>/scripts/palette.py select --brief <brief.json> --limit 3
python3 <当前Skill目录>/scripts/palette.py show 30
```

脚本只给助手已经提炼的信息排序，不会自行读懂全文。最高分仍要结合风格、材料、可用颜色数量和局部读字对比判断。自定义HEX不混进原100套。

3. 交付编号、名称、原始HEX、主推理由、底色/标题/小字/点缀分工，以及应保留的原图颜色。给出辅助黑白字色时单独标明，不算新配色。

## 推荐搭配Punk使用

本Skill选配色，推荐搭配[Adrian Punk的Punk-Posters](https://github.com/adrianpunk/Punk-Posters)完成封面。对方负责版式、字体、材料、主体和出图；本Skill只提供用色建议。两套分别安装，按各自许可使用，本包不包含或自动安装Punk。

用户已授权两者一起用时，按[搭配说明](references/punk-pairing.md)交接；Punk未安装也照常给出选色结果，不把选色任务卡在外部依赖上。不要把“推荐搭配”说成已经自动调用。

导出交接单：

```text
python3 <当前Skill目录>/scripts/palette.py handoff --id 30 --brief <brief.json> --out <输出目录>
```

它输出`palette-handoff.md`和`plan.json`，不调用Punk或生图服务。完整参数见[脚本用法](references/script-usage.md)。

## 交付检查

- 编号、颜色名、HEX和顺序与目录一致；61—79组的单色名称是补充描述，见[数据说明](references/data-notes.md)。
- 标题、小字和每块衬底分别算对比；照片、人物肤色、产品实色与带含义的图例按用户要求保留。对比数值针对给定HEX，实际成图由后续制作方复核。
- 色卡是AI视觉预览，精确配色以目录HEX为准。检查通过不等于训练了模型，也不代表所有文章的视觉效果都已验证。
