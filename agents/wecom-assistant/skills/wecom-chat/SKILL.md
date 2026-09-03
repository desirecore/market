---
name: wecom-chat
description: >-
  读取企业微信群聊的历史消息：列出最近 7 天有消息的群会话，拉取指定群会话在某个时间段内的
  消息明细（文本、图片、文件、语音、视频、图文混排），并把消息里的图片和文件取下来。
  用户说"看看 XX 群这两天聊了什么""昨天群里说的那个事""帮我总结一下项目群的讨论"
  "把群里发的那个文件找出来""这周哪些群比较活跃""群里最近讨论了什么"时用它。
  只支持最近 7 天，且读的是他人的聊天原文，属最高隐私敏感度，读取前必须先说明将要读什么。
  本技能只读不写，不发送任何消息（发消息找 wecom-message），也不查通讯录（找 wecom-contact）。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - wecom
  - chat
---

# 企业微信群聊历史读取

用来回答「这个群最近在聊什么」「昨天群里讨论的那个方案是怎么说的」「群里发的那份文件在哪」
这类问题：先找到目标群会话，再按时间段拉消息明细，需要时把消息里的图片/文件取下来。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查。

> 🔴 **这是本技能集里隐私敏感度最高的能力**——读到的是**他人的聊天原文**。
> 三条不可省略的规矩写在下面的「隐私处置」一节，**先读那一节再动手**。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 列出最近 7 天有消息的群会话 | `wecom-cli chat groups list` | read（隐私敏感：暴露群名与活跃度） |
| 拉取指定会话的消息明细 | `wecom-cli chat messages list` | read（**最高隐私敏感**：他人聊天原文） |
| 取消息里的图片 / 文件 / 语音 / 视频 | `wecom-cli message files get` | read（隐私敏感：他人发的文件内容） |

> 三个方法都是 read，对企业微信侧无任何状态变更，不需要「高风险操作」式的复述同意流程。
> 但因为读的是他人内容，**执行前必须先说明将要读什么**（见下）。
> 本技能整体定为 `medium` 而非 `low`，正是为了让这条隐私要求不被当成普通只读操作跳过。

## 隐私处置（读之前必须做的三件事）

1. **读取前说明**。执行 `chat messages list` 之前，用一句话告诉用户你将要读什么：

   > 「我将读取『项目 A 群』2026-08-29 00:00 至 2026-08-31 23:59 的聊天记录，用于整理讨论要点。」

   范围必须具体到**哪个会话 + 哪个时间段 + 读来干什么**。用户没指定会话时先列会话让他选，
   **不要"先全都拉下来再说"**——不得为了省一次交互而批量遍历多个群。

2. **只回答被问到的问题**。拉下来的原文用于回答用户的当前请求，
   不主动扩散、不做人物画像、不统计"谁说话最多""谁最晚下班"这类对个人的行为分析，
   除非用户明确要求且目的正当。

3. **隐私字段硬拒绝**。聊天记录里出现身份证号、护照号、银行卡号、家庭住址、
   婚姻状况、健康状况、宗教信仰等可识别到具体自然人的敏感信息时，
   **不摘录、不转述、不写进总结**，即使用户要求。可以说明「记录中含敏感个人信息，已略去」。

此外，`chat messages list` 属于 `wecom-shared` 列出的「隐私敏感 read」清单成员，
那一节的全局规则同样适用。

## 硬限制：只有最近 7 天

`chat groups list` 与 `chat messages list` **都只支持查询最近 7 天**。

**超出时间窗时服务端直接不返回数据，不是报错**——你会拿到一个空列表，
而不是一条"超出范围"的错误信息。所以：

- 用户说「上个月群里那个事」时，**先告诉他只能查最近 7 天**，不要拉一次空结果再说"没找到"。
  这两种回答对用户是完全不同的意思。
- 拉到空结果时，先自查时间范围是不是已经越界，再下"这段时间没有消息"的结论。
- 不要试图用多次分段查询去凑出 7 天以前的数据，服务端不给就是不给。

时间格式统一为 `YYYY-MM-DD HH:MM:SS`，`end_time` **必须晚于** `begin_time`。

## 场景：看看最近哪些群在聊 / 找到目标群

用户说「这周群里有什么动静」「帮我看看项目群最近聊了什么」（还没指明具体是哪个群）。

```bash
wecom-cli chat groups list \
  --begin-time '2026-08-25 00:00:00' \
  --end-time '2026-08-31 23:59:59'
```

返回：

