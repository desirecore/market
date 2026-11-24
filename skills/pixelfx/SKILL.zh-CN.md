<!-- locale: zh-CN -->

# pixelfx

## 范围与来源

这个可选本地包包含 pixelfx Agent 技能、上游 MIT [LICENSE](LICENSE) 和 [NOTICE.md](NOTICE.md)。固定提交与文件哈希见 [UPSTREAM.md](UPSTREAM.md)。

特效库、Node 工具和仓库中的其他代码**不在**本包中；若要制作特效，请从同一 MIT 固定版本另行检出。`gallery/fonts` 不在仓库 MIT 许可范围内，也未收录。

可选的 pch CLI 仅在你选择运行远程脚本时才会安装，须自行审核该脚本。本包不会自动执行远程脚本。

在本地备好库之后，按 [references/upstream-skill.md](references/upstream-skill.md) 中的上游原文使用。

## 前提与风险

- 能够加载本技能的运行环境
- 需要制作特效时，从固定版本 `5294518ce7c72e48b6100a744596e0acf57f2826` 另行检出 pixelfx 库和 Node 工具
- 在运行任何 `curl | sh` 或类似的 pch 安装前，由操作者自行审核
