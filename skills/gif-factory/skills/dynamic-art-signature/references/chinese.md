# 中文草书与三字签名

## 字体与字形

- 默认采用有传统草书依据的连笔和省笔；收到行书要求时保留更完整字形、减少牵丝。不要仅给普通字体增加斜度，也不要把字形省成任意线团。
- 逐字核对名字，保留必要的偏旁辨识；先确认静态字形，再制作动效。用户已选择中文草书方向，并明确接受三字「卧云间」示例；九款扩展提供设计范围，不代表逐款单独批准。
- “手写质感”使用提按、粗细、转折、牵丝与收锋；少量飞白可以服务笔势，不要替换成金属、浮雕、发光或粗糙粉笔。

## 意象与排布

中文也必须有字以外可见的意象。用祥云、月弧、星轨、竹叶等抽象线条呼应字形，避免只有字，或在成字旁贴写实图标。上方意象与下方字身保持实际间隙，分别拥有独占墨迹。

两字保持疏密对比。三字按整体长短重新安排三个字的宽度、重心和连笔，不要挤进两字布局或丢字。让末字的长锋平衡整体；不要求所有字符等宽。沿用960×640画布，长名字必要时统一缩放与留边，不拉伸字形。

字体改版保留已确认的意象、渐变、节奏；只在实际几何需要时重画笔势。三字仍沿用两组视觉笔势，不把“三字”解释成“三笔”。

## 动效与中文收笔

默认沿用主流程的0.30秒空白、0.14秒上笔、1.02秒停顿、约0.16–0.18秒字身快写与0.72秒末锋减速。实际做法按[字体适配](font-adaptation.md)重新计算：看当前字稿的细线、提按、连笔和回钩，不复用另一张图的坐标。普通两笔签名保持干净底色，默认无轻震、回弹、粒子或音效。乐器入字与粒子成字按[专门流程](instrument-semantic.md)处理。

逐张重新检查连通组件，包括细小的飞白碎片和独立点画。上方意象碎片不可分到字身阶段；中文字点画不可误归意象。不要复用另一张图的组件编号。

- 对「月」的返回钩，按实际下行再回转的路径描画，不能水平擦除。
- 对「星」的底横或末字向右长尾，隔离完整末锋后顺向减速。
- 回环附近的末锋区域需排除相邻字身，避免提前出现或二次描画。画笔可扩大覆盖边缘，不能靠扩大遮罩掩盖错误归属。
- 当前栅格显现是两组视觉笔势和末端路径，不是自动恢复汉字逐笔笔顺；不要称为精确笔顺动画。

先检查停顿期只见意象、字身到末锋的交接、渐慢末端及循环重置。需要精确逐笔笔顺时另做独立笔画图层。

## 中文九宫格

先完成九段独立视频，再用make_grid.py合成。标签必须使用有中文字形的字体；可自动选择Noto CJK，或显式传入--font。禁止用静态拼图充当动态九宫格。

[九宫格封面](../assets/media/chinese/nine-grid.png) · [GIF](../assets/media/chinese/nine-grid.gif) · [MP4](../assets/media/chinese/nine-grid.mp4)

## 可复现案例

下列命令保留重跑旧稿；新字体和用户提供字稿默认使用[适配渲染器](rendering.md)。

从本模块目录运行：

```bash
python scripts/render_signature.py inspect --image assets/chinese/Woyunjian.png
python scripts/render_signature.py render --config assets/chinese/Woyunjian.json --out /absolute/output/woyunjian
python scripts/audit_video.py /absolute/output/woyunjian.mp4
```

配置路径相对配置文件；末锋坐标基于960×640，不能跨设计照搬。所有资源均为本次原创生成图与成品，不包含第三方参考截图。

| 名字 | 意象 | 渐变 | 资源 |
| --- | --- | --- | --- |
| 卧云 | 祥云 | 月白→浅青 | [原图](../assets/chinese/Woyun.png) · [配置](../assets/chinese/Woyun.json) · [GIF](../assets/media/chinese/Woyun.gif) · [MP4](../assets/media/chinese/Woyun.mp4) |
| 栖月 | 月弧 | 月白→淡靛 | [原图](../assets/chinese/Qiyue.png) · [配置](../assets/chinese/Qiyue.json) · [GIF](../assets/media/chinese/Qiyue.gif) · [MP4](../assets/media/chinese/Qiyue.mp4) |
| 枕星 | 星芒 | 浅金→淡紫 | [原图](../assets/chinese/Zhenxing.png) · [配置](../assets/chinese/Zhenxing.json) · [GIF](../assets/media/chinese/Zhenxing.gif) · [MP4](../assets/media/chinese/Zhenxing.mp4) |
| 听澜 | 海浪 | 珠白→青蓝 | [原图](../assets/chinese/Tinglan.png) · [配置](../assets/chinese/Tinglan.json) · [GIF](../assets/media/chinese/Tinglan.gif) · [MP4](../assets/media/chinese/Tinglan.mp4) |
| 竹隐 | 竹叶 | 嫩黄→翠绿 | [原图](../assets/chinese/Zhuyin.png) · [配置](../assets/chinese/Zhuyin.json) · [GIF](../assets/media/chinese/Zhuyin.gif) · [MP4](../assets/media/chinese/Zhuyin.mp4) |
| 鹿鸣 | 鹿角 | 象牙白→琥珀 | [原图](../assets/chinese/Luming.png) · [配置](../assets/chinese/Luming.json) · [GIF](../assets/media/chinese/Luming.gif) · [MP4](../assets/media/chinese/Luming.mp4) |
| 惊鸿 | 飞羽 | 珠白→朱红 | [原图](../assets/chinese/Jinghong.png) · [配置](../assets/chinese/Jinghong.json) · [GIF](../assets/media/chinese/Jinghong.gif) · [MP4](../assets/media/chinese/Jinghong.mp4) |
| 流萤 | 萤迹 | 浅金→青柠 | [原图](../assets/chinese/Liuying.png) · [配置](../assets/chinese/Liuying.json) · [GIF](../assets/media/chinese/Liuying.gif) · [MP4](../assets/media/chinese/Liuying.mp4) |
| 松风 | 松枝 | 月白→鼠尾草绿 | [原图](../assets/chinese/Songfeng.png) · [配置](../assets/chinese/Songfeng.json) · [GIF](../assets/media/chinese/Songfeng.gif) · [MP4](../assets/media/chinese/Songfeng.mp4) |
| 卧云间 | 祥云长弧 | 月白→冰青 | [原图](../assets/chinese/Woyunjian.png) · [配置](../assets/chinese/Woyunjian.json) · [GIF](../assets/media/chinese/Woyunjian.gif) · [MP4](../assets/media/chinese/Woyunjian.mp4) |
