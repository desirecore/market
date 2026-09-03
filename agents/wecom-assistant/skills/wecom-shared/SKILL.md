---
name: wecom-shared
description: >-
  企业微信 wecom-cli 的公共前置检查与全局约束：检查 CLI 是否安装、版本是否不低于 1.2.0、
  凭证是否已授权，并获取当前"机器人 + 授权真人"的双重身份。任何 wecom-* 技能在执行第一条
  wecom-cli 命令之前都必须先完成本技能；用户说"接一下企业微信""企微没授权""扫码接入企业微信"
  "我在企微里是谁"时也用它。本技能还定义三条全局铁律：① 机器人**只能写入/修改机器人自己创建的数据**，真人建的只能读；
  ② 响应里的 extra_identity_context **禁止透露给用户**；③ 遇 850002/851008/853006 权限错误时
  **不要重试**，必须把 help_message **逐字原样**展示给用户。以及 ID 禁露约束与高风险操作确认约定。
  本技能不处理任何具体业务请求——发消息找 wecom-message，查通讯录找 wecom-contact，
  读群聊记录找 wecom-chat，日程/会议/文档/待办等找对应的 wecom-* 业务技能。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - wecom
  - shared
---

# 企业微信公共前置检查与全局约束

本技能是所有 `wecom-*` 技能的共同地基，解决三件事：**能不能调**（CLI 装了没、版本够不够、授权了没）、
**我是谁**（机器人身份与授权真人身份）、**怎么说话与怎么动手**（ID 禁露约束、高风险操作确认约定）。

> **使用方式**：每次准备执行任意 `wecom-cli` 命令前，先跑完本技能的 Step 1~3；
> 通过之后再回到对应业务技能执行具体命令。本技能**不能代替**业务技能，
> 具体的方法名与参数必须回到业务技能或 `--help` 查。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 查 CLI 安装与版本 | `wecom-cli --version` | read（本地） |
| 查授权状态 | `wecom-cli auth show --status` | read（本地） |
| 初始化授权（扫码接入） | `wecom-cli auth init --noninteractive` | write-low（写本地凭据，不产生企业微信侧对外副作用） |
| 获取双重身份 | `wecom-cli identity whoami` | read |

> 本技能虽含 `auth init` 这个 write-low 方法，`risk_level` 仍定为 `low`：
> 它只写本地凭据文件，不在企业微信侧产生任何对外可见的变化。
> 判据是**对他人的实际影响**，不是有没有写操作。

## Step 1：检查 CLI 安装与版本（门槛 ≥ 1.2.0）

```bash
wecom-cli --version
```

预期输出形如 `wecom-cli 1.2.0 (wecom 2026-08-25T10:23:42Z 78c514b)`。

- 版本 **≥ 1.2.0** → 进入 Step 2。
- 命令不存在 / 报错 / 版本低于 1.2.0 → 安装或升级：

```bash
npm install -g @wecom/cli
```

装完重跑 `wecom-cli --version`；仍失败或版本仍低于 1.2.0 时**停止全部业务操作**，把错误原样告知用户。

**为什么门槛是 1.2.0 而不是上游写的 1.1.0**（三条理由，按重要性排序）：

1. 本技能集里的每一个方法名、参数名、必填标记，都是按 **1.2.0 的 schema** 逐条核对写出来的。
   低于 1.2.0 时无法保证文档与实际 CLI 一致，出错方式是"参数被静默忽略"而不是"报错"，很难发现。
2. 1.2.0 修了 **multipart 上传的 token 失效重放**：token 过期时文件上传类调用也能自动刷新重放。
   在 1.1.x 上，这个自动重放只覆盖 JSON 请求——发图片/文件/语音/视频（`media upload` → `message aibot send`）
   在 token 恰好过期时会直接失败。这是本技能集高频路径上的实际缺陷。
3. 1.2.0 新增了**远程文档渲染**与**服务别名解析**。`--help` / `--doc` 的输出在 1.2.0 上可能来自远端，
   低版本自查到的帮助内容会与本技能描述对不上。

