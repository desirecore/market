---
name: wecom-disk
description: >-
  企业微信微盘（网盘）文件操作：列出最近浏览、按关键词/类型/创建者/空间搜索、读取文件元信息（在哪个空间、哪个文件夹、多大、谁建的）、
  上传本地文件、下载文件到本地、重命名文件、新建文件夹。
  当用户说"微盘""网盘""共享空间""团队盘"，或说"传到微盘""微盘里搜一下""微盘那个 PPT 在哪""下载微盘那个文件""把微盘那个文件改个名"，
  或直接给出 https://drive.weixin.qq.com/s?k=... 形式的链接时使用。
  只做文件级操作：在线文档（doc/sheet/smartsheet/smartpage）的正文读写不归本技能，改文档权限/加成员也不归；
  移动、删除、复制文件、管理共享空间与分享链接企微 CLI 均不支持，需引导用户去客户端。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - wecom
  - disk
---

# 企业微信微盘

帮用户在微盘里**找到文件、拿到文件、放进文件、理顺文件名和目录**。
微盘装的既有离线二进制文件（Word/Excel/PPT/PDF/图片/音视频），也有在线协作文档的入口——
这两类的处理方式完全不同，是本技能最需要分清的一件事。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 已安装、版本达标、`auth show --status` 为 `authorized`；具体版本门槛以 `wecom-shared` 为准）。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 列出最近浏览过的文件 | `wecom-cli disk files list` | read |
| 搜索文件 / 文件夹 / 共享空间 | `wecom-cli disk files search` | read |
| 读取一个文件的元信息 | `wecom-cli disk files get` | read |
| 下载文件到本地 | `wecom-cli disk files download` | read（只写本地磁盘，无远端副作用） |
| 上传本地文件到微盘 | `wecom-cli disk files upload` | write-low |
| 新建文件夹 | `wecom-cli disk folders create` | write-low |
| 重命名文件 | `wecom-cli disk files rename` | write-low ⚠️ **条件升级为 write-high** |

### ⚠️ `disk files rename` 的条件升级判据

重命名个人空间里自己的文件是可回退的小操作；但**共享空间里的重命名对全体协作者立刻可见**，
别人看到的是文件"凭空改名了"。判据如下：

1. 改名前先 `wecom-cli disk files get --file-id '<file_id>'`，读返回的 `file.space_name` 与 `file.path`；
2. `space_name` 指向**团队 / 共享空间**（而非该用户自己的个人空间）→ **按 write-high 处理**；
3. 接口没有"是不是个人空间"的布尔字段，**判不准时一律按共享空间处理**（保守升级，不赌）。

命中升级时：

> ⚠️ **高风险操作**：共享空间里的文件改名对该空间全体协作者立刻可见，别人会看到文件"凭空改了名"。
> 执行前必须向用户复述「把共享空间「<空间名>」里的「<原文件名>」改名为「<新文件名>」」并取得明确同意；
> 用户未明确同意时不得执行。

（改名本身可以再 `rename` 一次改回去，所以是"对外可见"而非"不可逆"；确认的目的是别在别人眼皮底下动共享文件。）

`disk files upload` 上传到共享空间文件夹时同样对该空间成员可见。它仍是 write-low（新增文件，可再删），
但目标位置不明确时要先问清楚传到哪里，不要默认往共享空间塞。

## 场景：找文件

### 「微盘里搜一下 XX」「那个季度汇报的 PPT 在哪」

```bash
wecom-cli disk files search --json '{"keywords": ["季度汇报"], "limit": 10}'
```

`keywords` / `creator_userids` / `search_type` / `file_types` **四选一，至少传一个**才能发起搜索
（`space_keywords` 只是附加过滤，单独传不足以触发）。四者全空时用自然语言追问用户搜什么。

按类型收窄（用户明确点了形态时才传）：

```bash
wecom-cli disk files search --json '{
  "keywords": ["报告"],
  "file_types": ["sheet", "offline_excel"],
  "search_type": "file",
  "sort_by": "modify_time",
  "sort_order": "desc",
  "limit": 20
}'
```

