# 渲染与字体适配

新字稿默认用 `scripts/render_ink_signature.py`。需要 Python 3、Pillow、NumPy；导出 MP4、GIF 需要 FFmpeg，检查视频参数用 ffprobe。本地渲染不调用付费 API，生图另用当前环境的图像工具。

先按[字体适配](font-adaptation.md)由代理看图、准备分层，再运行脚本。基础配置不需要手填起笔点、尾巴路径和碎片参数：

```json
{
  "art": "art.png",
  "masks": {
    "upper": "upper.png",
    "first": "first.png",
    "tail": "tail.png"
  },
  "background": [29, 30, 33],
  "effect": "write"
}
```

路径相对于配置文件。原图可用 RGB 或带真实透明度的 RGBA，遮罩为同尺寸黑白 PNG；各层互斥。原图尺寸直接决定视频尺寸，宽高需为至少 32 的偶数。没有长尾时省略 `tail`，不要凭空补一条。

纯文字款省略 `upper`，把连笔字身和独立点画都放在 `first`。这时从第 0.30 秒开始写字身，默认写 1.20 秒，末锋仍可单独放在 `tail`。

普通款用 `write`。用户明确要墨迹聚合时，增加 `rest` 遮罩并选 `ink-fragments`；该层会切成保有原色和笔画的碎片，移动、转动后回到原位置。其余部分照常书写，不自动给所有字加粒子。

```bash
python3 -m pip install Pillow numpy
python3 scripts/render_ink_signature.py --config assets/adaptive/Woyunjian/write.json --out /tmp/signature --plan-only
python3 scripts/render_ink_signature.py --config assets/adaptive/Woyunjian/write.json --out /tmp/signature
python3 scripts/audit_video.py /tmp/signature.mp4
```

`--plan-only` 不编码视频，输出 `.plan.png` 六张实际中间帧和 `.plan.json` 自动计算记录。有 `upper` 时前三张显示上方笔势，纯文字款前四张显示字身书写。正式导出为 MP4、循环 GIF、定格 PNG 和 JSON 参数记录；默认 4 秒、MP4 60fps、GIF 25fps。

墨迹聚合的现成配置是 `assets/adaptive/Woyunjian/ink-fragments.json`。这两份配置共用同一张已选字稿及分层，均不指定坐标、路径或字体名称。

## 配色预设

沿用现有字稿和书写节奏时，在配置的顶层加 `"palette": "hello-split"` 即可换色。预设同时指定成片底色和墨色，`background` 仍用于识别不透明原图的墨迹。省略 `palette` 时沿用原有颜色。

| 配置值 | 效果 |
| --- | --- |
| `macaron` | 深灰底，浅粉、淡紫、薄荷绿渐变 |
| `cola-red` | 红底，奶白墨迹 |
| `hello-split` | 深底，珊瑚粉、杏黄、天蓝、淡紫沿斜向柔和过渡 |
| `google-color` | 深底，蓝、红、黄、蓝、绿从左到右渐变衔接 |
| `sea-salt-soda` | 深青底，青蓝到柠檬黄渐变 |
| `retro-print` | 奶油纸色底，朱红和深靛蓝在中间渐变衔接 |
| `night-gradient` | 深紫底，电蓝、紫色、紫红渐变 |

渐变以整张字稿的墨迹范围为基准。分色款保留各段的主色，在交界处逐渐过渡。写过的笔画保留各自的颜色。带真实透明度的字稿直接保留 alpha；RGB 字稿根据原底色与附近笔画估算边缘的浓淡，保留抗锯齿和飞白的层次。RGB 图片已经丢失原始透明度，需要精确保留透明边缘时，优先提供带真实透明度的 PNG。

纯文字示例可直接重跑：

```bash
python3 scripts/render_ink_signature.py --config assets/adaptive/word-only/Likka/config.json --out /tmp/likka
```

## 需要时再改参数

| 配置 | 什么时候改 |
| --- | --- |
| `upper_pen.start_point`、`first_pen.start_point`、`tail_pen.start_point` | 自动起笔方向不合当前笔势时，由代理填当前画布的 `[x,y]` |
| `upper_path`、`first_path`、`tail_path` | 交叉、回环需要明确先后时，由代理给当前稿的一串 `[x,y]` 路径点；精确逐笔仍需另分笔画层 |
| `upper_pen.stroke_paths`、`first_pen.stroke_paths`、`tail_pen.stroke_paths` | 复杂连笔按顺序给出多段路径，每段都是 `[x,y]` 点列；首尾相接时连续书写，分开的点画抬笔后再写。和对应的单条 `*_path` 二选一 |
| `upper_pen.front_duration`、`first_pen.front_duration`、`tail_pen.front_duration` | 调整笔头经过局部墨迹的过渡；不要把整层当作透明度淡入 |
| `upper_pen.acceleration_power`、`first_pen.acceleration_power` | 快写加速度，默认 1.3；末锋使用减速曲线 |
| `fragments.cell_width`、`cell_height`、`rotation`、`drift` | 已选效果需要更完整墨块或更小动作时覆盖自动值 |
| `timing` | 调整 `upper_start/end`、`first_start/end`、`tail_start/end`、`fade_start/end`；先保留用户已认可的节奏 |
| `duration`、`fps`、`seed` | 总时长、视频帧率和墨迹碎片随机种子，默认 4、60、731 |

脚本估计笔宽后计算默认参数，沿当前墨迹而非水平坐标推进。分离点画用不可见的抬笔时间接续，空白处不会生出线。自动路径在交叉处可能分叉；普通连笔出现扩散、同时长出支线时，改用 `stroke_paths` 按当前字稿安排上挑、回转和落笔。它只让笔头经过的当前笔势显现，笔宽按每段墨迹估计。Likka 示例已按这个方法安排连续字身与最后的点画，字身用 1.60 秒写完；具体路径见示例配置。路径由代理根据当前稿准备，不让用户填坐标，也不套用其他名字的点位。这是视觉书写顺序，不宣称从静态图恢复了书写者的真实笔顺。

遮罩重叠、明显漏分墨迹、字身缺失、指定的 `upper` 遮罩为空、路径异常或未成字就进入淡出时，脚本会报错。修当前输入后重跑，不在最后贴完整字稿掩盖缺笔。自动结果不能代替正常播放检查。

## 九宫格与旧案例

九个单款完成后运行 `make_grid.py --out /tmp/grid --videos FILE1 ... FILE9 --labels NAME1 ... NAME9`。输入用四秒成片；输出 1440×1440 MP4、定格和 1080×1080 GIF。标签用本机有授权的中文字体。ZIP 保留成片、配置和必要字稿，不放机器专用绝对路径或私人参考截图。

要从随包字稿重跑九种字体，运行 `python3 scripts/render_collection.py --manifest assets/adaptive/multifont/cases.json --out /tmp/signature-multifont`。网格标签由 Pillow 绘制，不要求 FFmpeg 带 `drawtext`；字体可用 `--font` 指定。

`render_signature.py` 保留重跑 `assets/examples` 和 `assets/chinese` 旧配置，需要额外安装 SciPy；其组件编号和贝塞尔末锋坐标只属于对应原图。没有末锋路径时的横向显露只是旧版兼容方式，新字体走上面的适配流程。

`render_semantic_signature.py` 保留重跑星屑、雨丝两个旧演示，使用 Pillow、NumPy 和 FFmpeg。它不是两组原版九宫格的生成源码；新字稿的墨迹碎片效果用 `render_ink_signature.py`，不要混称。
