<!-- locale: zh-CN -->

# 火柴人视频导演

## 范围与来源

这个可选 MIT 本地包收录火柴人视频导演技能、脚本与参考文档、字体及其 OFL 许可、音频库目录和许可证据、适合精简快照的风格样板，以及安装树中的 [LICENSE](LICENSE)。详见 [UPSTREAM.md](UPSTREAM.md) 和 [references/market-packaging.md](references/market-packaging.md)。

上游技能原文见 [references/upstream-skill.md](references/upstream-skill.md)。目录标识为 `stickman-video-director`；上游 frontmatter 的 name 是 `directing-stickman-videos`。

## 按需资源（仅在明确触发时下载）

以下分组对指定的 B 模式工作是必要的，但不随包安装：

- `required-for-B-audio` — `assets/b-audio-library/audio/` 下的配乐音频
- `required-before-B6` — `assets/b6/reference/` 下的 B6 风格锁定参考视频，包括 Eiffel V44 标准
- `required-for-B6-paint` — `assets/b6/paint/` 下的默认绘制底板
- `required-before-B8` — `assets/b8/` 下已批准的 B8 视觉参考和可移植回放包

只通过运行 [scripts/fetch-optional-assets.py](scripts/fetch-optional-assets.py) 并指定 [references/fetch-manifest.json](references/fetch-manifest.json) 来获取。脚本使用固定 pin 的 `raw.githubusercontent.com` URL，校验 SHA-256，不执行下载内容，也不会在安装时自动启动。请把文件写到本技能**之外**的绝对目录，再把 `assets/` 树复制或符号链接回来。

README 演示、技能 examples、公开展示、B5 本地基线，以及 B6 香港题材的进行中示例制作已排除，仍位于固定提交。

## 前提

- 若使用本地代码引擎渲染器，需要 Node.js 20 或更高版本，并在私有环境中安装 `package.json` 声明的依赖（`@napi-rs/canvas`、`sharp`）
- 部分 B 模式辅助脚本需要 Python 3；使用相关工作流时还须安装 `scripts/requirements-b8.txt` 中的包
- 按上游技能说明自行配置生成工具；本包不附带付费 API，也不会自动运行不受信任的远程代码
- DesireCore 兼容客户端
