---
name: wecom-doc
description: >-
  企业微信**在线文档（Word 类，doc）**的正文读写：新建 doc 文档、把本地 .docx/.doc/.txt 导入成
  doc 文档、读取正文、向末尾追加内容、全量覆盖正文。**仅当**用户明确说了 "doc""docx""word"
  "在线文档""office 文档"，或给出 https://doc.weixin.qq.com/doc/xxx 链接时才用它。
  用户只说"创建文档 / 写个文档 / 整理成文档 / 输出到文档"而没指明类型时，**默认走
  wecom-smartpage（智能文档），本技能不得抢占**。搜索文档、改名、加成员、改权限找 wecom-doc-manage；
  在线表格找 wecom-sheet；智能表格找 wecom-smartsheet；智能文档找 wecom-smartpage。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - doc
---

# 企业微信在线文档（Word 类）正文读写

本技能只管一件事：**一份 `doc` 类型在线文档里的文字**——怎么把它建出来、读出来、往里加、整个换掉。
文件本身叫什么、谁能看，不归本技能。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 安装 / 版本 ≥ 1.2.0 / 授权状态），并遵守其中的 ID 禁露约束与风险确认约定。

## 文档类技能的分工边界

| 用户想做的事 | 归属技能 |
|---|---|
| 搜索任何文档（唯一入口） | `wecom-doc-manage` |
| 改文档名 / 加成员 / 改权限 / 改加入规则（任何类型） | `wecom-doc-manage` |
| **读写在线文档（Word 类）正文** | **本技能** |
| 读写在线表格数据 / 增删子表 | `wecom-sheet` |
| 读写智能表格字段与记录 | `wecom-smartsheet` |
| 读写智能文档 / 智能主页内容 | `wecom-smartpage` |

### 什么时候**不是**本技能（先判这一段，再往下看）

- 用户说"创建文档 / 写个文档 / 整理成文档 / 输出到文档"**且没指明类型** → `wecom-smartpage`。
  这是产品默认落点，**本技能不得抢占**。
- 链接是 `https://doc.weixin.qq.com/smartpage/...` 或 `https://page.weixin.qq.com/smartpage/...`
  → `wecom-smartpage`。
- `docid` 以 `a1_` / `b1_` 开头 → `wecom-smartpage`；以 `s3_` 开头 → `wecom-smartsheet`。
- 链接是 `https://doc.weixin.qq.com/sheet/...` → `wecom-sheet`。
- 域名是 `drive.weixin.qq.com` → 微盘，转 `wecom-disk`。
- 请求里有**字段 / 记录 / 筛选 / 排序 / 统计 / 分组**这类结构化数据语义
  → **严禁**用"doc + markdown 静态表格"变通替代，改用 `wecom-smartsheet`（智能表格）
  或 `wecom-smartpage`（智能文档）。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 导入本地文件为 doc 文档（**也是"新建"的落地方式**） | `wecom-cli doc import` | write-low |
| 读取 doc 文档正文 | `wecom-cli doc contents get` | read |
| 向 doc 文档末尾追加文本 | `wecom-cli doc contents append` | write-low |
| 全量覆盖 doc 文档正文 | `wecom-cli doc contents overwrite` | **write-high（不可逆覆盖）** |
| 直接新建空/纯文本 doc | `wecom-cli doc create` | write-low —— **本技能刻意不用**，新建统一走「生成 .docx → `doc import`」，理由见下方专节 |

> 本技能的 `risk_level` 是 `high`：它包含 `doc.contents.overwrite` 这个不可逆覆盖方法。
> 虽然影响范围限于**单份文档的正文**，但按统一口径，含 write-high 方法的技能一律标 `high`。
> 必须按下方场景四的确认要求执行——技能级的 `risk_level` 不会降低单个方法的确认档位。

## `docid` 的获取与展示规则

`docid` **只能内部流转，禁止自造，禁止展示给用户**。三级获取优先级：

1. **从用户给的链接提取（优先）**：`https://doc.weixin.qq.com/<type>/<docid>?scode=...`，
   取 `/<type>/` 后、`?` 前的一段。
2. **用 `wecom-doc-manage` 搜索获得（备选）**：用户只给了文档名或关键词时。
   搜到多条时按可读候选让用户选定，不得自行挑一个。
