<!-- market-package-note -->
This DesireCore market package is a slim optional snapshot of WoYun520/gif-factory@e89003a4a6ca4fd0e9e39c8859851b58c82bc368. Example renders, GALLERY.md and rendered style-catalog / english-title / signature previews are not shipped; they remain at that pinned commit. See UPSTREAM.md.

# GIF 工厂

把这句话发给 Codex 安装：

> 帮我安装 GIF 工厂：[https://github.com/WoYun520/gif-factory](https://github.com/WoYun520/gif-factory)

安装 Skill 是加入制作说明和脚本；运行时需要的工具按功能分别准备，见[需要装什么](GUIDE.md#需要装什么)。

装好后，给一张图、一段文字，或直接说想做什么。角色图、场景图、片名、字稿和配乐都可以自己提供，缺的部分再一起补。

[表情包](#stickers) · [光栅变画卡](#cards-transforms) · [动态海报](#posters-type) · [动态签名](#dynamic-signatures) · [电影片头](#cinematic-title-lettering) · [文章封面配色](#article-cover-palette) · [动态绘本](#storybooks) · [品牌短片](#brand-films) · [vibe 知识大赏](#mechanism-explainers)

[分类说明](styles/README.md) · [完整作品库](GALLERY.md) · [使用指南](GUIDE.md) · [下载项目](https://github.com/WoYun520/gif-factory/archive/refs/heads/main.zip)

## 仓库里有哪些 Skill

一般安装 GIF 工厂总入口即可，直接说需求。如果只用某个功能，也可以让 Codex 单独安装对应的 Skill 文件夹。

| Skill | 能做什么 | 说明 |
| --- | --- | --- |
| GIF 工厂总入口 | 根据需求选择表情包、卡片、海报、签名、片头、文章配色、绘本、品牌短片或「vibe 知识大赏」的做法 | [查看](SKILL.md) |
| 动态签名 | 支持多种字体和自定义字稿，把名字与意象融成动态签名 | [查看](skills/dynamic-art-signature/SKILL.md) |
| 电影片头 | 中文50种写法，英文50款基础字体与装饰封面；可用自己的字体、照片或字稿 | [查看](skills/cinematic-title-lettering/SKILL.md) |
| 文章封面配色 | 按文章选配色，写清标题、底色和点缀怎么搭；推荐搭配Punk制作封面 | [说明与安装](skills/article-cover-palette/README.md) |
| 动态绘本 | 让插画做完一个动作，再翻到下一页，能做横屏或竖屏 | [查看](skills/compact-storybook/SKILL.md) |
| vibe 知识大赏 | 四种内置风格，含同屏实验；立体剖面联动使用外部 lemo-opuscar Skill | [查看](skills/paper-mechanism-explainer/SKILL.md) |

<a id="stickers"></a>
<a id="表情包展厅"></a>

## 表情包

可以做像素、插画、真人、宠物和粘土角色。既能轻轻点头、摇摆，也能让角色完整做完挥手、行礼等动作。

<table>
<tr>
<td align="center"><a href="styles/pixel-light/STYLE.md"><img src="docs/previews/pixel-light.gif" alt="像素表情包" width="180"></a><br>像素</td>
<td align="center"><a href="styles/illustrated-actions/STYLE.md"><img src="docs/previews/illustrated-actions.gif" alt="插画角色动作" width="180"></a><br>插画</td>
<td align="center"><a href="styles/photo-pets/STYLE.md"><img src="docs/previews/photo-pets.gif" alt="宠物表情包" width="180"></a><br>宠物</td>
</tr>
</table>

<a id="pixel-games"></a>
<a id="illustration-anime"></a>
<a id="people-pets"></a>
<a id="materials-mascots"></a>

[像素轻动效](styles/pixel-light/STYLE.md) · [像素完整动作](styles/pixel-actions/STYLE.md) · [插画](styles/illustrated-actions/STYLE.md) · [真人](styles/photo-people/STYLE.md) · [宠物](styles/photo-pets/STYLE.md) · [粘土吉祥物](styles/clay-mascot/STYLE.md) · [全部案例](GALLERY.md#表情包展厅)

> 用这张角色图做 12 张中文表情包，每张表情和姿势不同，加轻微点头或摇摆，文字用我给的这组台词。

<a id="cards-transforms"></a>
<a id="电子光栅卡展厅"></a>

## 光栅变画卡

让一张卡片在两种样子之间切换，比如人物与面罩、日常与变身、产品的两种配色。

<a href="styles/lenticular/STYLE.md"><img src="docs/previews/lenticular.gif" alt="光栅变画卡" width="240"></a>

[看做法](styles/lenticular/STYLE.md) · [全部案例](GALLERY.md#电子光栅卡展厅)

> 用这两张图做一张变画卡，来回切换两种状态，标题保持不动。

<a id="posters-type"></a>
<a id="动态海报展厅"></a>

## 动态海报

可以保留原画，让人物和文字一起变化；也可以把人物、背景和大字重新设计成一张完整海报。

<table>
<tr>
<td align="center"><a href="styles/type-linked/STYLE.md"><img src="docs/previews/type-linked.gif" alt="保留原画，人物和字体一起动" width="240"></a><br>保留原画，字体联动</td>
<td align="center"><a href="styles/comic-fusion/STYLE.md"><img src="docs/previews/comic-fusion.gif" alt="人物背景和文字一起设计的漫画海报" width="240"></a><br>人物、背景和字一起设计</td>
</tr>
</table>

[字体联动](styles/type-linked/STYLE.md) · [漫画印刷风格](styles/comic-fusion/STYLE.md) · [全部案例](GALLERY.md#动态海报展厅)

> 用这个角色做一张动态宣传海报，人物从安静切到登场，大字一起展开，日期和地点固定。

<a id="dynamic-signatures"></a>

## 动态签名

动态签名分成下面四种。每种都有动图和做法，选喜欢的效果，再换成你的名字、字体和颜色。也可以直接用你提供的字稿。

| 风格 | 主要效果 | 看预览和做法 |
| --- | --- | --- |
| 纯文字连笔 | 沿字迹写出名字，配单色或渐变色 | [打开](skills/dynamic-art-signature/references/styles.md#word-only) |
| 意象融字 | 鸟、月亮、植物等融进名字的笔画 | [打开](skills/dynamic-art-signature/references/styles.md#motif-fusion) |
| 乐器融字 | 琴弦、笛身、音孔成为字的一部分 | [打开](skills/dynamic-art-signature/references/styles.md#instrument-fusion) |
| 墨迹聚合 | 墨迹碎片移动、聚拢，最后成字 | [打开](skills/dynamic-art-signature/references/styles.md#ink-assembly) |

同一张字稿可以换成七种配色，笔迹和书写节奏保留。

<a href="skills/dynamic-art-signature/assets/media/multifont/MultiFont_Nine_Grid.mp4"><img src="docs/previews/dynamic-signatures-multifont.gif" alt="九种字体方向的乐器融字动态签名，支持自定义" width="560"></a>

[多字体视频](skills/dynamic-art-signature/assets/media/multifont/MultiFont_Nine_Grid.mp4) · [九款字体与自定义说明](skills/dynamic-art-signature/references/multifont.md) · [中英文案例](examples/dynamic-signatures/README.md) · [早期乐器案例](skills/dynamic-art-signature/references/instrument-semantic.md) · [Skill](skills/dynamic-art-signature/SKILL.md)

> 做一款「卧云间＋竹笛＋月白到浅青渐变」的动态签名，让乐器融进笔画，沿用仓库的快写和慢收锋节奏。

> 用我提供的字稿，保留字体和颜色，自定义一款动态签名；书写、墨迹聚合和收锋按字形来。

<a id="cinematic-title-lettering"></a>

## 电影片头

中文50种字的写法，另有英文50款基础字体和装饰封面。中文选 F 编号，英文选 EN 编号；都支持自定义字体和字稿。选喜欢的编号，换成你的片名，字和场景一起设计。新增的十款手写风格是 F41–F50，每款都有原稿、白底字稿、换句对照和独立场景。也可以提供自己的照片、文案、字体参考或现成字稿，只做你需要的部分。

<a href="skills/cinematic-title-lettering/references/handwriting-stability.md"><img src="skills/cinematic-title-lettering/assets/style-catalog/previews/handwriting-scenes-01.jpg" alt="十款手写电影片头 F41–F50，每款各有片名和场景" width="720"></a>

[50 种字形与原图](skills/cinematic-title-lettering/references/style-catalog.md) · [十款手写字怎么用](skills/cinematic-title-lettering/references/handwriting-stability.md) · [五种排法](skills/cinematic-title-lettering/references/layout-recipes.md) · [三联图](skills/cinematic-title-lettering/references/promo-triptychs.md) · [Skill](skills/cinematic-title-lettering/SKILL.md)

英文每款都有独立场景、原始字体文件和装饰参考，分成五张图，每张十款。

<a href="skills/cinematic-title-lettering/references/english-titles.md"><img src="skills/cinematic-title-lettering/assets/english-titles/previews/01-10.jpg" alt="英文装饰片头 EN01–EN10，每张十款，共五组" width="720"></a>

[看英文50款与五组大图](skills/cinematic-title-lettering/references/english-titles.md) · [字体与授权](skills/cinematic-title-lettering/assets/english-titles/source-notes.md)

> 用 EN25 的写法做 “Letters from Summer”，放大首字母，让收笔融进海岸线。

> 用我提供的风景图和片名，按 F13 粉笔拙块做一张横向片头，字写得有点特别。

<a id="article-cover-palette"></a>

## 文章封面配色

这套Skill负责给文章选配色，不负责制作封面。给一篇文章、标题或现有封面，它会推荐颜色并说明底色、标题字、小字和点缀怎么分。支持指定编号、自定义HEX，也可以保留合适的原配色。100套是颜色库，文章仍按少数用途判断。

推荐搭配[Adrian Punk的Punk-Posters](https://github.com/adrianpunk/Punk-Posters)使用：本Skill选颜色，Punk负责构图、字体、风格和出图。两套分别安装，按各自说明和许可使用，本包不附带Punk。

<table>
<tr>
<td><a href="skills/article-cover-palette/assets/cards/030-落日与海.jpg"><img src="skills/article-cover-palette/assets/cards/030-落日与海.jpg" alt="030落日与海：橙、米色、钴蓝" width="350"></a></td>
<td><a href="skills/article-cover-palette/assets/cards/070-数字先锋.jpg"><img src="skills/article-cover-palette/assets/cards/070-数字先锋.jpg" alt="070数字先锋：黄、蓝、黑、白" width="350"></a></td>
</tr>
</table>

[说明与安装](skills/article-cover-palette/README.md) · [100张色卡＋色号](skills/article-cover-palette/references/color-cards.md) · [用途和标题搭法](skills/article-cover-palette/references/palette-table.md) · [Skill](skills/article-cover-palette/SKILL.md)

附100张1200×400现成色卡和完整配色表。选色、查表和导出交接单只用Python 3，不需要FFmpeg或画图工具；实际封面由后续工具制作。

> 读这篇文章，给一套主推配色，必要时再给两套有区别的备选。说清颜色怎么分，整理成配色方案，我再交给Punk做封面。

<a id="storybooks"></a>

## 动态绘本

让插画做完一个小动作，停一下，再翻页。可以做独立动画，也可以做成横屏翻书或适合手机看的竖屏书页。

<a href="examples/storybooks/tea-party/realbook-writing.mp4"><img src="examples/storybooks/tea-party/realbook-writing-preview.gif" alt="动态绘本横屏翻书与正文书写" width="640"></a>

[看做法](styles/compact-storybook/STYLE.md) · [横屏和竖屏完整案例](examples/storybooks/tea-party/README.md) · [Skill](skills/compact-storybook/SKILL.md)

> 把这个故事做成动态绘本，一页完成一个动作，配上正文和音乐，先做一页小样。

<a id="brand-films"></a>
<a id="品牌宣传片展厅"></a>

## 品牌短片

让吉祥物和产品一起演一个小故事，比如拿起面包、装进包装、露出店名。可以用自己的角色、产品图和品牌素材。

<a href="examples/brand-films/manman-bakery/film.mp4"><img src="examples/brand-films/manman-bakery/preview.gif" alt="慢慢面包店品牌短片" width="640"></a>

[看案例和工程](examples/brand-films/manman-bakery/README.md) · [制作方法](references/brand-film.md)

> 用这套吉祥物和产品图做一条 15 秒品牌短片，让角色亲手把产品装进包装，给我成片和可修改的工程。

<a id="mechanism-explainers"></a>

## vibe 知识大赏

把一个物件的机关、一种物理变化或一笔钱的来去讲成能看见的动作。内容可选生活机关、机械结构、物理现象、金融机制；画面有摄影纸艺、彩色贴纸、复古档案、同屏实验四种内置风格，以及使用外部 Skill 的立体剖面联动。默认无个人水印，延续作品时保留已选声线和节奏。

先看两分钟无水印精选，包含拉链、机械表、弹子锁、差速器、按动笔，以及金融与消费机制。

<a href="examples/mechanism-explainers/highlights/film.mp4"><img src="examples/mechanism-explainers/highlights/preview.gif" alt="两分钟 vibe 知识大赏精选，摄影纸艺、复古档案与彩色贴纸的静音节选" width="240"></a>

[观看120秒完整合集](examples/mechanism-explainers/highlights/film.mp4) · [片段、字幕与声音来源](examples/mechanism-explainers/highlights/README.md)

<table>
<tr>
<td align="center" valign="top"><a href="examples/mechanism-explainers/loan-creation/film.mp4"><img src="examples/mechanism-explainers/loan-creation/preview.gif" alt="摄影纸艺：贷款创造存款，静音节选" width="180"></a><br>摄影纸艺<br>贷款创造存款 · 42.73秒</td>
<td align="center" valign="top"><a href="examples/mechanism-explainers/coupon-funding/film.mp4"><img src="examples/mechanism-explainers/coupon-funding/preview.gif" alt="彩色贴纸：优惠券到底谁买单，静音节选" width="180"></a><br>彩色贴纸风<br>优惠券到底谁买单 · 50.4秒</td>
<td align="center" valign="top"><a href="examples/mechanism-explainers/unit-price-archive/film.mp4"><img src="examples/mechanism-explainers/unit-price-archive/preview.gif" alt="复古档案：大包装一定更划算吗，静音节选" width="180"></a><br>复古档案记录<br>大包装一定更划算吗 · 22.17秒</td>
</tr>
</table>

点击预览看带旁白的完整视频。三支是制作方法与风格示例，示例参数不代表真实产品或当前报价；每支附封面、字幕、数据模型及声音署名，不含完整渲染工程。

[怎么选风格](styles/paper-mechanism-explainer/STYLE.md) · [案例与来源](examples/mechanism-explainers/README.md) · [独立 Skill v0.6.0](skills/paper-mechanism-explainer/SKILL.md)

### 同屏实验：内置独立流程

相同起始条件、同一时刻操作，只改变一个关键变量，先看结果差异，再用局部透视、电流、受力或能量图解释。三维装置与渲染由本项目独立制作，**不调用 lemo-opuscar Skill**。

<a href="examples/mechanism-explainers/copper-magnet-same-screen/film.mp4"><img src="examples/mechanism-explainers/copper-magnet-same-screen/preview.gif" alt="同屏实验：完整铜管与纵向开缝铜管中的磁铁下落，静音节选" width="480"></a>

[观看79秒完整视频](examples/mechanism-explainers/copper-magnet-same-screen/film.mp4) · [铜管5秒小样](examples/mechanism-explainers/copper-magnet-same-screen/look-test.mp4) · [吸管5秒小样](examples/mechanism-explainers/copper-magnet-same-screen/straw-look-test.mp4) · [流程、三维源码与模型](examples/mechanism-explainers/copper-magnet-same-screen/README.md) · [同屏实验制作说明](skills/paper-mechanism-explainer/references/same-screen-experiments.md)

完整片为1920×1080、24fps，云杰HD配音，含字幕、原创轻配乐和拟音。运动、场线和能量采用有范围说明的原理模型，不作为实测落时或完整电磁仿真。

### 立体剖面联动：使用 lemo-opuscar Skill

**这期《齿轮减速原理》由 Codex 调用 [Lemo-Opuscar by Lemomo（LemoLab）](https://github.com/lemomo-ai/lemo-opuscar) 的 `lemo-opuscar` Skill 制作**，使用其分色机械图解风格，复用了齿形、描边代码及材质、剖面渲染方法。齿轮箱布局、讲解稿、镜头、传动时序和声音编排为本期定制。

<a href="examples/mechanism-explainers/gear-reduction-cutaway/film.mp4"><img src="examples/mechanism-explainers/gear-reduction-cutaway/preview.gif" alt="使用 lemo-opuscar Skill 制作的立体剖面齿轮减速讲解，静音节选" width="480"></a>

[观看76.67秒完整视频](examples/mechanism-explainers/gear-reduction-cutaway/film.mp4) · [5秒效果小样](examples/mechanism-explainers/gear-reduction-cutaway/look-test.mp4) · [制作流程与来源](examples/mechanism-explainers/gear-reduction-cutaway/README.md) · [外部 Skill 调用说明](skills/paper-mechanism-explainer/references/lemo-cutaway.md)

GIF 工厂收录调用入口和案例。**上游 Skill 与渲染运行时需另行安装**；安装 GIF 工厂不会同时带上 Lemo-Opuscar 的完整风格库。原作者链接、代码复用范围与各自许可见案例的[CREDITS](examples/mechanism-explainers/gear-reduction-cutaway/CREDITS.md)。

> 用彩色贴纸风讲“优惠券到底谁买单”，跟着一笔订单看顾客、商家和平台的资金关系。先核实规则，再给我无水印成片、封面和可编辑工程。

> 用摄影纸艺讲拉链怎么扣上，做出剖面里的咬合动作；文字和结构可编辑。

> 用同屏实验讲“铜管开一条纵缝，磁铁为什么落得更快”，控制比较条件，再用透视和电流回路解释，沿用我选的配音，交付成片、字幕、封面与工程。

> 调用 lemo-opuscar Skill，用立体剖面和零件联动讲清齿轮减速，沿用我选的声线，交付成片、字幕、封面和可编辑工程，并写清使用了 Lemo-Opuscar。

## 使用说明

想换台词、配色、画风、尺寸或动作，直接说。已经选好的稿子和要求会继续沿用。完整系列和试作的说明放在[作品库](GALLERY.md)，具体怎么提需求看[使用指南](GUIDE.md)。

## 开源许可

本仓库原创制作脚本与 Skill 说明采用 [MIT](LICENSE)。外部 Lemo-Opuscar Skill、文档和代码分别按其[上游许可](https://github.com/lemomo-ai/lemo-opuscar/blob/main/LICENSE)处理，来源与使用范围见[齿轮案例说明](examples/mechanism-explainers/gear-reduction-cutaway/CREDITS.md)。动态海报的角色与参考设计语言不随代码转授商业权利，见[案例说明](examples/dynamic-posters/p5-integrated/README.md)。电子光栅卡中的角色 IP、网络照片与他人插画不随代码一并授予 MIT 权利，出处及使用边界见[案例来源说明](examples/lenticular-cards/README.md)。

第三方配乐和字体按各自许可使用；面包店案例的来源与署名见 [CREDITS](examples/brand-films/manman-bakery/CREDITS.md)，vibe 知识大赏的声音及画面来源见[各案例说明](examples/mechanism-explainers/README.md#来源与复用)。

