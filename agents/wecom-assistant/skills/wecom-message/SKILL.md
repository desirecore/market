---
name: wecom-message
description: >-
  向企业微信的单聊或群聊发送消息，并查询当前有权限发送的会话范围、拉取消息里的图片/文件/语音/视频。
  支持机器人身份的 markdown、图片、文件、语音、视频消息，以及普通文本消息。
  用户说"给张三发个消息""在 XX 群里通知一下""把这个文件发到企微""发条消息提醒他"
  "把刚才那张图下载下来"时用它。
  发送是高风险操作，执行前必须复述并取得明确同意。
  本技能不负责把人名解析成收件人（那是 wecom-contact），不负责读群聊历史（那是 wecom-chat），
  也不发邮件（那是邮件技能）。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - message
---

# 企业微信发送消息

发消息是**发出去就收不回**的操作，也是这套技能集里最容易出事的地方——
发错人比发错内容更糟。因此本技能的重心不在"怎么发"，而在**"怎么确保发对人"**。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 列出机器人最近的会话（可发送范围） | `wecom-cli message aibot sessions list` | read |
| 以**机器人身份**发 markdown / 图片 / 文件 / 语音 / 视频 | `wecom-cli message aibot send` | **write-high** |
| 发**纯文本**消息到指定会话 | `wecom-cli message send` | **write-high** |
| 按媒体 ID 取消息里的图片 / 文件 / 语音 / 视频 | `wecom-cli message files get` | read |

> ⚠️ **高风险操作**（`message aibot send` / `message send`）：消息一旦发出即对收件人可见，
> CLI 没有撤回接口。执行前必须向用户复述
> 「即将以 \<机器人 / 你本人\> 的身份，向 \<会话的可读名称\> 发送 \<消息类型\>：\<正文原文或摘要\>」
> 并取得明确同意；用户未明确同意时不得执行。
>
> 复述里**用会话名称，不用 chat_id**。用户回复含糊（「嗯」「你看着办」）不算明确同意。

## 两个发送方法怎么选

| | `message aibot send` | `message send` |
|---|---|---|
| 发送身份 | **明确以「智能机器人」身份**（接口描述原文） | 接口未声明机器人身份（推测为授权真人身份，**未实测证实**） |
| 支持的消息类型 | `markdown` / `image` / `file` / `voice` / `video` | **仅 `text`** |
| 正文上限 | markdown ≤ **20480** UTF-8 字节 | 文本 ≤ **2048** 字符 |
| `chat_id` 来源约束 | **最严**：必须取自本次刚调的 `sessions list`（或授权人本人） | 见下方「`message send` 的 chat_id 来源」 |
| 上游是否覆盖 | 是（`wecomcli-message`） | **否**——本技能补齐，行为未经上游验证 |

**选用判据（按顺序判断）**：

1. 要发的是**图片、文件、语音、视频，或者带格式的 markdown** → 只能用 `message aibot send`。
   `message send` 的 `msg_type` 目前只支持 `text`。
2. 正文超过 2048 字符 → 只能用 `message aibot send`。
3. 用户明确说"以机器人身份发""用机器人通知" → `message aibot send`。
4. **其余所有情况，默认用 `message aibot send`。** 这是上游唯一验证过的路径，
   会话范围、匹配规则、失败语义都有明确定义。
5. **仅当用户明确要求「不以机器人身份发送」时**，才考虑 `message send`，
   并且必须先告知用户这条路径未经验证。

> ⚠️ **「目标不在 `sessions list` 范围内」不是切换到 `message send` 的理由。**
> 那种情况的正确出口是**停止发送**并告知用户目标不在机器人会话范围内，
> 而不是换一条约束更松的路径把消息发出去。

> **诚实提示**：`message.send` 的实际发送身份（收件人看到是谁发的）**没有实测过**。
> 判断依据只是接口命名与描述的对比：`message aibot send` 明写"以智能机器人身份"，
> `message send` 没有这个声明。首次使用时应先在**与授权人本人的单聊**里试一条，确认呈现效果再用于他人。

## 场景：给某人 / 某个群发消息（主路径）

用户说「给张三发个消息说会议改到明天下午三点」「在『项目 A 群』里通知一下」。

### Step 1：确定能不能发给这个对象

企业微信只允许机器人向两类对象发消息：

