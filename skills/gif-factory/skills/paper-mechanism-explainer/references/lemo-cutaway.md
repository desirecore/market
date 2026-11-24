# 立体剖面联动：调用 lemo-opuscar

本分支使用 **[Lemo-Opuscar by Lemomo（LemoLab）](https://github.com/lemomo-ai/lemo-opuscar) 的 `lemo-opuscar` Skill**。已公开的齿轮片实际调用了该 Skill，并复用了其齿形、描边代码及材质、剖面渲染方法。GIF 工厂增加的是入口、项目工作流和案例记录。

## 何时走这个分支

用户要看立体外壳打开、剖面内部、零件接触、共轴和传动速度关系时使用。已有验证为20→40、同轴18→36的两级减速教学装置；新机构重新建模，不能直接沿用这组齿数。三维人物或微缩人偶不属于本分支。

## 依赖与调用

先确认当前环境是否已有 `lemo-opuscar` Skill。有则读取其入口并按其当前规范制作。没有则说明缺少该外部依赖，按上游[安装说明](https://github.com/lemomo-ai/lemo-opuscar/blob/main/README.zh-CN.md#安装)准备：上游给其他 agent 的 Skill 路径为 [`plugin/skills/lemo-opuscar/`](https://github.com/lemomo-ai/lemo-opuscar/tree/main/plugin/skills/lemo-opuscar)。不能把 Claude 专用安装命令直接当作 Codex 命令。

安装 GIF 工厂会得到这份调用说明及参考抽帧；不会同时安装 Lemo-Opuscar 的 Skill、风格库、渲染运行时、模型或外部服务。不要将上游文档复制进本包再统一标成 MIT；其代码与文档许可分别见[上游 LICENSE](https://github.com/lemomo-ai/lemo-opuscar/blob/main/LICENSE)。

## 本项目的制作顺序

1. 沿用用户选题和已认可的效果，给外部 Skill 明确风格名“分色机械图解 / Color-Coded Mechanism”、主体、时长、画幅与声线。首次尝试可做约5秒的小样；已认可则继续完整片，不重复选声或审批同一方案。
2. 核实原理，写本期旁白、镜头与参数。先明确谁驱动谁、齿数与中心距、哪些零件刚性共轴，再安排剖面和镜头。使用教学模型时记下简化范围。
3. 使用 `lemo-opuscar` 的方法与渲染工具建立本期工程；只剖开外壳，保留被解释零件的接触关系。主轴角度统一驱动所有从动件，跨特写、全景和数字读数共用状态。
4. 配音跟随用户当前选择。齿轮案例用了 Clipchamp 的云杰 HD，具体声线名为 `Yunjie Dragon HD Flash Latest`，默认音调、1倍速；需要时读[Clipchamp 配音流程](clipchamp-voiceover.md)。这是一项微软在线服务。
5. 取得实际旁白后排时序，给“一圈/半圈”等动作留完整观察周期。用转写辅助核对内容与字幕，配乐和机械点击按同一时轴合成。画面改动可复用已有音轨。
6. 检查啮合、共轴、剖切、盖板路径、文字遮挡和数圈结果，再导出成片、封面、字幕、工程及来源说明。运动学演示不等于制造或受力仿真，自动转写也不代替人耳试听。

齿轮片实际工具组合：Codex + lemo-opuscar Skill + Three.js / WebGL + Clipchamp 云杰 HD + Whisper 转写 + FFmpeg 合成。该组合是案例记录，具体安装和版本按所在环境确认。

## 制作来源怎样写

项目的来源说明应明确实际使用的 Skill、作者与代码范围，并区分本期新增内容。齿轮案例的表述可直接沿用：

> 本片由 Codex 调用 Lemo-Opuscar by Lemomo（LemoLab）的 lemo-opuscar Skill 制作，使用其分色机械图解风格，并复用齿形生成、描边代码及材质与剖面渲染方法；齿轮箱布局、讲解稿、镜头、传动时序和声音编排为本期定制。

查看[完整案例及来源](https://github.com/WoYun520/gif-factory/tree/main/examples/mechanism-explainers/gear-reduction-cutaway)。本包不强制给成片加作者水印或来源底条，署名放在工程与发布说明中。