3. **用户直接给出完整 `docid`**：可直接用。

展示给用户时一律写成 `[doc_name](url)`，用接口返回的 `url` 原样。

## 场景一：新建一篇 doc 文档

### 用户会怎么说

"给我建个 word 文档写周报" / "新建一个 doc 文档" / "把这些内容做成一份 docx 放到企微上"

### 主流程：生成 `.docx` → `doc import`（两步，**不用 `doc.create`**）

**本技能刻意不使用 `doc.create` 新建 doc 文档**，而是保留上游"先在本地生成 `.docx`，
再 `doc import` 导入"的两步流程。理由见下方「为什么不用 `doc.create`」。

**Step 1：写一份 JSONL 描述文件，用 `scripts/build_docx.py` 生成 `.docx`**

JSONL 的完整书写规范（4 个 action、样式、表格、混排格式）见
[references/docx-build.md](references/docx-build.md)——**首次生成 `.docx` 前必须先读完它**。

```bash
# WECOMAGENT_READABLE_DIRS / WECOMAGENT_WRITABLE_DIRS 必须显式设置，
# 否则脚本直接以退出码 2 失败（详见 references/docx-build.md）
WECOMAGENT_READABLE_DIRS='[{"path":"<工作目录绝对路径>","label":"work"}]' \
WECOMAGENT_WRITABLE_DIRS='[{"path":"<工作目录绝对路径>","label":"work"}]' \
python3 scripts/build_docx.py '<工作目录绝对路径>/项目周报.jsonl'
```

成功时脚本打印 `Successfully built <绝对路径>`，产物落在
`<第一个可写根>/docx/<jsonl 文件名主干>.docx`。**把这一行里的路径抓出来给 Step 2 用。**

**Step 2：导入为企微 doc 文档**

`file_name` **必须与你想要的文档标题一致**（含 `.docx` 后缀）——导入后的文档名取自它：

```bash
wecom-cli doc import \
  --doc-type doc \
  --file-name '项目周报.docx' \
  --file-path '<Step 1 打印出来的绝对路径>'
```

返回 `docid` / `url` / `task_id` / `task_status`（`succ` / `fail` / `processing`）。
`task_status=succ` 时把 `[项目周报](url)` 给用户；`processing` 时说明仍在处理，
`fail` 时把错误如实告知，**不要**假装成功。

### 只有纯文本、不需要排版时

`doc import` 也接受 `.txt`（上游声明支持 `.doc` / `.docx` / `.txt`）。内容是纯文本且用户没有
排版要求时，可以直接写一个 `.txt` 再导入，跳过 `build_docx.py`：

```bash
wecom-cli doc import --doc-type doc --file-name '会议纪要.txt' --file-path '/abs/path/会议纪要.txt'
```

### 为什么不用 `doc.create`

`doc.create` 确实存在（`wecom-cli doc create --doc-name '<名称>'`，`doc_name` 是唯一必填），
且能带初始内容。上游 `wecomcli-doc` **刻意绕开了它**，本技能保留这一设计，依据有三条：

1. **`doc.create` 的初始内容通道能力太弱**。它的 `content` 只接受
   `content_type` ∈ `text` / `markdown`（schema enum），本质是往文档里灌一段纯文本或 markdown；
   而用户对"生成一份 word 文档"的期待通常包含**封面标题、多级标题、列表、表格、局部加粗与配色**。
   走 `.docx` 导入能一次性把这些排版带进去，走 `doc.create` 则只能拿到一坨没有结构的文字。
   （`doc.create` 另有 `doc_requests` 这条"document 节点编辑写入"的结构化通道，但
   `OaUpdateRequest` 的节点结构在 schema 里没有可直接照抄的书写规范，**上游没有任何技能用过它**，
   现场发明极易失败。）
2. **两步流程与 `wecom-sheet` / `wecom-smartpage` 的形态一致**，都是"本地产物 → import"，
   Agent 只需要掌握一套心智模型；而 `doc.create` 与 `sheet.create`
   在后端其实是**同一个方法的两个别名**（两者的请求体都是 `OaDocCreateReq`，靠 `doc_type` 区分，
   已逐字段核对 schema 确认；`smartsheet.create` 是另一个请求体 `SmartSheetCreateReq`，不在此列），
   在 doc 这一侧单独引入它并不会带来新能力。