- **`keywords` 里不要混文件类型后缀**：「Excel 报告」应拆成 `keywords:["报告"]` + `file_types:["sheet","offline_excel"]`。
- **在线/离线拿不准就都传**：用户说「Excel」「Word」「PPT」「PDF」而没说在线还是离线时，
  两个枚举一起传（`["sheet","offline_excel"]` / `["doc","offline_word"]` / `["ppt","offline_ppt"]` / `["pdf","offline_pdf"]`）。
- **限定空间**：用户说「在 XX 空间里搜」时用 `space_keywords`（填空间**名称关键词**，本接口不接受空间 ID）。
- **限定创建者**：用户说「张三上传的」时，先用 `wecom-contact` 把姓名解析成 `userid`，再填 `creator_userids`。
- **没有时间范围参数**：接口没有 `begin_time` / `end_time`，**禁止伪造**。
  用户说「最近三天的」时改用 `sort_by: "modify_time"` + `sort_order: "desc"` 拉取，再按返回的 `update_time` 自行筛。

### 「我最近看过的微盘文件」

```bash
wecom-cli disk files list --json '{"limit": 10}'
```

注意这是**最近浏览过**的列表（按最后浏览时间倒序），不是全盘目录树。
用户想看"微盘里都有什么"时要用搜索，不是这个。

### 「这个文件在微盘哪里」「这文件多大、谁建的」

```bash
wecom-cli disk files get --file-id '<file_id>'
# 或者用户直接给了微盘分享链接：
wecom-cli disk files get --url 'https://drive.weixin.qq.com/s?k=XXXXXXXX'
```

`--file-id` 与 `--url` 二选一（同时给时以 `file_id` 为准）。
返回 `file.space_name`（所在空间）、`file.folder_name`（所在文件夹）、`file.path`（完整路径）、
`file.file_size`、`file.create_time` / `update_time`、`file.type`。
`file.creator_userid` 要展示创建者时，先用 `wecom-contact` 换成姓名再说。

## 场景：拿文件

### 「把微盘那个文件下载下来 / 看看里面写了什么」

```bash
wecom-cli disk files download --file-id '<file_id>'
# 或
wecom-cli disk files download --url 'https://drive.weixin.qq.com/s?k=XXXXXXXX'
```

返回本地 `file_path`（内容不长时还会直接给 `file_content`）与 `size`。拿到本地路径后按常规方式读内容。

> **[CRITICAL] 只有 `type=file` 的离线二进制文件能下载。**
> 搜索/列表返回的 `type` 若是 `smartsheet` / `smartpage` / `sheet` / `word` / `ppt` / `journal` / `collect` / `mind` / `flow`，
> 这些是**在线协作文档**，正文存在云端，把它们的 `id` 或 `doc_url` 当 `file_id` / `url` 传进来会失败或拿到空壳。
> 正确路由见下方「在线文档怎么办」。

### 在线文档怎么办

| 命中项 `type` | 用户想读内容时 |
|---|---|
| `word`（`docid` 非 `a1_`/`b1_` 开头）、`doc` | 把 `docid` 交给 `wecom-doc` |
| `sheet` | 把 `docid` 交给 `wecom-sheet` |
| `smartsheet` | 把 `docid` 交给 `wecom-smartsheet` |
| `smartpage`，或 `word` 且 `docid` 以 `a1_` / `b1_` 开头 | 把 `docid` 交给 `wecom-smartpage` |
| `ppt` / `journal` / `collect` / `mind` / `flow` | **没有任何技能或 CLI 能读正文**。如实告知暂不支持，把 `doc_url` 给用户，引导其在企业微信客户端打开 |

`doc_url` 是可读链接，**允许直接展示给用户**，也可以直接当分享链接发出去。

## 场景：放文件

### 「把这个文件传到微盘」

手上是本地文件时，直接传路径，**不需要**先过 `wecom-media`：

```bash
wecom-cli disk files upload --file-path '/abs/path/季度汇报.pptx' --folder-id '<folder_id 或 space_id>'
```