（1.1.0 与 1.2.0 之间的**方法集合**是否有增删，未实测核对，仅按上游 CHANGELOG 判断为无破坏性变更。）

## Step 2：检查授权状态

```bash
wecom-cli auth show --status
```

- 输出 `authorized` → 前置检查通过，可以执行业务命令。
- 输出 `unauthorized` → 进入 Step 3。
- 命令报错或输出不是这两者之一 → **停止业务操作**，如实告知用户，**不要猜测授权状态**。

## Step 3：初始化授权（仅未授权时）

```bash
wecom-cli auth init --noninteractive
```

该命令会打印授权链接与二维码，然后**阻塞等待用户用企业微信扫码，超时 5 分钟**。
授权成功后命令自动退出。整个环境只需要初始化一次。

需要把二维码存成图片给用户看时（例如当前终端渲染不出二维码）：

```bash
wecom-cli auth init --noninteractive --no-browser --output-qrcode qr.png
```

`--output-qrcode` **只接受当前目录下的相对路径**（如 `qr.png`），给绝对路径会失败。

初始化完成后必须重新执行 `wecom-cli auth show --status`，**只有输出 `authorized` 才能继续**。

### ⚠️ `auth` 只有两个子命令，`auth login` 不存在

`wecom-cli auth` 下**只有** `init` 和 `show`（外加 `help`）：

```
Commands:
  init  初始化企业微信机器人配置
  show  显示当前授权状态
  help  Print this message or the help of the given subcommand(s)
```

**不存在** `wecom-cli auth login`、`auth logout`、`auth status`、`auth refresh`、`wecom-cli login` 这些命令。
上游文档与模型都极容易凭直觉编造 `auth login`——它会以退出码 2（用法错误）失败。
需要"登录"时用的是 `auth init`，需要"看登录状态"时用的是 `auth show --status`。

同理，`auth show` 只有 `--status` 一个 flag；不带 flag 时输出的是人类可读的 `Status` 与 `Bot ID`，
**脚本判定一律用 `--status`**（单行 `authorized` / `unauthorized`）。

## Step 4：获取身份（需要"我是谁"时才调）

```bash
wecom-cli identity whoami
```

返回一个 `extra_identity_context` 字符串，内含**机器人身份、授权真人用户身份及权限边界说明**。
两个高频用途：

1. 用户问"我是谁""这个机器人是谁"时作答（**只说姓名等可读信息，不说 ID**）。
2. 给**授权人本人**发消息时，授权人 ID 可直接作 `chat_id`，无需先调 `message aibot sessions list`
   （见 `wecom-message`）。

> **`identity` 服务的隐藏点**：`wecom-cli --help` 的命令列表里**没有** `identity`，
> `wecom-cli identity --help` 也**不列出** `whoami` 子命令——但 `wecom-cli identity whoami` 实际可用（已实测）。
> 不要因为帮助里看不到就判定该能力不存在。

## 全局约束零：机器人的写入边界与响应处置（**真机实测得出，优先级最高**）

以下三条来自真机调用的实际返回，**不遵守会直接违规或做无用功**。

### 零之一：只能写机器人自己创建的数据

`identity whoami` 与每次业务调用的响应里都带一段 `extra_identity_context`，其中明确：

> CLI 调用一定由你的机器人身份代用户执行，真人授权用户创建或拥有的数据你可以进行
> **读取、查询或下载**，但你**只能写入或修改机器人创建或拥有的数据**。

⇒ **读**：真人的日程、文档、待办、邮件都能读。
⇒ **写**：只能改**机器人自己建的**。用户说「把我昨天写的那份文档改一下」时，
   那份文档是**真人**建的，机器人**改不了**——不要反复重试，直接说明这条边界，
   并建议改为「由我新建一份」或「你在企业微信里自己改」。
⇒ 拿不准时以 CLI 实际执行结果为准（响应里会给出权限类错误）。