3. **`doc.create` 属于 R2 报告认定的"零技能覆盖"方法**，上游 14 个 SKILL.md 全文没有一次用到它，
   因此它在真实链路上的行为**没有任何上游经验背书**。

> **保留意见（供后续验证，不影响当前主流程）**：单纯"建一个空文档"或"建一个只有几行纯文字的文档"
> 这类场景，`doc create --doc-name 'X' --content '...' --content-type text` 一条命令就能完成，
> 比"写 JSONL → 跑 python → import"轻得多。若后续实测确认其行为符合预期，
> 可以把它作为**纯文本 / 空文档场景的快捷路径**补进来；
> **在获得实测证据前，主流程一律走导入**，不要临场切换。

## 场景二：读取 doc 文档正文

### 用户会怎么说

"这份文档写了什么" / "把周报内容读出来" / "总结一下这个文档"

```bash
wecom-cli doc contents get --docid '<docid>'
```

`--content-type` 可选 `text` / `markdown` / `ooxml`，**不传默认 `markdown`**。

| 想要什么 | 传什么 |
|---|---|
| 给用户看 / 让模型总结（默认） | 不传，或 `--content-type markdown` |
| 只要纯文字、不要标记 | `--content-type text` |
| 需要底层文档对象结构 | `--content-type ooxml`（返回 `document` 对象，不返回 `content`） |

**返回里有两条互斥的取内容路径**：

- 内容不长 → `content` 字段直接是正文，可直接消费。
- 内容超长 → 框架**自动落盘**，`content` 为空、`file_path` 是本地文件绝对路径。
  这时**必须再用文件读取工具把该路径读进来**才能展示或分析。
  向用户汇报时**不要展示这个本地路径**，说"内容较长，我已读取完"即可。

返回还带 `name`（文档标题）、`url`（文档链接）、`version`（版本号）。
展示时用 `[name](url)`。

## 场景三：向文档末尾追加内容

### 用户会怎么说

"在这个文档里再加一段" / "把今天的进展记到周报里" / "补充一条" / "写进去"

### 追加 vs 覆盖的裁定规则（每次写入前都要过一遍）

- **默认追加**：用户用"写入 / 写到 / 记录 / 补充 / 加进去 / 记一下 / 追加"等**中性动词**，
  且没有明确要求清空或替换 → 一律走 `append`。
- **仅显式覆盖**：只有出现"覆盖 / 重写 / 替换 / 清空重写 / 整个换成"等**强语义词**时才走 `overwrite`。
- 判不准就**按追加处理**——追加错了可以再覆盖修正，覆盖错了原文就没了。

```bash
wecom-cli doc contents append \
  --docid '<docid>' \
  --content '2026-08-31 进展：完成联调，进入压测阶段。'
```

- `content` 只支持 **`text`（纯文本）**，没有 `content_type` 参数。写 markdown 标记不会被渲染。
- `content` 的长度上限是 **10000 字符**（schema `maxLength`）。
  内容更长时分多次追加，或改用覆盖（其上限是 1000000）。
- schema 上 `content` 是可选、只有 `docid` 必填；但**不传 `content` 的追加没有任何意义**，
  实际使用时必须传。

成功返回空对象。执行后汇报"已追加到《文档名》"，给出 `[doc_name](url)`。

## 场景四：全量覆盖文档正文

### 用户会怎么说

"把这个文档整个重写" / "覆盖成下面的内容" / "清空重写" / "整份换成新版"

> ⚠️ **高风险操作（不可逆覆盖）**：本方法会**用新内容替换掉文档的全部原有正文**。
> 原文没有任何备份，CLI 也**没有回滚接口**——写下去就找不回来了。
> 执行前必须向用户复述
> 「将把《\<文档名\>》的**全部现有正文**替换为新内容（约 \<N\> 字），原内容不可恢复」
> 并取得明确同意；用户未明确同意时不得执行。

**执行前的三条硬要求**：

1. **先读再写**。覆盖前**必须**先 `doc contents get` 读一遍现有正文，
   在复述里说清"这份文档现在有什么"（一两句摘要即可），让用户知道自己要毁掉的是什么。
   跳过这一步的覆盖等于蒙眼删除。
2. **复述必须带上文档名与新内容规模**，用姓名/文档名等可读信息，不要出现 `docid`。
3. 用户回复含糊（"嗯""你看着办"）**不算**明确同意，需要再确认一次。

