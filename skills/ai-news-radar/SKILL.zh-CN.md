<!-- locale: zh-CN -->

# AI 资讯雷达

## 范围与来源

使用完整本地 Python 包生成 AI 日报 JSON、评估公开信源质量，并可查看随包阅读器资源。先读[安装说明](README.md)、[来源与许可](UPSTREAM.md)和[信源接入指南](references/source-intake.md)。这是仅基于 LearnPrompt/ai-news-radar 提交 `689395109cc962a27c369bdd6fa50d1e090eb319` 维护的 MIT 本地版；包版本 `2026.11.24` 不是上游发行版。本技能供市场可选安装，不会自动全局安装。

## 前提与边界

需要 Python 3.11+、`uv` 或等效私有 Python 环境、[requirements.txt](requirements.txt) 中固定的依赖，以及用户选定公开信源的访问条件。依赖下载和正常采集需要联网；上游网站可能失效、修改条款或限流。必须如实报告信源错误。安装成功或离线夹具通过，不代表实时信源、认证服务、部署或邮件已验收。

安装目录必须保持只读。使用[安全启动器](scripts/run_daily_brief.py)：强制指定安装目录之外的绝对输出路径，并禁止写入字节码。未修改的[上游生成器](scripts/update_news.py) 默认使用相对输出路径；禁止在技能目录内直接运行默认命令。不得把虚拟环境、私人 OPML、生成数据、日志、token、cookies 或邮件正文写入安装目录或公共仓库。

## 准备私有运行目录

将 `SKILL_DIR` 设为实际安装目录的绝对路径，再选择其外部的私有工作目录。以下命令创建全新临时目录；需要保留结果时可改用私有持久目录。

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-news-radar.XXXXXX")"
export SKILL_DIR RUN_DIR
cp "$SKILL_DIR/feeds/follow.example.opml" "$RUN_DIR/follow.opml"
uv run --with-requirements "$SKILL_DIR/requirements.txt" python -B "$SKILL_DIR/scripts/update_news.py" --help
```

先确认用户希望跟踪的信源。仅修改私有 OPML 副本，参考随包[示例 OPML](feeds/follow.example.opml)，不要在聊天中收集凭据。随包 OPML 是公开示例，不是用户订阅清单。

## 生成日报

```bash
uv run --with-requirements "$SKILL_DIR/requirements.txt" python -B "$SKILL_DIR/scripts/run_daily_brief.py" --output-dir "$RUN_DIR/data" --window-hours 24 --rss-opml "$RUN_DIR/follow.opml"
```

从指定输出目录读取日报、最近 24 小时条目和信源状态 JSON。这些文件是运行产物，并非漏装资源。支持无历史数据首跑；不分发上游巨型历史归档或翻译缓存。已包含 [AI 相关性模块](scripts/ai_relevance.py)及可选[翻译词表](translation-glossary.txt)。离线冒烟仅使用夹具，不证明公开信源当前可用。

## 评估候选信源

遵循[接入指南](references/source-intake.md)和[产品方法](references/v2-method.md)。优先官方 RSS/Atom 或公开生成的 feed，避免脆弱抓取。已包含[信源重叠分析工具](scripts/evaluate_source_overlap.py)；基线使用私有输出目录内生成的归档，建议报告也必须保存到技能之外。低重叠率不代表质量合格或拥有抓取授权。

## 可选本地阅读器

已包含[阅读器页面](index.html)、[阅读器代码](assets/app.js)、[样式](assets/styles.css)和本地静态依赖。预览时，把页面和资源复制到私有工作站点，在那里生成数据，且只为该目录启动服务。不得把服务根目录指向已安装技能，也不得自动公开私有结果。阅读器截图和历史数据不是运行依赖。已包含经典视图和 Web manifest；可选 GSAP 动画脚本来自 jsDelivr，需联网并遵守其独立条款。可选点评已包含[评分脚本](scripts/persona_score.py)和[人物定义](personas/README.md)，须显式指定私有数据目录及随包人物目录。设置 `PERSONA_ENABLED=0` 可仅用规则评分；没有另行授权和私有凭据时不得启用收费的 DeepSeek API。日报生成器不会自动运行点评脚本。

## 可选私有集成

邮件、X、依赖 cookies 的信源及付费 API 都需独立授权，不附送账号或免费服务额度。邮件默认禁用，只有用户明确授权后才可设置 `EMAIL_DIGEST_ENABLED=1`，仍保持禁止发布。凭据只进私有主机或凭据库配置，不进入聊天、历史 token 复用、公共文件或日志。任何发布、发邮件、修改账号或收费前都须确认。本技能默认只读采集，不发送邮件。集成未就绪或未获授权时先停止，不得伪造成功。

## 参考资料与验证

随包提供上游[项目指南](references/upstream-project-readme.md)、[英文指南](references/upstream-project-readme.en.md)、[技能指南](references/upstream-skill-readme.md)、[交接说明](docs/GPT_HANDOFF.md)、[信源覆盖](docs/SOURCE_COVERAGE.md)、[路线图](docs/ROADMAP.md)和[产品简报](docs/V2_PRODUCT_BRIEF.md)，仅供参考。该版本不会安装或调用上游开发测试、外部技能校验器、托管网站、GitHub Actions 或发布工作流。没有另行请求时，不得执行参考文档中的上游工作流或部署指令。再分发时保留原文 [MIT 许可](LICENSE)和 LearnPrompt 署名。
