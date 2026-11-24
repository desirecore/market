# 动态艺术签名

先看[四种风格的动图和做法](../skills/dynamic-art-signature/references/styles.md)：纯文字连笔、意象融字、乐器融字、墨迹聚合。名字、字体、字稿和颜色都可以自己提供；有物体时，让它成为笔画的一部分。

现在支持多种字体，也可以自定义。可以指定书体、描述想要的感觉，或提供自己的字稿与字体参考。先看[九种字体方向与自定义方法](../skills/dynamic-art-signature/references/multifont.md)。

纯文字款直接写字身，末端可慢收锋。有独立上方意象时，两笔分开、间隔约 1 秒。默认无底印、无轻震、无回弹。手写质感指提按、粗细与尖锋，不默认金属、粉笔或立体材质。

同一张字稿可以选择[七种配色](../skills/dynamic-art-signature/references/rendering.md#配色预设)，换颜色时保留原来的笔迹和书写节奏。

字体由当前字稿决定怎么动：代理重新检查粗细、连笔、点画和回钩，脚本据此计算起笔、收锋与可选碎片参数。用户可以直接提供字稿，不需要填写组件编号或坐标；详见[字体适配](../skills/dynamic-art-signature/references/font-adaptation.md)。

[九款样例](../examples/dynamic-signatures/README.md) · [风格入口](../styles/dynamic-signatures/STYLE.md)


支持中英文名字。中文默认草书，可按要求切换行书；两字与三字都需保留完整名字及用户选定的意象。三字沿用已定的书写节奏，重新设计排布与末字收锋。详见[中文规则](../skills/dynamic-art-signature/references/chinese.md)。

乐器入字时让乐器和字共享笔画。粒子按字意成字时，为每种粒子设计对应的动势和落笔位置。见[两组定稿九宫格与可复现案例](../skills/dynamic-art-signature/references/instrument-semantic.md)。