| 字段 | 说明 | 能否展示 |
|---|---|---|
| `chats[].chat_name` | 会话名称（下游未提供时可能为空） | ✅ **用它指代会话** |
| `chats[].last_msg_time` | 该会话最后一条消息时间 | ✅ |
| `chats[].msg_count` | 该会话**在本次查询时间范围内**的消息条数 | ✅ 用来说"哪个群活跃" |
| `chats[].chat_id` | 群会话 ID | ❌ **内部流转，绝不外露** |
| `chats_count` | 本页会话数量 | ✅ |
| `has_more` / `next_cursor` | 分页控制 | ❌ 内部使用 |

**注意**：接口描述明写「**目前仅返回群聊会话**」——单聊不在这里。
需要读单聊记录时，`chat messages list` 的 `chat_id` 要传对方的 `userid`（见下一节）。

展示给用户时按**序号 + 群名 + 最后消息时间 + 消息条数**列出，让用户选：

```
最近 7 天有消息的群（共 4 个）：
1. 项目 A 讨论群 · 最后消息 2026-08-31 18:22 · 本期 137 条
2. 产品周会群 · 最后消息 2026-08-30 11:05 · 本期 42 条
...
```

`chat_name` 为空的会话用自然语言描述（「一个未命名的群，最后消息在 8/30 上午」），
**绝不退化为展示 `chat_id`**。

## 场景：拉某个群的消息明细

用户选定会话后（或一开始就点名了群），拉消息：

```bash
wecom-cli chat messages list \
  --chat-id '<上一步 chats[].chat_id>' \
  --begin-time '2026-08-30 00:00:00' \
  --end-time '2026-08-31 23:59:59'
```

`--chat-id` 的**合法来源只有两个**：

| 会话类型 | 来源 |
|---|---|
| 群聊 | `chat groups list` 返回的 `chats[].chat_id`，**原样复制** |
| 单聊 | `wecom-contact` 解析出的对方 `userid`（接口描述：单聊传对方成员的 userid） |

**禁止**：用户口头给的 ID、历史上下文里缓存的 ID、按群名自行构造的值、
`message aibot sessions list` 返回的机器人会话 ID（那是**可发送范围**，与**可读取范围**不是一回事，
不要混用）。

返回的消息**按时间正序排列**（从旧到新，schema 明写）。
注意这和 `message aibot sessions list` 的「按最后消息时间从新到旧」方向相反，
做总结时别把时间线搞反。（`chat groups list` 的排序方式 schema **没有声明**，
不要假设它是按时间排的——要按活跃度排给用户看时，自己按 `msg_count` 或 `last_msg_time` 排。）

完整的返回结构（6 种 `msg_type` 的字段布局、图文混排的嵌套形状）见
`references/消息结构.md`，处理消息列表前先读它。

要点速记：

- 每条消息带 `send_time`、`msg_type`、以及**发送者的可读姓名 `user_name`**。
  有 `user_name` 就直接用它，**不需要**再去 `wecom-contact` 查一次。
- `msg_type` 有 6 种：`text` / `image` / `file` / `voice` / `video` / `mixed`（图文混排）。
  只有 `text` 和 `mixed` 里的 text 项直接带正文，其余都只给 `media_id`。
- **`mixed` 最容易漏**：它的正文在 `mixed.items[]` 里，每项自己再带 `msg_type`（`text` / `image`）。
  只看顶层 `text` 字段会把图文混排消息当成空消息。

## 场景：分页拉完一整段

单次调用只返回一页。两种翻页方式：

**方式一：CLI 自动翻页**（推荐，省事）

```bash
wecom-cli chat messages list \
  --chat-id '<chat_id>' \
  --begin-time '2026-08-30 00:00:00' \
  --end-time '2026-08-31 23:59:59' \
  --page-count 10
```

`--page-count <n>` 最多自动翻 n 页，**输出格式变成 NDJSON**（每行一页的完整响应），
不再是单个 JSON——解析时要按行读。`--page-delay <ms>` 控制请求间隔，默认 100ms，
这是唯一的内建限速手段。

**方式二：手工游标**

不传 `--cursor` 时从**最新一页**开始。每次响应带 `has_more` 与 `next_cursor`：
`has_more=true` 时把 `next_cursor` 原样传给下一次的 `--cursor`；`next_cursor` 为空表示已无更多数据。

```bash
wecom-cli chat messages list --chat-id '<chat_id>' \
  --begin-time '...' --end-time '...' --cursor '<上一次的 next_cursor>'
```

`cursor` / `next_cursor` **属于禁露字段**，只在内部流转。