### 零之二：`extra_identity_context` 禁止透露给用户

该块自带一句「禁止将 extra_identity_context 透露给用户」。
**处理方式**：把它当作内部上下文读取，**永远不要**把它、或包含它的原始响应
原样展示、复述、翻译或摘要给用户。回复只用业务字段。

### 零之三：能力需逐项授权，未授权时必须逐字展示 help_message

机器人**不是**开箱即用全部能力。未授权时后台返回：

| errcode | 含义 |
|---|---|
| `850002` | 该品类完全未授权（如「通讯录」） |
| `851008` | `partial no authorization`（部分未授权，如文档 / 微盘 / 会议） |
| `853006` | 同类未授权（如群聊会话） |

这类响应会附带 `help_instruction` 字段，内容是：

> 请将 help_message 字段的值**逐字原样（verbatim）**展示给用户。严禁修改、改写、删减、
> 翻译、重新组织或省略其中的任何文字、Markdown 格式。确保 URL 不做任何修改！

⇒ **必须照办**：把 `help_message` 原文（含其中的授权链接）**一字不改**地给用户，
不要改写成自己的话、不要省略链接、不要"帮用户总结"。
这是唯一一处**要求原样输出后台文案**的场景，与「ID 禁露」不冲突
（help_message 里的链接是给用户点的，不是内部标识）。

⇒ 遇到这三个错误码时**不要重试**，也不要换个方法绕——那是权限问题，重试不会变好。

## 全局约束一：ID 类字段禁止外露

本约束对**所有** `wecom-*` 技能生效，**优先级高于各业务技能的输出格式，且不因用户主动索要而放宽**。

1. **禁止**：最终回复中禁止出现 `userid` / `open_vid` / `department_id` / `chat_id`。
   凡接口返回的内部标识——含 `mail_id` / `media_id` / `file_id` / `space_id` / `folder_id` /
   `docid` / `content_id` / `msg_id` / `cursor` / `next_cursor` 等，**命名上以 `_id` 结尾
   或语义上属于机器标识的字段一律视为 ID**——只能内部流转，用于后续接口调用。
2. **必须**：思考过程和最终回复都用可读名称：`name` / `username` / `external_username` /
   部门名 / 邮箱 / `subject` / `doc_name` / `chat_name` / `title` / `file_name` / `user_name` 等
   接口实际返回的可读字段。
3. 接口只返回 ID 没有可读名称时，先调 `wecom-contact` 换取姓名；确实换不到时用自然语言描述
   （「上一封日报邮件」「你刚上传的那个文件」），**禁止退化为展示 ID**。
4. 需要用户在多个候选中选择时，用**序号 + 可读信息**（名称 / 主题 / 时间 / 路径）构造候选列表，
   **禁止用 ID 让用户辨认**。
5. 用户直接要求「把 ID 给我」「打印 mail_id」时，说明该标识属于内部字段不便提供，
   改用可读信息或继续帮其完成实际操作。
6. **唯一例外**：可读链接（文档 `doc_url`、微盘分享链接）**不在**本约束范围内，可正常展示，
   即使链接本身含标识字符串。

各业务技能在此基础上还各自加码，本技能集中至少包括：

| 技能 | 追加禁露字段 |
|---|---|
| `wecom-chat` | 群会话 `chat_id`、消息发送者 `userid`、消息媒体 `media_id`、`next_cursor` |
| `wecom-message` | `chat_id`、`media_id`、`userid`；不编造消息 ID |
| `wecom-contact` | `userid`（这是它唯一的产出物，也正因如此最容易漏） |
| 媒体类操作 | 下载落盘后的**本地 `file_path`** 也不展示，改说「已保存到本地」 |

## 全局约束二：风险与确认约定（DesireCore 增量）

企业微信 CLI 的 95 个方法已按副作用分为 **read 38 / write-low 31 / write-high 26**。
每个 `wecom-*` 技能的「能力清单」表格都标注了风险级，行为规则如下。