1. **授权人本人**——ID 直接可用作 `chat_id`，**不需要**调 `sessions list`：

   ```bash
   wecom-cli identity whoami
   ```

2. **机器人最近有消息往来的会话**（单聊 + 群聊）——必须从会话列表里取：

   ```bash
   wecom-cli message aibot sessions list
   ```

   无入参。返回按最后一条消息时间**从新到旧**排序、**最多 20 个**会话，不支持分页与过滤。
   已解散 / 已封禁 / 全员群已关闭 / 机器人已被移出的群聊**不会返回**。

   | 返回字段 | 说明 | 能否展示 |
   |---|---|---|
   | `sessions[].chat_name` | 群名；单聊为「中文名(英文名)」 | ✅ |
   | `sessions[].chat_type` | `single` 单聊 / `group` 群聊 | ✅ |
   | `sessions[].last_msg_time` | 最后一条消息时间 `YYYY-MM-DD HH:MM:SS` | ✅ |
   | `sessions[].chat_id` | 会话 ID | ❌ **内部流转，绝不外露** |
   | `sessions_count` | 会话数量 | ✅ |

### Step 2：在本次返回里匹配目标（这是最硬的一条约束）

> ### 🔒 `chat_id` 必须取自**本次刚调的** `sessions list`
>
> 调用 `message aibot send` 前，必须先调**一次** `sessions list`，
> 从**本次**返回的 `sessions[]` 里选定目标项，把该项的 `chat_id` **原样复制**到 `--chat-id`。
>
> 以下值**一律不可用作** `--chat-id`：
> - 用户输入的 ID
> - 之前轮次、历史上下文、或你自己记住的 `chat_id`
> - `wecom-contact` 返回的 `userid`
> - 根据姓名、群名或任何其他字段自行构造 / 拼接的值
> - `wecom-chat` 的 `chat groups list` 返回的群会话 ID（那是给读历史用的，不是机器人可发送范围）
>
> 这些值**最多只能作为匹配线索**，最终发送参数必须重新取自本次 `sessions list` 的匹配项。
>
> **用户在多个候选中选完之后，还要再调一次 `sessions list`**，用选定对象重新匹配当次返回值，
> 再取 `chat_id`。会话列表按最后消息时间排序，用户思考的这段时间里顺序可能已经变了。
>
> 唯一豁免：目标是**授权人本人**时，用 `identity whoami` 的 ID，不走 `sessions list`。

匹配规则：

- **按聊天名称**：在本次 `sessions[]` 里按非空 `chat_name` **精确匹配**。
  不能精确匹配时**向用户反问确认发送目标**，不要模糊匹配后直接发。
- **「最近的那个会话」「最近第一个群」**：按 `sessions[]` **原始顺序**选择用户明确指定的那一项。
- **用户提供了 ID**：只能与本次 `sessions[].chat_id` 做**完全相等**校验；
  命中后仍然从匹配项复制 `chat_id`，**不能直接复用用户输入值**。

匹配结果的处理：

| 情况 | 处理 |
|---|---|
| 唯一匹配 | 进入 Step 3 |
| 多个候选 | 按返回顺序展示**聊天名 + 最后消息时间**（不展示 `chat_id`）让用户选；选完**重新调一次** `sessions list` |
| 无匹配 | **停止发送**，如实告知目标不在机器人最近的会话范围内；**不接受外部 `chat_id` 绕过限制** |
| `sessions_count = 0` | **停止发送**，告知当前没有可发送的最近会话 |

### Step 3：复述并取得同意，然后发送

```bash
wecom-cli message aibot send \
  --chat-id '<本次 sessions[].chat_id>' \
  --msg-type markdown \
  --markdown '{"content":"会议改到明天下午三点，请注意时间调整。"}'
```

发送成功后，只说明**目标（可读名称）和消息类型**，**不编造消息 ID**。
接口返回 `success` 布尔字段；失败时如实转达错误，不要换 `curl` / Python 等方式绕过 `wecom-cli`。

## 场景：发图片 / 文件 / 语音 / 视频

先把本地文件传成 `media_id`，再发送。**上传时的 `--type` 必须与发送时的 `--msg-type` 对齐。**

