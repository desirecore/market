# 乐器入字、粒子按字意成字

## 字形与动效

- 先写清楚乐器与哪个字的哪一笔共用轮廓，再定上方独立意象。比如「枕星」把「星」的外弧和底横画成竖琴框，琴弦落在框内。「雨巷」把口琴的管身和音孔嵌进「雨」的上横。用笔画的提按和留白交代乐器结构，同时保证名字可读。
- 给目标字或目标笔画单独做遮罩。先给粒子匹配字意与动势，例如星屑聚向琴弦和「星」的笔画，雨丝向下落入「雨」，「听澜」的水珠沿连笔流入「澜」，收锋带涟漪。让粒子落点触发对应位置的墨迹显现，直到目标区域形成完整的字。
- 上方意象先出，停顿后下方书写和粒子成字开始。保留空白开场和独立的上笔停顿，主笔快写，末锋减速，成字后留停顿再淡出。普通两笔签名沿用原有无粒子默认设置。
- 逐款查看四个画面：上笔停顿、粒子尚在途中、粒子落入笔画、字形完整的定格。用单款尺寸和九宫格缩略尺寸核对乐器与字的共用部位、中文字辨识、粒子落点、收锋和循环。拼格时使用九段实际动画。

换字体时按[字体适配](font-adaptation.md)重新分出乐器共用部位。新稿的墨迹碎片效果用[适配渲染器](rendering.md)的 `ink-fragments`：碎片来自当前笔画，粗细、位移和扭转按字稿计算，顶部也沿自身墨迹写出。普通书写选择 `write`，不自动加入效果。

## 两组定稿

| 九宫格 | 顺序 | 下载 |
| --- | --- | --- |
| 第一组 | 卧云间·竹笛、枕星·竖琴、听澜·古琴、栖月·琵琶、竹隐·排箫、鹿鸣·小提琴、惊鸿·二胡、流萤·铃鼓、松风·洞箫 | [原版 MP4](../assets/media/instrument-semantic/Instrument_Semantic_Nine_Grid.mp4) · [封面](../assets/media/instrument-semantic/Instrument_Semantic_Nine_Grid.png) |
| 第二组 | 雾舟·陶埙、雪汀·扬琴、雁回·阮、花渡·箜篌、山眠·手碟、霜林·大提琴、雨巷·口琴、潮生·古筝、晚钟·编钟 | [原版 MP4](../assets/media/instrument-semantic/New_Instrument_Signatures_Nine_Grid.mp4) · [封面](../assets/media/instrument-semantic/New_Instrument_Signatures_Nine_Grid.png) |

两组原版 MP4 均为 1440×1440、30fps、4 秒。封面取自各组 2.7 秒成字帧。

## 复现单款

两款旧示例的定格字形取自上面的原版九宫格，下面的旧渲染器根据定格、上笔遮罩、目标区域和随机种子另做星屑或雨丝动画。它不是两组原版九宫格的生成源码。以下命令只复现仓库内这两个独立演示，新字稿使用上面的适配流程。

| 示例 | 配置及素材 | 成品 |
| --- | --- | --- |
| 枕星·竖琴 | [配置](../assets/instrument-semantic/Zhenxing-Harp.json) · [定格](../assets/instrument-semantic/Zhenxing-Harp.png) · [上笔遮罩](../assets/instrument-semantic/Zhenxing-Harp-upper.png) | [MP4](../assets/media/instrument-semantic/Zhenxing-Harp.mp4) · [GIF](../assets/media/instrument-semantic/Zhenxing-Harp.gif) |
| 雨巷·口琴 | [配置](../assets/instrument-semantic/Yuxiang-Harmonica.json) · [定格](../assets/instrument-semantic/Yuxiang-Harmonica.png) · [上笔遮罩](../assets/instrument-semantic/Yuxiang-Harmonica-upper.png) | [MP4](../assets/media/instrument-semantic/Yuxiang-Harmonica.mp4) · [GIF](../assets/media/instrument-semantic/Yuxiang-Harmonica.gif) |

从动态签名模块目录运行，环境需要 Python 3、Pillow、NumPy，以及 PATH 中的 FFmpeg 和 ffprobe。

```bash
python3 -m pip install Pillow numpy

python3 scripts/render_semantic_signature.py \
  --config assets/instrument-semantic/Zhenxing-Harp.json --out /tmp/zhenxing-harp
python3 scripts/render_semantic_signature.py \
  --config assets/instrument-semantic/Yuxiang-Harmonica.json --out /tmp/yuxiang-harmonica

python3 scripts/audit_video.py /tmp/zhenxing-harp.mp4
python3 scripts/audit_video.py /tmp/yuxiang-harmonica.mp4
```

每次导出 4 秒 MP4、循环 GIF 和 PNG 封面。配置中的素材路径相对于 JSON 文件，`target_polygon` 使用原始定格图的像素坐标。换字时重新标定上笔遮罩和目标区域，并按字意设计粒子轨迹。示例渲染器实现星屑和雨丝两种轨迹。