手上已经有 `media_id`（前置技能返回或用户给出）时复用它，此时 `--file-name` 必填：

```bash
wecom-cli disk files upload --json '{
  "file_content_media": "<media_id>",
  "file_name": "季度汇报.pptx",
  "folder_id": "<folder_id 或 space_id>"
}'
```

- `--file-path` 与 `--file-content-media` **二选一，必须有其一，不能同时传**。两者都没有时追问用户，禁止靠搜索凑一个文件。
- `--file-name`：传 `file_path` 时可不传（从路径自动提取）；传 `file_content_media` 时**必填**。
  名称长度 1~255，且**不能含** `/ \ : * ? " < > |`。
- `--folder-id` 不传则上传到默认空间。目标位置不明确时先问清楚，不要默认往共享空间塞。

### 「在微盘建个文件夹」

```bash
wecom-cli disk folders create --folder-name '2026 年季度材料' --folder-id '<父文件夹 file_id 或 space_id>'
```

`--folder-name` 必填（1~255，禁含 `/ \ : * ? " < > |`）；`--folder-id` 不传则建到个人空间根目录。

### 「把微盘那个文件改个名」

```bash
# 第一步：文件名不是 file_id，先搜出来
wecom-cli disk files search --json '{"keywords": ["季度汇报"], "search_type": "file", "limit": 10}'
# 第二步：确认它在哪个空间（决定是否需要用户确认，见上方条件升级判据）
wecom-cli disk files get --file-id '<第一步命中的 files[].id>'
# 第三步：改名
wecom-cli disk files rename --file-id '<file_id>' --new-name '2026Q2 季度汇报.pptx'
```

`--file-id` 与 `--new-name` 均必填。新名称 1~255，**不能含** `/ \ : * ? " < > |`，且要**带上原扩展名**。
返回只有 `status: "success"`，不带文件对象；需要最新元数据就再 `disk files get` 一次。

> 在线文档（doc/sheet/smartsheet/smartpage）的改名归 `wecom-doc-manage`，不走这里。
> **文件夹（`folder`）不支持重命名**，如实告知用户去客户端操作。

## 参数速查

| 方法 | 必填 | 关键可选与约束 |
|---|---|---|
| `disk files list` | 无 | `--cursor`、`--limit` |
| `disk files search` | `keywords` / `creator_userids` / `search_type` / `file_types` 至少一个 | `--keywords` ≤20、`--file-types` ≤10、`--creator-userids` ≤50、`--space-keywords` ≤10、`--limit` ≤100（默认 10）、`--cursor`、`--sort-by`、`--sort-order` |
| `disk files get` | `--file-id` 与 `--url` 二选一 | — |
| `disk files download` | `--file-id` 与 `--url` 二选一 | — |
| `disk files upload` | `--file-path` 与 `--file-content-media` 二选一 | `--file-name`（用 media 时必填）、`--folder-id` |
| `disk files rename` | `--file-id`、`--new-name` | — |
| `disk folders create` | `--folder-name` | `--folder-id` |

**枚举取值（写枚举外的值会失败）：**

- `search_type`：`all`（默认）/ `file` / `folder` / `space`
- `sort_by`：`best_match`（默认）/ `modify_time` / `file_size`
- `sort_order`：`asc` / `desc`（默认）
- `file_types`：`doc` / `sheet` / `ppt` / `collect` / `mind` / `flow` / `smartsheet` / `smartpage` / `journal` / `pdf` /
  `offline_word` / `offline_excel` / `offline_ppt` / `offline_pdf` / `image` / `videoaudio` / `design`
- 返回的 `type`：`file` / `folder` / `space` / `smartsheet` / `smartpage` / `sheet` / `word` / `ppt` / `collect` / `journal` / `flow` / `mind`

**可选参数的默认策略：默认不传，仅当用户明确点名时才传。**
用户笼统说「搜一下 xxx / 找找资料」时，`search_type` / `sort_by` / `file_types` 都不传，让后端用默认值。