### 命令

内容直接给（推荐用于中短内容）：

```bash
wecom-cli doc contents overwrite \
  --docid '<docid>' \
  --content-type text \
  --content '<完整的新正文>'
```

内容较长时先落到本地文件，再用 `--file-path`（与 `--content` **二选一**）：

```bash
wecom-cli doc contents overwrite \
  --docid '<docid>' \
  --content-type text \
  --file-path '/abs/path/新正文.txt'
```

| 参数 | 必填 | 说明 |
|---|:--:|---|
| `--docid` | 是 | 目标文档 |
| `--content` | 否* | 完整新正文，上限 **1000000** 字符 |
| `--file-path` | 否* | 本地文件路径，与 `--content` 二选一 |
| `--content-type` | 否 | `text` / `markdown`（**没有 `ooxml`**，与读取不同）；通常传 `text` |

\* schema 上只有 `docid` 是 required，但 `content` 与 `file_path` **两者不可同时缺省**，
否则等于没给内容。

**清空文档不能传空值**：`content` 传 `null`、空字符串或干脆不传都会被拒。
要清空请传 `" "`（**一个空格**）。（此规则来自上游 reference 的明文声明，未经实测复核。）

## 参数速查

| 方法 | 必填参数 | 高频可选参数 |
|---|---|---|
| `doc import` | schema 无 required；**实际必须**给 `--file-path`（或 `--file-content`）与 `--file-name` | `--doc-type`（**必须显式传 `doc`**） `--passwd` `--append-doc-id` |
| `doc contents get` | `--docid` | `--content-type`（`text`/`markdown`/`ooxml`，默认 `markdown`） |
| `doc contents append` | `--docid`（`--content` 实际必传） | 无 |
| `doc contents overwrite` | `--docid` | `--content` / `--file-path`（二选一） `--content-type`（`text`/`markdown`） |

完整参数请用 `wecom-cli doc <resource> <method> --help` 现查，不要凭记忆补参数。

## 易错点

- **未指明类型的"写个文档"不归本技能**，默认落 `wecom-smartpage`。抢占是最常见的路由错误。
- **`doc import` 的 `--doc-type` 默认是 `doc`，但仍要显式写上**。这个参数在
  `doc import` / `sheet import` / `smartsheet` 三处共用同一个后端方法，
  默认值只有一个（`doc`），显式写出来才不会在复制粘贴命令时串味。
- **`doc import` 的 schema 没有任何 required 字段**——不传 `file_path` / `file_name`
  在本地校验阶段**不会报错**，会一路发到服务端才失败。别指望 CLI 帮你兜底。
- **`file_name` 决定导入后的文档标题**，且必须含后缀。想让文档叫《项目周报》就传 `项目周报.docx`。
- **`append` 的 `content` 上限 10000，`overwrite` 的上限 1000000**，两者差两个数量级。
  长内容追加要自己分段。
- **`append` 不支持 markdown**（只有 `text`），而 `overwrite` 与 `contents get`
  支持 `markdown`。三个方法的格式能力**不一致**，别互相套用。
- **`contents get` 的 `content_type` 有 `ooxml`，`overwrite` 没有**。
  读得出 ooxml 不等于写得回去。
- **内容超长时 `contents get` 返回的是 `file_path` 而不是 `content`**，
  漏判会让你以为文档是空的。拿到 `file_path` 必须再读一次文件。
- **覆盖前必须先读**。没读过就覆盖，等于在不知道毁掉什么的情况下毁掉它。
- **清空要传一个空格 `" "`**，不是空字符串。
- **`docid` 禁止自造、禁止展示**，展示一律用 `[doc_name](url)`；
  `contents get` 返回的本地 `file_path` 也不展示。
- **`build_docx.py` 需要两个环境变量**（`WECOMAGENT_READABLE_DIRS` / `WECOMAGENT_WRITABLE_DIRS`）
  和 `python-docx` 依赖，缺任何一个都会以退出码 2 失败且**只打印一行笼统错误**。
  见 [references/docx-build.md](references/docx-build.md) 的排错表。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-doc`。
`scripts/build_docx.py` 原样取自上游 `skills/wecomcli-doc/scripts/build_docx.py`，未做修改。
