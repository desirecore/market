# NOTICE — guizang-ppt

本技能（skill id：`guizang-ppt`）的内容 vendored（搬运）自上游开源项目，并在 DesireCore 官方市场以聚合形式分发。

## 来源 / Attribution

- **上游项目**：guizang-ppt-skill
- **作者 / Author**：歸藏（op7418）
- **规范源仓库 / Canonical repo**：https://github.com/op7418/guizang-ppt-skill
- **许可证 / License**：AGPL-3.0（见同目录 `LICENSE`）

DesireCore 仅对原作品进行打包分发与元数据适配（`_desirecore/frontmatter.yaml` 覆盖层），未修改 `references/`、`assets/`、`scripts/` 与 `SKILL.md` 的实质内容。上游 commit 溯源记录见 `_desirecore/upstream.json`。

## 许可与合规 / License & Compliance

本技能遵循 **AGPL-3.0**。再分发、修改或在网络服务中使用时，须遵守 AGPL-3.0 的条款（包括向用户提供对应源代码）。完整许可文本见 `LICENSE`。

## 维护方式 / Maintenance

- DesireCore 维护态（不随上游覆盖）：`_desirecore/`
  - `frontmatter.yaml`：DesireCore 市场 frontmatter 覆盖层
  - `upstream.json`：上游 commit / ref 溯源
- 同步更新：`node scripts/vendor/guizang-ppt.mjs --src <本地 clone 路径>`（或 `--ref <tag>` 联网克隆）
