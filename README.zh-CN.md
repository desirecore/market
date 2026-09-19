# DesireCore Market

[English](README.md) | **简体中文**

**DesireCore 官方 Agent、Team 与 Skill 市场目录，以 Git 进行版本管理。**

在这里发现可复用的智能体、协作团队和任务技能。本仓库统一维护市场元数据、本地随仓库分发的技能，以及经过整理的上游内容入口，并提供 Schema 和校验工具，支持一致、可核验的内容发布。

[项目概览](#项目概览) · [快速开始](#快速开始) · [仓库结构](#仓库结构) · [条目格式与契约](#条目格式与契约) · [多语言维护](#多语言维护) · [参与贡献](#参与贡献) · [校验与测试](#校验与测试) · [安全与信任边界](#安全与信任边界) · [相关项目](#相关项目) · [许可证](#许可证)

## 项目概览

| 资源类型 | 用途 | 浏览入口 |
| --- | --- | --- |
| **Agent（智能体）** | 具有明确角色、能力和配置的独立助手，以内联元数据或上游指针发布。 | [`agents/`](agents/) |
| **Team（团队）** | 由监督者协调的多个智能体，通过指向上游仓库的指针发布，供客户端 fork 安装。 | [`teams/`](teams/) |
| **Skill（技能）** | 可复用的任务指令和辅助资源，既可随仓库分发，也可指向上游 Git、Web 或 ZIP 来源。 | [`skills/`](skills/) |

本仓库是**内容目录，不是独立应用或执行运行时**。市场条目描述资源是什么、来自哪里，以及满足哪些条件才能使用；安装和执行由兼容的 DesireCore 客户端及资源所依赖的环境负责。

### 目录信息的权威来源

| 文件 | 定义的内容 |
| --- | --- |
| [`manifest.json`](manifest.json) | 市场身份、Schema 版本、支持语言、默认语言和汇总统计。 |
| [`categories.json`](categories.json) | 合法分类 ID，以及对应的多语言名称与说明。 |
| [`builtin-skills.json`](builtin-skills.json) | 本地内置技能 ID 和退役清单。 |
| 各条目旁的 `catalog-metadata.v1.json` | 版本化的展示信息、发布信息、来源、治理和兼容性事实。 |

当前资源清单与数量以 manifest 和实际目录为准，README 不再维护容易过期的第二份统计。`totalSkills` 统计顶层本地 `SKILL.md` 条目与外部 `entry.json` 条目，不逐个累计技能集合中的子技能。没有团队的目录可以省略 `totalTeams`；只要声明该字段，其值就必须与实际目录完全一致。

分类覆盖效率、开发、商业、创意、设计、媒体、沟通、研究、数据和管理。发布时应使用 `categories.json` 中的分类 ID，不要将本地化显示名称作为 ID。

## 快速开始

### 在 DesireCore 中使用市场

1. 在兼容的 DesireCore 客户端中打开市场，并同步官方目录。
2. 安装前阅读资源说明、来源、发布信息、客户端要求、许可证和外部依赖；条目提供使用说明时，一并查看。
3. 对可安装条目，按照客户端流程安装，再完成必要的本地配置或授权。凭据和私有配置不得写入本公共仓库。

**已收录不等于可安装。** 目录可以包含仅供展示的资源；兼容性、治理、来源可复现性或许可条件可能限制安装。同步目录也不会自动升级桌面客户端，或替用户开通第三方服务。

### 在本地浏览或参与维护

维护仓库需要 Git、**Python 3.10 或更新版本**以及 `uv`。Python 脚本通过文件内的依赖声明描述运行环境，由 `uv run` 管理。

```bash
git clone https://github.com/desirecore/market.git
cd market

# 校验市场结构和技能多语言内容。
uv run scripts/i18n/validate-i18n.py
```

首次准备环境可能需要下载 Python 依赖包。上述校验不需要模型 API 凭据，未指定 `--online` 时也不会获取上游内容。完整覆盖检查、翻译新鲜度检查和定向命令见[校验与测试](#校验与测试)。

克隆仓库只会下载目录和随仓库分发的文件，不会安装 DesireCore 客户端、智能体、团队或外部产品。

## 仓库结构

```text
.
├── README.md                         # 英文概览与贡献指南
├── README.zh-CN.md                   # 对应的简体中文文档
├── manifest.json                     # 市场元数据、语言与统计
├── categories.json                   # 分类注册表
├── builtin-skills.json               # 内置技能与退役策略
├── agents/<id>/
│   ├── agent.json 或 entry.json       # 主条目文件必须二选一
│   ├── catalog-metadata.v1.json       # 版本化目录元数据
│   └── USAGE[.<locale>].md            # 内联智能体的可选使用说明
├── teams/<id>/
│   ├── entry.json                    # 仅支持上游 Git fork 指针
│   └── catalog-metadata.v1.json
├── skills/<id>/
│   ├── SKILL.md 或 entry.json         # 本地技能或外部来源指针
│   ├── catalog-metadata.v1.json
│   ├── SKILL.<locale>.md              # 本地技能的多语言正文
│   ├── references/                   # 可选的扩展文档
│   └── scripts/                      # 可选的技能辅助脚本
├── schemas/                          # 目录契约及导出的客户端契约
├── scripts/
│   ├── catalog/                      # 目录校验与定向测试
│   ├── i18n/                         # 多语言 Schema、校验与翻译
│   └── gen-collection-children.py     # 上游技能集合清单生成器
├── docs/                             # 编写指南与应用说明
├── .github/workflows/                # 校验、翻译和评审自动化
├── AGENTS.md / CLAUDE.md              # 内容等价的仓库贡献规范
├── LICENSE                           # 仓库原创内容的许可证
└── THIRD_PARTY_NOTICES.md             # 第三方许可的补充说明
```

目录树展示的是支持的组织形式，并非每个目录都必须包含全部文件。多语言正文、辅助脚本和扩展文档属于本地技能；外部指针的实现保留在上游。团队目录只放 `entry.json` 和对应的 sidecar，不放内联 `team.json`。

## 条目格式与契约

以 Schema 和已有条目作为实现参考。精简的 JSON 示例不能替代完整客户端契约。

### 本地技能

本地技能位于 `skills/<id>/SKILL.md`，由 YAML frontmatter 和 Markdown 指令正文组成。顶层 `name` 必须与目录的小写 ASCII slug 一致；多语言显示名称放在 `metadata.i18n` 中。

只有 `SKILL.md` 包含 frontmatter。`SKILL.<locale>.md` 仅包含对应语言正文，以匹配的语言注释开头，并由 i18n 元数据引用。例如，`SKILL.zh-CN.md` 的首行是 `<!-- locale: zh-CN -->`。市场技能的 `disable-model-invocation` 只能设为 `true` 或省略，`false` 会被拒绝。

每个本地内置技能都必须登记到 `builtin-skills.json.skills`，提供 sidecar，并使用有效分类。参考 [frontmatter Schema](scripts/i18n/schema/skill-frontmatter.schema.json)、[联网访问技能](skills/web-access/SKILL.md)和[多语言作者指南](docs/I18N.md)。

`retired` 用于声明客户端可在启动时退役的旧内置技能。客户端只删除同时满足以下条件的副本：由 `skills.lock` 记录为市场或随包内容，且 `SKILL.md` 哈希仍与安装记录一致。手动安装或经过本地修改的副本会被保留。同一个 ID 不得同时出现在 `skills` 和 `retired` 中。

### 外部技能与技能集合

外部技能使用 `skills/<id>/entry.json` 描述上游来源、展示信息、维护者、分类、许可证和再分发方式。技能条目必须提供内联 SVG `icon`，来源支持 `git`、`web` 和 `zip`。外部条目计入 `manifest.stats.totalSkills`，但不进入内置技能索引。

技能集合通过一个市场条目组织多个上游技能，并声明 `children` 清单供发现和展示。子技能的元数据保留在父条目的 sidecar 中；每个子技能都有独立的 `skill + parentId + id` 身份和发布事实。父条目的版本可以未知，不得用父版本推断子技能版本。

参考[飞书 CLI 条目](skills/larksuite-cli/entry.json)及其 [sidecar](skills/larksuite-cli/catalog-metadata.v1.json)。[集合生成器](scripts/gen-collection-children.py)从上游 `SKILL.md` 提取子技能，`--check` 模式只验证固定版本、可复现的集合，不重写条目。

### 智能体

智能体目录必须包含一个主文件：内联元数据 `agent.json` **或**外部指针 `entry.json`，并同时提供 `catalog-metadata.v1.json`。主文件缺失或两种主文件同时存在均不合法。

对外部指针，目录 slug、`entry.id` 和 sidecar 的 `identity.id` 必须一致，`identity.kind` 为 `agent`。上游 AgentFS 的 `agent.json.id` 是独立 UUID，不得为了匹配市场目录而改写。

指针原始数据必须先通过[导出的智能体客户端 Schema](schemas/market-agent-entry.client.schema.json)，再进行 sidecar 校验。版本字段保留客户端要求的类型与格式。`installPolicy` 和 `updatePolicy` 必须同时缺省，或构成受支持的完整组合；双缺省时的有效策略为 `market/market`，sidecar 不得将其改成系统条目。

`latestVersion` 映射到 `release.version`；客户端要求、策略和来源字段必须在指针与 sidecar 之间保持一致；`maintainer` 映射到 `upstreamMaintainer`。可安装指针自身必须在 `source.ref` 中固定完整 Git 提交，或在 `source.sha256` 中固定 Web/ZIP 摘要，仅在 sidecar 中声明固定版本不够。智能体指针不适用内置技能在来源、许可或审查要求上的例外。

内联智能体可以提供简短、纯文本的 `USAGE.md`，说明前置条件、授权步骤和安全边界。多语言版本使用 `USAGE.<locale>.md`，回退顺序为请求语言 → 源语言 → 默认语言 → 无后缀文件。使用说明独立展示，不混入同时会进入智能体运行上下文的 `fullDesc`。客户端可能截断过长内容；详细资料应放入技能的 `references/`。使用说明中的相对路径图片不会渲染。

参考 [DesireCore 内联智能体](agents/desirecore/agent.json)和[钉钉工作台指针](agents/dingtalk-workspace/entry.json)。

### 团队

团队由监督者协调多个智能体，**只能以 Git fork 指针发布**：在 `teams/<id>/entry.json` 中登记来源，并提供 sidecar。团队实现，即 `team.json`、`members.json` 和 `shared/`，保留在上游；安装时 fork 该仓库并安装其声明的成员，之后通过 fork 仓库中的 `git pull` 更新。

因此，`source.kind` 必须为 `git`，必须提供 `source.repoUrl`，可安装指针还必须以 `source.ref` 固定完整提交 SHA。分支和标签可移动，不能满足不可变锁定要求。团队没有 `installPolicy` / `updatePolicy` 组合；即使上游使用宽松许可证，`redistribution` 仍为 `source-pointer-only`。

指针原始数据必须通过[导出的团队客户端 Schema](schemas/market-team-entry.client.schema.json)。目录 slug、`entry.id` 和 sidecar 的 `identity.id` 必须一致；`identity.kind` 为 `team`，`latestVersion` 映射到 `release.version`，来源字段必须与 `provenance.content` 指向同一制品。

`supervisorName`、`supervisorAgentId`、`memberCount`、`memberNames`、`requiredSkills` 和 `requiredClientVersion` 与 sidecar 进行双向一致性校验：既不能丢弃已声明事实，也不能补出原指针没有的事实。成员与监督者的展示元数据不具有安装或权限授权效力；这些事实应从 fork 后的 `team.json` 和 `members.json` 中解析。

智能体与团队卡片使用 `avatar`，而不是技能卡片的 `icon`。即使共享条目契约接受 `icon`，该字段也不会进入这些卡片，校验器会给出警告。参考[合同审查团队条目](teams/contract-review-team/entry.json)。

### 版本化目录元数据

每个顶层条目都必须在主文件旁的固定位置提供 `catalog-metadata.v1.json`。这个伴随元数据文件称为 **sidecar**，用于补充旧客户端兼容文件，而不是替代 `agent.json`、`entry.json` 或 `SKILL.md`。新客户端通过确定性适配器合并信息；重复字段不一致时，校验器直接拒绝，而不是静默选择其中一份。

[目录元数据 Schema](schemas/catalog-metadata.v1.schema.json)覆盖展示、发布、显式时间事实、内容来源、治理、兼容性及类型专属信息。必须保持以下边界：

- **来源事实与运行时事实分离。** sidecar 不能自报可信目录身份 `catalogSourceId`、目录提交/路径/信任等级、最终官方身份、安装状态、设备状态、健康状态、运行时发现的 URL 或 `syncedAt`。可信目录来源和运行时观察由 DesireCore 注入。
- **证据路径跟随实际内容。** 对随仓库分发的内容，`license.evidencePath`、`compliance.licenseEvidencePath` 和 `compliance.noticePath` 相对于条目目录解析，且文件必须真实存在。对指针，这些路径指向上游快照；离线校验无法获取该证据，并会对未固定来源的证据声明给出警告。
- **未知也是有效事实。** 使用显式 `known` / `unknown` 状态。已知日期使用 `YYYY-MM-DD` 和 `precision: "day"`；已知秒级时间使用以 `Z` 结尾的 RFC 3339 UTC 时间戳和 `precision: "second"`。不得用当前日期、克隆时间或同步时间填补未知的发布或目录时间。

智能体与团队客户端 Schema 是生成的兼容性快照，其 `$comment` 记录上游来源提交和 blob。兼容性变更时，应从相应 TypeScript 导出重新生成，不得放宽契约或用仅校验 sidecar 的方式替代。

## 多语言维护

市场语言由 `manifest.json.supportedLocales` 声明，目前为 `en-US` 和 `zh-CN`，默认语言为英文。本地技能显示文案放在 `metadata.i18n`；条目 JSON 和 sidecar 使用各自 Schema 定义的 i18n 结构，不能混用字段名称。

技能正文按照请求语言、源语言、默认语言的顺序回退。默认语言正文保留在 `SKILL.md` 中，其他正文通过路径明确引用，各语言的标题结构需要一致。[术语表](scripts/i18n/glossary.json)维护共享术语。

[翻译工作流](.github/workflows/i18n-translate.yml)使用已配置的模型凭据，处理符合条件的缺失或过期技能译文。生成后仍需人工检查术语、结构和事实准确性，自动化不能替代评审。`translated_by: human` 会锁定译文，阻止自动覆盖；源内容变更后，应先人工同步该译文，再在审查通过后更新 `source_hash`，不得伪造哈希来消除过期检查失败。

`translate.py --check` 只检查新鲜度，不调用模型 API，也不重写译文。后端配置和编写流程见[多语言作者指南](docs/I18N.md)；当前执行行为以工作流和脚本为准。两份 README 需要人工同步维护，不属于技能翻译流水线的输入。

## 参与贡献

欢迎新增可复用资源、完善现有条目、纠正元数据、增强校验，以及改进翻译与文档。

1. **确认内容归属。** 智能体、团队和技能放在本仓库；应用条目放在 [DesireCore Registry](https://github.com/desirecore/registry)。修改前阅读 [AGENTS.md](AGENTS.md) 或 [CLAUDE.md](CLAUDE.md)。
2. **基于最新 `main` 开始工作。** 使用职责单一的分支或独立 worktree，选择正确的条目形态、稳定的公开 slug 和有效分类。参考已有条目时，不要照搬其身份、审查状态或许可声明。
3. **提交完整且一致的条目。** 保持主文件与 sidecar 一致，提供多语言、来源、许可证据、兼容性和外部依赖说明。新增本地技能时更新 `builtin-skills.json`，资源清单变化时更新 `manifest.json` 统计；不要编造未知的日期或版本。
4. **发布前完成检查。** 运行下文适用的校验、审查译文，并遵循仓库规范中的私密词表与公开信息检查要求。扫描完整工作树，包括除 `.git` 外的隐藏文件，同时检查新增路径、分支名、提交信息和拟发布的 PR 文本。保密检索词必须保留在仓库外。
5. **向 `main` 提交 Pull Request。** 说明可复用场景、来源与许可选择、兼容性影响和已执行校验。示例保持通用；修改本指南时同步两种语言；合并前完成必需检查与评审。

目录错误、失效指针或文档问题可通过 [Issue](https://github.com/desirecore/market/issues) 反馈，提供条目 ID、相关客户端版本、预期行为和脱敏复现信息。上游实现问题应酌情反馈给上游项目。公开 Issue 中不得包含凭据、客户私有数据或保密事件证据。

## 校验与测试

从仓库根目录运行命令。脚本使用文件内的依赖声明，目录校验不需要先构建应用或安装 Node.js 项目依赖。

### 目录与翻译检查

```bash
# 校验市场统计、分类、内置索引、条目、sidecar 和技能多语言内容。
uv run scripts/i18n/validate-i18n.py

# 严格校验 sidecar，并按 CI 要求检查所有顶层条目的完整覆盖。
uv run scripts/catalog/validate_catalog_metadata.py --require-complete

# 检查缺失或过期译文，不调用模型 API，也不改写文件。
uv run scripts/i18n/translate.py --check
```

以上检查不会拉取上游来源仓库，但首次准备运行环境、安装依赖时仍可能需要联网。Schema 校验成功不代表上游许可已经核实、外部服务当前可用，或所有客户端都能成功安装。

### 定向编写检查与校验器测试

```bash
# 只检查一个现有技能的正文和翻译状态。
uv run scripts/i18n/validate-i18n.py skills/web-access
uv run scripts/i18n/translate.py --check skills/web-access

# 修改校验器或生成器时，选择运行对应的单文件测试。
uv run scripts/i18n/test_validate_i18n.py
uv run scripts/catalog/test_validate_catalog_metadata.py
uv run scripts/catalog/test_collection_generator.py
```

传入技能路径只缩小技能正文的校验范围，市场级与 sidecar 检查仍会执行。应根据改动选择相关测试文件，而不是每次修改文档都运行全部测试。

### 需要联网的检查

```bash
# 对照固定版本的上游集合检查 children，不重写条目。
uv run scripts/gen-collection-children.py --check

# 可选：在常规校验之外检查来源 URL 是否可访问。
uv run scripts/i18n/validate-i18n.py --online
```

集合检查需要 Git 和网络。可变来源集合会被报告并跳过，因为无法保证生成清单可复现。省略 `--check` 会进入写入模式；提交前应同时检查重新生成的子技能和对应 sidecar 事实。

[校验工作流](.github/workflows/i18n-validate.yml)是 CI 行为的权威来源。它会检测相关路径，纯文档改动可能跳过目录校验。跳过后显示成功的任务，不代表 Markdown 链接或中英文文档已被检查；这些内容仍需单独审查。

## 安全与信任边界

**由官方目录收录，不代表每个上游资源都由 DesireCore 编写、没有使用限制，或已经具备执行条件。** 应检查条目的来源、治理、可用性、许可证和兼容性，不能仅凭目录位置或显示名称推断信任。

所有贡献都必须可复用、不依赖特定客户，并适合公开索引。租户身份、私有组织结构、客户专属提示词、账号映射、凭据和部署细节只能保留在私有 AgentFS home、私有仓库或私有运行配置中。Git 与 GitHub 元数据同样受此边界约束。

连接器或适配器不等于已经打包、授权、安装、付费或托管它连接的第三方产品。依赖另行许可、购买、托管或部署的软件时，必须在发现描述、兼容性信息、多语言文案和执行指令中披露，并说明操作者前置条件、适用条款、相关费用、就绪检查和安全降级行为。必要依赖不可用时，应在外部调用前停止，不得伪造成功结果。

发生保密数据暴露时，按照 [AGENTS.md](AGENTS.md) 中的事件响应流程处理。删除当前文件或重写分支，本身并不能移除 PR 引用、通知、缓存或其他副本。

## 相关项目

| 项目或指南 | 职责 |
| --- | --- |
| [DesireCore Registry](https://github.com/desirecore/registry) | 应用目录及经过授权的生命周期元数据，与本仓库的 Agent/Team/Skill 目录分离。 |
| [DesireCore Control 条目](https://github.com/desirecore/registry/tree/main/entries/desirecore-control) | Control 发布来源、校验和、兼容性要求及安装/卸载指南的权威入口。 |
| [Control 安装说明](docs/desirecore-control.zh-CN.md) | 在兼容 DesireCore 客户端中使用该原生应用的说明。 |
| [Control 实现仓库](https://github.com/desirecore-agent/desirecore-cdp-mcp) | 应用源码与发布版本。 |

DesireCore Control 是面向外部智能体的原生应用，其应用条目属于 Registry，不应在此重复创建 Skill 或内部 MCP 服务条目。安装 Control 不会注册内部 MCP 工具，发布目录条目也不会自动部署兼容的桌面客户端或安装技能。当前要求以权威条目和安装指南为准，不在本概览中重复维护具体发布版本号。

## 许可证

DesireCore 编写的仓库原创内容采用 [MIT License](LICENSE)。**该许可证不会覆盖随仓库分发的第三方内容或外部资源自身的条款。**

使用前阅读 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)、资源自身的许可文件，以及 `license` / `redistribution` 元数据。特别是，第三方声明将随仓库分发的 `docx`、`pdf`、`pptx` 和 `xlsx` 技能列为源码可见的参考实现，而非 MIT 许可的开源内容；其他随仓库分发的内容可能使用 Apache-2.0 或独立条款。外部指针始终受上游许可证约束。

再分发模式描述内容如何交付，不能替代许可证。再分发或用于生产环境前，应核实适用的上游条款。