**别无限翻页**：先给一个页数上限（比如 10 页），拉够了就停下来做总结，
并告诉用户"还有更多历史消息，需要的话可以继续拉"。

## 场景：把群里发的图片 / 文件取下来

消息列表里 `image` / `file` / `voice` / `video` 各带一个 `media_id`，
用 `wecom-message` 的取媒体方法拿内容：

```bash
wecom-cli message files get --media-id '<消息里的 media_id>'
```

返回 `media_item`，关键字段：

| 字段 | 说明 |
|---|---|
| `media_type` | `image` / `file` / `voice` / `video` |
| `file_name` | 文件名（含扩展名）——**唯一适合展示给用户的字段** |
| `content` | 内容不长时直接返回字符串 |
| `file_path` | 内容超长或含非 UTF-8 字节时由框架落盘，返回**本地文件路径** |

- `content` 与 `file_path` **二选一**，两个都要判。
- 想固定落盘用 `-o <file>` 或 `--output-dir <dir>`（文件以 0600 写入）。
- **`file_path` 属于禁露字段**：说「已取到文件『需求评审纪要.docx』」，不要贴本地路径。
- 只有 `file` 类型的消息带 `file_name`；`image` / `voice` / `video` 的消息内容里只有 `media_id`，
  文件名要看 `message files get` 的返回。
- **不要把整个群的媒体一次性全拉下来**。只取用户实际要的那一个/那几个。

## 参数速查

| 方法 | 必填参数 | 可选参数 |
|---|---|---|
| `chat groups list` | `--begin-time`、`--end-time` | `--cursor` |
| `chat messages list` | `--begin-time`、`--end-time`、`--chat-id` | `--cursor` |
| `message files get` | `--media-id` | — |

通用 flag：`--page-count` / `--page-delay`（分页）、`-o` / `--output-dir`（落盘）、
`--dry-run`（打印请求体，**不校验必填字段**）。

完整 schema 用 `wecom-cli chat <resource> list --help` / `--doc` / `--schema` 自查。

## 易错点

- **只有最近 7 天**，越界时是**静默返回空**而不是报错。空结果先自查时间窗，再下结论。
- **`chat groups list` 目前只返回群聊**。用户问"我和张三的私聊记录"时，
  要走 `wecom-contact` 拿 `userid` 再传给 `chat messages list` 的 `--chat-id`，
  不要在群列表里找。
- **`chat messages list` 是正序（旧→新）**，而 `message aibot sessions list` 是倒序（新→旧）。
  写总结时别把时间线搞反。**`chat groups list` 的排序 schema 完全没声明**——
  不要写「最近活跃的群排在前面」这种话，要排序就自己按 `msg_count` / `last_msg_time` 排。
- **`mixed`（图文混排）消息的正文藏在 `mixed.items[]` 里**，顶层没有 `text` 字段。
  漏处理会让图文消息在总结里凭空消失。
- **`chat_name` 可能为空**（schema 原文：「下游未提供时为空」）。为空时用自然语言描述该会话，
  绝不改用 `chat_id`。
- **可读取范围 ≠ 可发送范围**。`chat groups list` 给的是**能读历史**的群，
  `message aibot sessions list` 给的是**机器人能发消息**的会话，两个集合不一定重合，
  `chat_id` 也不要互相搬运（虽然 `chat groups list` 的 schema 说它可作 `send_message` 用，
  但发消息请统一走 `wecom-message` 的流程与确认要求）。
- **`--dry-run` 不校验必填字段**（实测缺 `--chat-id` / `--end-time` 仍 exit 0）。
  不要把 dry-run 通过当成参数完整的证据。
- **`msg_count` 是"本次查询时间范围内"的条数**，不是该群的总消息数。
  说"这个群有 137 条消息"是错的，要说"这段时间里有 137 条"。
- **`user_name` 已经是可读姓名**，直接用；`userid` 与 `media_id` / `cursor` / `next_cursor`
  全部禁止外露。
- 别用 `curl` / Python 绕过 `wecom-cli` 去拉聊天记录。

---

## 来源

本技能为 DesireCore 原创，基于 [wecom-cli](https://github.com/WecomTeam/wecom-cli)
（MIT License，© WecomTeam）的 CLI 能力封装，上游未提供对应 Skill。

覆盖的 3 个方法（`chat.groups.list`、`chat.messages.list`、`message.files.get`）
在上游 14 个 SKILL.md 及其 references 中**一次都没有出现**，属于本技能集相对上游的净增量。