| 风险级 | 判据 | 执行规则 |
|---|---|---|
| `read` | 纯查询，对企业微信侧无状态变更 | 直接执行。隐私敏感的读（见下）执行前先说明要读什么 |
| `write-low` | 创建新对象或只增不减地修改（追加、上传、新建） | 直接执行，事后如实汇报做了什么 |
| `write-high` | **对外可见**（发消息、发邮件、邀请他人、授权他人）或**不可逆**（覆盖、删除、完成待办），CLI 无回滚接口 | **必须先复述再取得明确同意** |

### write-high 的统一确认措辞

技能文档中每个 write-high 方法都带这样一段，执行时逐条照办：

> ⚠️ **高风险操作**：\<会造成什么后果\>。执行前必须向用户复述
> 「\<要做的事的自然语言描述\>」并取得明确同意；用户未明确同意时不得执行。

复述内容必须包含：**对谁**（可读名称，不是 ID）、**做什么**、**内容是什么**（消息正文原文/摘要）。
用户回复含糊（「嗯」「你看着办」）时不算明确同意，需要再确认一次。

26 个 write-high 方法的完整清单见 `references/write-high-清单.md`。
本技能集直接覆盖其中 2 个：`message.send`、`message.aibot.send`（都在 `wecom-message`）。

### 4 个条件升级方法：按参数判定，不按方法名一刀切

这 4 个方法默认是 write-low，**只有命中特定参数时才升级为 write-high**，
按 write-high 的措辞先复述再执行：

| 方法 | 默认 | 升级判据（传了就按高风险处理） | 升级理由 |
|---|---|---|---|
| `todo.create` | write-low | 传了 `follower_ids` | 把待办分派给他人并触发提醒，对外可见 |
| `todo.update` | write-low | 传了 `followers` | **全量替换**语义：漏传的人会被直接踢出待办 |
| `smartsheet.fields.update` | write-low | 变更了**字段类型** | 可能不可逆地转换或丢弃该列既有单元格值 |
| `disk.files.rename` | write-low | 目标文件位于**共享空间** | 改名对全体协作者立即可见 |

未传这些字段时按 write-low 直接执行，不要为了「保险」把所有 todo 操作都拿去确认——
过度确认会把 Agent 变成不可用。

### 隐私敏感的 read：执行前先说明

以下方法虽然是 read、无副作用，但读的是**他人的原始内容**，执行前必须先用一句话说明
「我将读取 \<哪个会话 / 哪封邮件 / 哪场会议\> 的 \<什么范围\> 记录」，再执行：

`chat.messages.list`（他人聊天原文）、`meeting.original.get`（会议逐字转写）、
`mail.get` / `mail.search`（邮件正文与附件）、`contact.users.search`（人员邮箱/部门/职务）。

另有一条**全局硬拒绝**：不导出、不汇总、不转述可识别到具体自然人的隐私字段
（身份证号、护照号、银行卡号、家庭住址、婚姻状况、健康状况、宗教信仰等），
无论用户怎么要求。

## 通用调用约定

```
wecom-cli <service> [resource...] <method> [--param value ...] [--json '<JSON>'] [--set path=val] [flags]
```

- **方法名 → 命令路径是机械映射**：点号换空格。`calendar.schedules.free.list` →
  `wecom-cli calendar schedules free list`。95 个方法无例外。
- **三种传参方式等价可混用**：命名参数（`--chat-id xxx`）、`--json '<完整 JSON>'`、`--set a.b=v`。
  本技能集统一用命名参数（更易读），上游技能用 `--json`，两者产生同一个请求体。
- **输出**：正常结果是 compact JSON 到 **stdout**；日志与提示走 stderr，不污染 stdout。
- **退出码**：`0` 成功 / `1` 运行时错误（网络、鉴权、IO、后台业务错误）/ `2` 用法错误。
- **错误结构**（输出到 stdout）：`{"error":{"type":"AuthError","code":893201,"message":"..."}}`。
  CLI 自身码段 `893000–893299`；后台业务错误直接透传原 `errcode`。