```bash
# Step A：上传（属于媒体能力，参数以 wecom-cli media upload --help 为准）
wecom-cli media upload --file-path '/abs/path/周报.pdf' --type file
# → 返回 media_id（内部流转，不外露）

# Step B：确认目标会话（同上，必须走本次 sessions list）
wecom-cli message aibot sessions list

# Step C：复述取得同意后发送
wecom-cli message aibot send \
  --chat-id '<本次 sessions[].chat_id>' \
  --msg-type file \
  --file '{"media_id":"<media_id>"}'
```

各类型的内容对象：

| `--msg-type` | 内容 flag | 必填字段 | 可选字段 |
|---|---|---|---|
| `markdown` | `--markdown` | `content`（1~20480 UTF-8 字节） | — |
| `image` | `--image` | `media_id`（上传时 `--type image`） | — |
| `file` | `--file` | `media_id`（上传时 `--type file`，文件名取上传时的原始文件名） | — |
| `voice` | `--voice` | `media_id`（上传时 `--type voice`，**源文件必须是真 AMR**） | — |
| `video` | `--video` | `media_id`（上传时 `--type video`） | `title` ≤128 字节、`description` ≤512 字节 |

**每次请求必须且只能携带一个与 `--msg-type` 同名的内容对象**：不要传空对象，也不要同时传多个。

```bash
# 视频带标题与描述
wecom-cli message aibot send \
  --chat-id '<本次 sessions[].chat_id>' \
  --msg-type video \
  --video '{"media_id":"<media_id>","title":"产品演示","description":"本周版本的核心功能演示"}'
```

用户没给视频标题或描述时**直接省略字段**，不传空字符串，也不要为非必填字段追问。

## 场景：发纯文本（`message send`）

先读完上面「两个发送方法怎么选」，确认确实需要这条路径。

```bash
wecom-cli message send \
  --chat-id '<会话 ID>' \
  --msg-type text \
  --text '{"content":"会议改到明天下午三点。"}'
```

- `--msg-type` **目前只支持 `text`**，传别的值会失败。
- `--text` 在 `--help` 里不标 `[必填]`，但 `msg_type=text` 时**不传必定失败**。
- `content` 上限 **2048 字符**（注意：这里是字符不是字节，与 markdown 的字节口径不同）。
- 返回体没有任何业务字段，成功与否由框架外壳的 `errcode` / `errmsg` 表达。

### `message send` 的 `chat_id` 来源

> 🔴 **实测结论（2026-09-03）：本方法在测试企业上返回 `853006`
> `this tool is not available for your corporation`——即整个企业不具备该能力，
> 不是机器人权限问题。** 而同一账号的 `message aibot send` 可以正常发送。
> ⇒ **优先且默认使用 `message aibot send`**；只有在用户明确要求「不以机器人身份发送」
> 且你已告知其未验证时才考虑本方法，遇 `853006` 直接说明企业未开通、不要重试。
>
> ⚠️ **本方法的发送身份与目标范围仍未经成功验证**（上游零覆盖，schema 无明文）。
> 它是 write-high 的对外发送，**发错不可撤回**。因此**默认不使用**；
> 确需使用时，除常规高风险确认外，还必须单独告知用户「这条路径未经验证」并取得同意。

**强制交叉校验**：调用 `message send` 之前，**必须先跑一次 `message aibot sessions list`**——

- 目标**命中** sessions list → **改用 `message aibot send`**（已验证路径优先，不要用本方法）
- 目标**未命中** → 向用户复述：
  「该目标不在机器人会话范围内，将以非机器人身份发送，且这条路径未经验证，仍要发吗？」
  得到明确同意后才继续

在满足上述交叉校验的前提下，合法来源只有三个：

| 会话类型 | 合法来源 | 附加要求 |
|---|---|---|
| 单聊 | `wecom-contact` 解析出的对方 `userid` | 用户在**本轮对话里逐字确认过收件人姓名** |
| 群聊 | `wecom-chat` 的 `chat groups list` 返回的 `chats[].chat_id` | 用户在**本轮对话里逐字确认过群名** |
| 授权人本人 | `identity whoami` | — |

同样**禁止**：用户直接给的 ID、历史缓存的 ID、按名字拼出来的值。

## 场景：把消息里的图片 / 文件 / 语音 / 视频取下来

配合 `wecom-chat` 拉到的消息列表使用——消息里的 `image` / `file` / `voice` / `video`
各带一个 `media_id`，用它取内容：

```bash
wecom-cli message files get --media-id '<消息里的 media_id>'
```

