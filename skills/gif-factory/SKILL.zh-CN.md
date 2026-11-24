<!-- locale: zh-CN -->

# GIF 工厂

## 范围与来源

这个可选 MIT 本地包收录 GIF 工厂技能、五个配套技能、脚本、字体、模板、参考说明、100 张文章封面色卡、纸艺机关视觉参考，以及安装树中的 [LICENSE](LICENSE)。详见 [UPSTREAM.md](UPSTREAM.md) 和 [references/market-packaging.md](references/market-packaging.md)。

上游技能原文见 [references/upstream-skill.md](references/upstream-skill.md)。目录标识为 `gif-factory`；上游 frontmatter 的 name 是 `pixel-gif-sticker-pack`。

示例成片、`GALLERY.md`、`docs/` 预览，以及已渲染的风格目录 / 英文片名 / 签名 / 片头预览**不在**本包中，仍位于固定上游提交 `e89003a4a6ca4fd0e9e39c8859851b58c82bc368`。

## 前提

- 常用表情包导出（`export_pack.py` 及相关脚本）需在私有环境中准备 Python 3 与 Pillow
- 仅在使用 `--preview` 写出 MP4 时需要 FFmpeg
- DesireCore 兼容客户端
- 可选的外部 `lemo-opuscar` 技能不随包提供；若走该纸艺机关工作流请另行安装
- 本包不附带生图模型或付费服务