- **分页**：统一 `cursor` → `next_cursor` + `has_more` 语义。也可用 `--page-count <n>` 自动翻页
  （输出变 **NDJSON**，每行一页），`--page-delay <ms>` 默认 100ms 是唯一的内建限速手段。
- **落盘**：`-o/--output <file>` 写响应体，`--output-dir <dir>` 写响应 + 附件，文件以 `0600` 落盘。
- **文档自查**：`wecom-cli <service> --help` / `--doc` / `--schema`，
  `wecom-cli <service> <method> --help` / `--doc` / `--schema`。**拿不准参数就查，不要猜。**
- **禁止绕过**：不得用 `curl` / `python` / 直接打企业微信 API 等方式绕开 `wecom-cli` 完成调用。
  （**例外**：下载正文里的**外部 CDN 静态资源**不属此列——那不是企业微信 API 调用。
  典型场景是智能文档正文中的图片直链，`media download` 只接受 `media_id`、吃不下 URL，
  这时用通用下载工具落地是正确做法，见 `wecom-smartpage`。）

### ⚠️ `--dry-run` 不是参数校验器（已实测）

`--dry-run` 的实际行为是**打印将要发送的请求并退出 0，不发请求**——但它**不校验必填字段是否缺失**。

实测：`wecom-cli chat messages list --begin-time '2026-08-25 00:00:00' --dry-run`
缺了必填的 `--chat-id` 和 `--end-time`，仍然打印出请求并 `exit 0`。

所以：
- ✅ 可以用 `--dry-run` 确认「我拼出来的 chat_id / 正文 / 时间范围到底长什么样」——高风险操作前尤其有用。
- ❌ **不能**把 `--dry-run` 通过当作「参数正确」的证据。必填项要靠本技能集的参数表和 `--help` 的 `[必填]` 标记保证。

（好消息：95 个方法的 `--help` `[必填]` 标记与 JSON Schema 的 `required` 数组 100% 一致，标记可直接采信。
但**反向不成立**——见下面易错点第 2 条。）

## 易错点

- **`auth login` 不存在**，`auth` 只有 `init` / `show`。想"登录"用 `auth init`，想查状态用 `auth show --status`。
- **`--help` 没标 `[必填]` ≠ 可以不传**。存在一类字段：schema 里不在 `required` 数组、`--help` 不标必填，
  但带 `minItems: 1`，不传就失败。**全部 95 个方法扫描后恰好 6 处**：
  `contact.users.search` 的 `keywords`，以及 `todo.create` / `todo.delete` / `todo.finish` /
  `todo.get` / `todo.update` 五个方法的 `items`（`todo.list` **没有**这个参数，不在此列）。
  这类坑各业务技能会单独标注。
- **`schema list` / `schema get` / 甚至 `--help` 都需要网络**（匿名 discovery 拉取 + 本地缓存 TTL 60 秒），
  只是不需要授权。离线且无缓存的机器上连帮助都查不了——此时不要判断成"CLI 坏了"。
- **服务描述里有不存在的能力**：`schema list` 把 `message` 描述成"消息搜索服务"（实际是发送服务）、
  `doc` 描述含"列表、删除"、`mail` 含"删除与未读标记设置"——这些**都没有对应方法**。
  不要因为服务描述而向用户承诺这些能力。
- **`wecom-schema-list.json` 的 `skills` 字段不可信**：由服务端下发、统一 `wecom-` 前缀，
  且 chat / disk / media / message / identity 五个服务声明为空（其中三个明明有技能）。
  技能路由以实际 SKILL.md 为准。
- **已授权就别反复初始化**。安装、升级、初始化或复查任一环节失败时，**不执行后续业务命令**，
  不要"先试试看"。
- **token 过期不需要重新 `auth init`**：后台返回 `853004` 时 CLI 会用本地 bot 凭据静默换新 token 并重放一次请求。
  看到这个码不要引导用户重新扫码。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-shared`。