返回 `media_item`：

| 字段 | 说明 |
|---|---|
| `media_type` | `image` / `file` / `voice` / `video` |
| `file_name` | 媒体文件名（含扩展名）——**这是可以展示给用户的可读信息** |
| `content` | 内容不长时直接返回字符串 |
| `file_path` | 内容超长或含非 UTF-8 字节时由框架落盘，改用此字段返回**本地文件路径** |
| `media_id` | 与请求入参一致 |

**`content` 与 `file_path` 是二选一的**：小内容走 `content`，大内容/二进制走 `file_path`。
写代码处理时两个都要判。想固定落盘可以加 `-o <file>` 或 `--output-dir <dir>`（文件以 0600 写入）。

**`file_path` 属于禁露字段**：告诉用户「已取到文件『周报.pdf』」，不要把本地路径贴出来。

> ⚠️ 别和 `media download` 搞混（两者都叫 `--media-id`，但来源不同）：
> - `message files get --media-id` 取的是**聊天消息里的**媒体，`media_id` 来自
>   `chat messages list` 返回的 `image` / `file` / `voice` / `video.media_id`。
> - `media download --media-id` 取的是**由 CLI 上传后获得的** `media_id`
>   （schema 原文：「由 CLI 上传文件后获得」，框架层会把它解码为 cosid）。
>
> 两者的解码路径不同，互换很可能失败（**未实测**，但 schema 描述明确指向不同来源）。
> 拿到 `media_id` 时记住它是从哪个接口来的，用配套的方法取。

## 参数速查

| 方法 | 必填参数 | 关键可选参数 |
|---|---|---|
| `message aibot sessions list` | 无入参 | — |
| `message aibot send` | `--chat-id`、`--msg-type` | `--markdown` / `--image` / `--file` / `--voice` / `--video`（条件必填，与 `--msg-type` 同名的那个） |
| `message send` | `--chat-id`、`--msg-type` | `--text`（`msg_type=text` 时条件必填） |
| `message files get` | `--media-id` | — |

完整 schema 用 `wecom-cli message <path> --help` / `--doc` / `--schema` 自查。

## 易错点

- **`chat_id` 的来源约束是本技能的第一条命令**，比消息内容重要得多。发错人不可撤回。
  用户选完候选后**必须重新调 `sessions list`**——不要因为"刚才才查过"就跳过。
- **`sessions list` 最多 20 个会话，且不支持分页与过滤**。目标不在里面就是发不了，
  如实告知用户「对方不在机器人最近的会话范围内，需要对方先给机器人发一条消息」，
  不要试图用别的 ID 绕过。
- **上限的计量口径不一样**：markdown `content` 按 **UTF-8 字节**（20480），
  `message send` 的 `content` 按**字符**（2048），视频 `title` / `description` 按字节（128 / 512）。
  超限时**不要静默截断**，请用户缩短，或在用户明确同意后拆分发送。
- **条件必填字段的 `--help` 不标 `[必填]`**：`--markdown` / `--image` / `--file` / `--voice` /
  `--video` / `--text` 都是这样。`--msg-type` 传了什么，就必须传同名的内容 flag，否则请求失败。
- **语音必须是真 AMR**：改扩展名冒充 AMR 会失败。
- **`--dry-run` 不校验必填字段**（实测缺参数仍 exit 0），但它**很适合发送前自查请求体**：
  确认 `chat_id`、正文、消息类型都对了再真发。别把 dry-run 通过当成参数完整的证据。
- **连续发多条**时不必每条都重新 `sessions list` / `whoami`，
  但**上下文一旦发生压缩就要重新调**，确保 `chat_id` 仍然正确。
- **不编造消息 ID**。接口本身也不返回消息 ID（`message send` 返回体为空，
  `message aibot send` 只返回 `success`）。
- `chat_id` / `userid` / `media_id` / `file_path` 全部是内部调用值，**禁止面向用户展示**。
- 用户明确要求发送、且目标与内容都完整时，做完一次复述确认即可，**不要反复追问**；
  缺目标、缺内容或缺本地文件时**只追问缺失项**。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-message`。

相对上游的增量：补齐了上游未覆盖的 `message.send`（纯文本发送）与 `message.files.get`
（取消息媒体）两个方法，并为两个发送方法加上了 write-high 的确认要求。