## 明确不支持（如实告知，引导去客户端）

- 移动 / 删除 / 复制文件；删除或重命名**文件夹**；调整目录树
- 创建 / 删除共享空间，修改空间成员与设置
- 修改分享权限、生成或撤销分享链接、设置访问密码与有效期
- 版本管理（看历史版本、恢复旧版、比对）
- 覆盖上传 / 秒传 / 断点续传（需要替换就重新上传一份新文件）
- 持续监视微盘变更、新文件到达通知 —— **不要承诺「有新文件我告诉你」**，请用户稍后自己再问
- **给机器人授予某空间权限 / 把机器人加进共享空间成员**：微盘**没有**这个功能，客户端也做不到。
  **禁止**向用户提这类建议，也不要引导用户「联系空间管理员给机器人授权」

## 易错点

- **文件名不是 `file_id`**：用户给名字/关键词时先 `search` 拿 `id`，禁止把文件名当 `file_id` 拼进命令。
- **域名分不清就全错**：`drive.weixin.qq.com` 才是微盘；`doc.weixin.qq.com` / `page.weixin.qq.com` 是在线文档，
  传进本技能的 `--url` 会失败。
- **在线文档不能下载**：见上方 [CRITICAL]。只有 `type=file` 才可 `download`。
- **搜索必须有界**：一组条件搜完必要时再调整一次，2~3 轮仍无结果就停下来如实告知"未搜到"，
  并请用户补更准的关键词 / 类型 / 创建者，**禁止无限换词硬搜**。
  停下时要说清楚是「搜不到文件」还是「搜不到这个空间」。
- **重名要追问**：搜出多个同名空间或文件夹时，用序号 + 可读信息（名称/路径/时间）让用户选，禁止随手选第一个。
- **`path` 才是层级真相**：`space_name` 与 `folder_name` 同名时不一定是父子关系，可能平级，判断层级看 `path`。
- **翻页**：`has_more=true` 时把 `next_cursor` 填进下一次的 `cursor`；首次调用 `cursor` 传空串或不传。
- **展示顺序跟随排序方向**：`sort_order=desc` 时向用户也从新到旧展示，不要颠倒。
- **内部 ID 一律不外露**：`id` / `file_id` / `space_id` / `folder_id` / `docid` / `creator_userid` / `cursor` / `next_cursor`
  只能内部流转。要展示创建者就先用 `wecom-contact` 换姓名。**唯一例外是 `doc_url` 等可读链接**，可正常展示。
- **禁止绕过 CLI**：不得用 `curl` / `python` 等手段直接请求企微接口。CLI 报错时原样转达错误信息并给替代建议。

## 结果展示规范

展示 `list` / `search` 结果时：

- 用 **markdown 无序列表**逐条展示，**不要用表格**，最多展示 10 条。
- 每条首行：`doc_url` 非空（在线文档）写成 `- [文件名](doc_url)`；`doc_url` 为空（离线文件 / 文件夹 / 空间）
  写成 `- 文件名`，**不得编造链接**。
- 副行可放 `path` / `update_time` / 可读大小（如 `2.4 MB`），字段间用 `·` 或空格分隔。
- 禁止直接贴原始 JSON，禁止出现任何内部 ID。

## 跨技能依赖

| 技能 | 何时触发 |
|---|---|
| `wecom-shared` | 每次执行 `wecom-cli` 前的前置检查（必做） |
| `wecom-contact` | 用户按「谁上传的」搜索时把姓名解析成 `userid`；要展示 `creator_userid` 时换姓名 |
| `wecom-media` | 上下文已有 `media_id` 想传进微盘时，直接填 `--file-content-media` 即可（**不用**再跑 media upload）；只有本地文件时也直接填 `--file-path` |
| `wecom-doc` / `wecom-sheet` / `wecom-smartsheet` / `wecom-smartpage` | 命中在线文档且用户要读正文时，按 `type` / `docid` 前缀路由 |
| `wecom-doc-manage` | 在线文档的改名 / 加成员 / 改权限 |

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-disk`。
