# 照片来源与制作记录

这十款电影片头为静帧制作示例，使用已选字稿、实拍照片和用户提供的电影片名参考参与图像生成。画面经过 AI 重构，不标记为原始实拍。新片头已经检查文字和画面，但尚未逐款获得使用者确认。

## 输入的角色

- 自有基础字稿：本目录 foundations/01.png 至 10.png，来自用户选中的《长风追光越海》对照字稿。
- 场景照片：以下 Unsplash 来源页，原始照片未重复打包。
- 用户提供的电影片名参考：只用来研究层级、笔触和镜头关系，原始图片不随公开仓库分发。

## 场景照片

| 编号 | 片名 | 照片来源页 |
| --- | --- | --- |
| 01 | 晚风经过我 | [Unsplash](https://unsplash.com/photos/VTSF1xvrkZo) |
| 02 | 把晴天借给你 | [Unsplash](https://unsplash.com/photos/TeKyo8Eb_zY) |
| 03 | 晚点再告别 | [Unsplash](https://unsplash.com/photos/8BTrldpHRMY) |
| 04 | 无人应答 | [Unsplash](https://unsplash.com/photos/T1JoLRjcDbk) |
| 05 | 风把山路折弯 | [Unsplash](https://unsplash.com/photos/WAxAr6mVJKw) |
| 06 | 春天藏在树后 | [Unsplash](https://unsplash.com/photos/sQ79O-bkz9g) |
| 07 | 我们慢慢靠岸 | [Unsplash](https://unsplash.com/photos/iDzsLWUge1Q) |
| 08 | 远山没有回信 | [Unsplash](https://unsplash.com/photos/ofWmPiCYELQ) |
| 09 | 凌晨还有人醒着 | [Unsplash](https://unsplash.com/photos/P3xMgBn9N7Y) |
| 10 | 等潮水说完 | [Unsplash](https://unsplash.com/photos/b_Ko1SovFRI) |

## 重跑与保存

[prompts.json](prompts.json) 保留原始三参考提示词、十款题材与笔形描述、输入角色和 04 的修订记录。replay_prompt 是可移植的两参考版本：使用目录内的自有基础字稿，并从来源页取得相应照片；它不需要用户未公开的电影参考原图。两参考重跑与原始制作的输入不同，图像生成也可能波动，因此只承诺延续方向。精确保留本轮结果请使用目录中的独立 PNG。

总览是独立成品的拼版，脚本可从这些成品重新组装预览。原版总览含中文标注；跨平台脚本默认用编号与英文，不依赖本机中文字体。
