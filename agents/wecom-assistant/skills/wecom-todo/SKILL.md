---
name: wecom-todo
description: >-
  企业微信待办管理：创建待办（可分派给他人、可设截止时间与提醒）、查询与筛选待办列表、查待办详情、
  修改标题/描述/参与人/截止时间、标记完成、删除或退出待办。
  当用户说「记个待办 / 帮我记一下 / 加到待办里 / 我有哪些待办 / 未完成的待办 / 这条待办完成了 /
  把某某也加进去 / 改一下截止时间 / 删掉这条待办 / 我退出这条待办」时使用。
  不负责：日程与会议安排（wecom-calendar / wecom-meeting）、姓名转 userid（wecom-contact）、
  发消息提醒他人（wecom-message）；也不做语义检索（关键词是字面匹配）。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - todo
  - task
---

# 企业微信待办

把「这件事要做」记进企业微信待办系统：记一条、查一批、改内容、标完成、删掉或退出。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 已安装、版本达标、`auth show --status` 返回 `authorized`；具体版本门槛以 `wecom-shared` 为准）。
> 未通过前置检查时不得执行本技能任何命令。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 查待办列表（按时间/状态/关键词筛选） | `wecom-cli todo list` | read |
| 批量查待办详情 | `wecom-cli todo get` | read |
| 创建待办 | `wecom-cli todo create` | write-low（**传 `follower_ids` 时升级为 write-high**） |
| 更新待办 | `wecom-cli todo update` | write-low（**传 `followers` 时升级为 write-high**） |
| 完成待办 | `wecom-cli todo finish` | **write-high** |
| 删除 / 退出待办 | `wecom-cli todo delete` | **write-high** |

### 高风险与条件升级的确认要求

> ⚠️ **高风险操作**：`todo delete` 对创建人是**删除整条待办**（其他参与人也不再看到），对非创建人是**退出该待办**。
> CLI **没有任何恢复接口**。执行前必须向用户复述
> 「将删除待办「<标题>」（参与人 <人名>，删除后所有人都看不到，无法恢复）」或
> 「将把你从待办「<标题>」中移除（其他参与人不受影响）」并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作**：`todo finish` **没有反向的「取消完成」方法**；`finished_all: true` 会以创建人身份
> **把全体参与人的份一并标记完成**。执行前必须向用户复述
> 「将把待办「<标题>」标记完成（范围：仅你自己 / 全体参与人 <人名>），完成后无法通过本技能撤销」
> 并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作（条件升级）**：`todo create` 传了 `follower_ids` 时会**把待办分派给他人并触发提醒**，
> 对方待办列表里立刻出现这条。传该字段时按高风险处理：执行前必须向用户复述
> 「将创建待办「<标题>」并分派给 <人名列表>，他们会收到提醒」并取得明确同意；用户未明确同意时不得执行。
> 不传 `follower_ids`（只给自己记）时按 write-low 处理，可直接执行。

> ⚠️ **高风险操作（条件升级）**：`todo update` 传了 `followers` 时是**全量替换**语义 ——
> 没重新传进去的人会被踢出这条待办。传该字段时按高风险处理：执行前必须向用户复述
> 「将把待办「<标题>」的参与人整体改为 <新名单>，未列出的 <被移除的人名> 会被移出该待办」
> 并取得明确同意；用户未明确同意时不得执行。只改标题/描述/截止时间时按 write-low 处理，可直接执行。

## 场景：帮我记个待办

### 意图前置判断（调接口之前先做）

- 消息里**显式出现「待办」二字**（「创建一条待办」「加到待办里」「帮我记一个待办」）→ 在本技能内创建。
- 明确是「定时提醒的待办 / 待办提醒 / 创建待办并提醒」→ 在本技能内创建。
- **泛泛的提醒需求、没说要建企业微信待办** → **不要**擅自创建待办，先由上层确定承载方式
  （可能该用日程、可能该用调度任务）。

### 从用户原话里提参数（尽量别追问）

用户刚把事情讲清楚，再问一遍是劣体验。除非真的提不出，**不要**追问。

- **`title`（必填）**：优先「动宾」结构，尽量保留用户原始表达。
  **只有当消息里完全没有任何任务内容时**（只说「帮我记个待办」），才追问「要记什么事？」。
  哪怕只有一个动作或一个对象，也要先自己提炼。
- **`description`（多数情况不传）**：只在有**标题装不下的额外细节**（背景、要求、对接人、单号、链接）时才填。
  **禁止把 `description` 写成与 `title` 相同或仅是 title 的复述** —— 没有额外信息就不传，一条只有标题的待办完全正常。
- **`follower_ids`**：用户说「分派给我」「我和某某一起」时，**要把当前用户自己的 userid 也放进去**
  （后台不会自动把创建者算作参与人）。但「只给我自己创建、没有其他人」时**不用**把自己放进去。
  姓名必须经 `wecom-contact` 解析成 `userid`（`wo` 前缀），**禁止**拼接或编造。
- **`deadline` / `remind_at_deadline`**：见下文「截止时间与提醒」。没提任何时间就都不传，不追问。

### 命令

```bash
# 最简：只给自己记一条
wecom-cli todo create --json '{"items": [{"title": "把周报发出去"}]}'

# 带描述、分派人、截止时间与截止时提醒
wecom-cli todo create --json '{
  "items": [
    {
      "title": "准备周会材料",
      "description": "本周三上午周会需要的销售数据 PPT",
      "follower_ids": ["woxxxa", "woxxxb"],
      "deadline": {"type": "datetime", "value": "2026-09-03 09:00:00"},
      "remind_at_deadline": true
    }
  ]
}'

# 批量（单次最多 20 条）
wecom-cli todo create --json '{
  "items": [
    {"title": "订会议室"},
    {"title": "整理评审结论", "deadline": {"type": "date", "value": "2026-09-05"}}
  ]
}'
```

### 返回与回显

返回 `items[]`，与入参一一对应，每项含 `success` / `todo_id` / `title` / `followers[]`（含 `user_name`）/ `extra_info` / `errmsg`。

回显必须体现**标题、参与人、截止时间**三项（不存在的项直接缺省，**不要硬写「无」**）：

- **标题**：取返回的 `title`。
- **参与人**：取返回的 `followers[].user_name`，多人用 `、` 拼接；无参与人或仅创建者本人时缺省。**只展示人名。**
- **截止时间**：取**本次入参**的 `deadline.value` —— **返回体不回传 `deadline`**，必须用刚提交的值。

批量创建时逐条回显。示例：

> 已创建待办「准备周会材料」，参与人：张三、李四，截止时间：2026-09-03 09:00:00。

## 场景：我有哪些待办 / 未完成的待办

```bash
# 默认：只返回进行中（proceed）的待办，limit 默认 10
wecom-cli todo list --limit 20

# 已完成的待办 —— status_filter 必须显式传
wecom-cli todo list --json '{"status_filter": ["finished"], "limit": 20}'

# 全部（含已完成）
wecom-cli todo list --json '{"status_filter": ["finished", "proceed"], "limit": 20}'

# 按创建时间范围 + 关键词
wecom-cli todo list --json '{
  "create_begin_time": "2026-09-01 00:00:00",
  "create_end_time": "2026-09-07 23:59:59",
  "keywords": ["报销"],
  "limit": 20
}'

# 按截止时间范围（只有用户明确说「截止 / 到期 / ddl / 这之前要做完」时才用）
wecom-cli todo list --json '{
  "deadline_begin_time": "2026-09-01 00:00:00",
  "deadline_end_time": "2026-09-07 23:59:59",
  "status_filter": ["proceed"]
}'

# 拉全部分页（--page-count 是命令行参数，不要塞进 --json 里）
wecom-cli todo list --json '{"status_filter": ["finished", "proceed"], "limit": 20}' --page-count 10
```

### 筛选规则

- **`status_filter` 不传 = 只返回 `proceed`**。用户问「已完成的待办」要传 `["finished"]`，问「所有待办」要传 `["finished","proceed"]`。漏传会把「其实有」误判成「没有」。
- **枚举只有 `finished` / `proceed`**，**不接受 `deleted`**。用户要查已删除待办时直接说明列表接口不支持。
- **时间范围默认归到创建时间**：用户给「上周」「本月」这类范围但没点明创建还是截止时，用 `create_begin_time` / `create_end_time`。只有明确带「截止 / 到期 / deadline / ddl / 这之前要做完」才改用 `deadline_*`。
- **`keywords` 是字面命中过滤，不是语义检索**：数组元素之间 **OR**，单元素内空格分隔 **AND**。
  例：`["service ai", "claw"]` = `("service" AND "ai") OR "claw"`。
- **统计 / 计数 / 「有哪些」类需求必须翻完全部分页**（`--page-count` 取足够大，直到某页 `has_more` 为 `false`）。只读开头几页就下结论会严重少算；若结果被转存到文件，要把整个文件读完再统计。

### 返回

`items[]` + `has_more` + `next_cursor`。每条已含 `title` / `description` / `status` / `user_status` /
`creator`（含 `user_name`）/ `followers[]`（含 `user_name` / `user_status`）/ `deadline` / `extra_info` /
`source` / `create_time` / `update_time` —— **多数场景不必再调 `todo get`，也不必用 `wecom-contact` 反查人名**。

### 展示格式

**仅当用户直接询问待办列表时**才用本格式。`list` 被删除/完成/更新流程内部调用（为定位待办）时**不要**把列表展示给用户。

```markdown
## 进行中（N 条）

1. <title>
  - 创建人：<creator.user_name>
  - 参与人：<followers[].user_name 用「、」拼接>
  - 截止时间：<deadline.value>

## 已完成（M 条）

1. <title>
  ...
```

- 按 `status` 分组：`proceed` → `## 进行中（N 条）`，`finished` → `## 已完成（M 条）`；某组无数据则整组省略。
- **创建人是用户自己时缺省**；无参与人时缺省；无截止时间时缺省。
- 组内按 `deadline.value` 升序（无截止时间的排最后），截止时间相同按 `update_time` 倒序。

## 场景：这条待办现在什么状态

手上已有 `todo_id` 且需要核对最新 `status` / `user_status` 时才用（`list` 返回已经很完整）：

```bash
wecom-cli todo get --json '{"items": [{"todo_id": "<todo_id>"}, {"todo_id": "<todo_id2>"}]}'
```

单次最多 20 个，超出分批。返回字段与 `list` 条目相同，另有 `success` / `errmsg`。

## 场景：改一下这条待办

上下文没有 `todo_id` 时，**先用 `todo list` 定位**（修改场景通常查 `proceed` 即可）。

```bash
# 改标题 / 描述
wecom-cli todo update --json '{
  "items": [{"todo_id": "<todo_id>", "title": "调整后的周会材料"}]
}'

# 改截止时间并设为截止时提醒
wecom-cli todo update --json '{
  "items": [
    {
      "todo_id": "<todo_id>",
      "deadline": {"type": "datetime", "value": "2026-09-03 09:00:00"},
      "remind_at_deadline": true
    }
  ]
}'

# 改参与人 —— 全量替换！必须把要保留的人一并重传
wecom-cli todo update --json '{
  "items": [{"todo_id": "<todo_id>", "followers": [{"userid": "woxxxa"}, {"userid": "woxxxb"}]}]
}'

# 清空截止时间（空对象）+ 清空参与人（空数组）
wecom-cli todo update --json '{
  "items": [{"todo_id": "<todo_id>", "deadline": {}, "followers": []}]
}'
```

### `followers` 全量替换的正确做法

1. 先 `todo list` / `todo get` 取现有 `followers[]`。
2. 在本地合并（加人）或删减（去人），得到**完整的应保留名单**。
3. **剥掉 `user_name` / `user_status` / `update_time`，只保留 `userid`** —— 入参的 `followers` 子对象只接收 `userid`。
4. 把完整名单一次性传入。
5. 用户说「把我也加进去」「分派给我和某某」时，名单里**同样要带上当前用户自己的 `userid`**。

### 其他更新规则

- **避免冗余更新**：用户只是把已记录的内容又复述一遍（标题已等于用户这次说的内容），这是确认不是修改，**不要发起 `update`**，直接回「这条已经记好了」。尤其**不要把 `description` 更新成与 `title` 相同的内容**。
- **补全信息先查上下文**：用户要求「写清楚点」或补充参与人/时间/链接/单号时，先从当前会话与待办详情里找；能确定就更新，找不到或有歧义时再一次性向用户确认，别让用户重发。
- **未传的字段保持原值**。清空 `followers` 传 `[]`，清空 `deadline` 传 `{}`。
- 返回 `items[]`，每项含 `success` / `todo_id` / `title` / `extra_info` / `errmsg`。

## 场景：这条待办完成了

上下文没有 `todo_id` 时先 `todo list` 定位，**`status_filter` 要传 `["finished","proceed"]`**，避免把已完成的误判成找不到。

### 幂等检查（先做）

定位时若发现该待办整体 `status = finished`，或当前用户 `user_status = finished`，说明已完成 ——
**直接告知「这条待办已完成」，不要再调 `finish`**。只有用户本次或本会话前文明确要求「完成后删除/清掉」时才继续走删除流程。

### 决定 `finished_all`

| 用户表述 | 传法 |
|---|---|
| 明确「仅我完成自己的部分」（「我这边搞完了」「先把我那块标了」） | **显式**传 `finished_all: false`（显式 false 才能让后端跳过 `ask_finish_all` 兜底） |
| 明确「全部完成」（「这条结掉」「都搞完了」），或本会话已对同一 `todo_id` 调过一次 `finished_all: false`、用户又说要完成 | 传 `finished_all: true` |
| 表达不明确（只说「完成 XX 待办」） | **不传** `finished_all`，让后端走 `ask_finish_all` 流程 |

```bash
# 只完成自己那份
wecom-cli todo finish --json '{"items": [{"todo_id": "<todo_id>", "finished_all": false}]}'

# 全体一并完成（仅创建人可用）
wecom-cli todo finish --json '{"items": [{"todo_id": "<todo_id>", "finished_all": true}]}'

# 让后端决定是否需要追问范围
wecom-cli todo finish --json '{"items": [{"todo_id": "<todo_id>"}]}'
```

### `ask_finish_all` 处理

返回里出现 `ask_finish_all` 字段，说明当前用户既是创建人又是参与人，**第一次调用已把自己那份标记完成**。
此时必须用文字确认是否把其他参与人也一并标记完成，提问里要含待办标题和参与人中文名（用 `、` 拼接）：

```
待办「<待办标题>」中您的部分已完成。参与人：<参与人姓名>。请选择完成范围：仅我完成，还是已完全完成？
```

- 用户选**「仅我完成」** → **不再调接口**（第一次已完成自己那份），告知已标记完成。
- 用户选**「已完全完成」** → 用同一 `todo_id` 再调一次 `todo finish`，传 `finished_all: true`。

## 场景：删掉这条待办 / 我退出这条待办

`delete` 一个接口承载两种语义，取决于当前用户是不是创建人：

| 情况 | 语义 |
|---|---|
| `creator.userid` == 当前用户 | **删除整条待办**，其他参与人也不再看到 |
| `creator.userid` != 当前用户 | **当前用户退出该待办 / 从自己的待办中移除**，不影响其他人 |

**非创建人也可以调 `delete`。** 不要因为 `creator.userid` 不是当前用户就拒绝，
也不要回「创建人之外无权删除」之类的话术 —— 核对创建人只是为了**理解语义、组织话术和做幂等判断**。

```bash
wecom-cli todo delete --json '{"items": [{"todo_id": "<todo_id>"}, {"todo_id": "<todo_id2>"}]}'
```

- 上下文没有 `todo_id` 时先 `todo list` 定位，**`status_filter` 要传 `["finished","proceed"]`**，
  否则可能找不到（默认只返回 `proceed`）。列表返回的 `creator` / `user_status` 用于判断语义和避免重复操作。
- 用户说某待办「已完成」时**默认是完成操作，不等于删除**；只有明确说删除才调本接口。
- 返回 `items[]`，每项含 `success` / `todo_id` / `title` / `errmsg`。

## 截止时间与提醒（`deadline` / `remind_at_deadline`）

### `deadline` 结构

| 字段 | 类型 | 必填 | 语义 |
|---|---|:--:|---|
| `type` | string | 是 | `date`（**用户没提具体时分秒时一定选它**）/ `datetime`（用户提了具体时刻） |
| `value` | string | 是 | `type=date` → `YYYY-MM-DD`；`type=datetime` → `YYYY-MM-DD HH:mm:ss` |

```json
{ "type": "date",     "value": "2026-09-05" }
{ "type": "datetime", "value": "2026-09-05 09:00:00" }
```

- `deadline` **整体可选**；一旦提供，内部 `type` 与 `value` 都必填。
- **清空**已设置的截止时间：把 `deadline` 更新为**空对象 `{}`**（`update` 专用）；不传该字段则保持原值。
- **返回体不回传 `deadline`**（`create` / `update` 的结果里没有这个字段），回显时用本次入参的值。
- 未设置截止时间的待办，在 `list` / `get` 里 `deadline` 不返回或为 `null`。

### 从用户输入推断 `deadline`

日期/星期直接限定任务本身时，也视为截止日期 —— 「周三开会要带笔记本」应把周三写进 `deadline`。

1. **要「定时提醒」且给了具体时刻** → 该时刻落为 `deadline.type=datetime`，并传 `remind_at_deadline: true`。
2. **只说截止/到期时间，或只给了任务发生日期** → 只填 `deadline`，**不传** `remind_at_deadline`（按后台默认提前时间提醒）。
3. **只给了日期没给时刻** → `type=date`、`value="YYYY-MM-DD"`，**不传** `remind_at_deadline: true`（date 类型会忽略该参数）。
4. **完全没提截止/提醒/任务发生时间** → `deadline` 与 `remind_at_deadline` 都不传，**不追问**。

### `remind_at_deadline` 的三条硬语义

- **必须与 `deadline` 同传**。脱离 `deadline` 单独传**不会生效**，不要这么传。
- `true` → 在**截止时刻**提醒（**仅 `type=datetime` 有效**，`date` 类型会被忽略）。
  `false` 或不传 → 按**后台默认提前时间**提醒（schema 声明：`date` → 18:00，`datetime` → 提前 15 分钟）。
- **入参层面没有「关闭提醒」这一档**。`false` ≠ 关闭。用户要「取消提醒 / 别提醒了」时直接告知不支持关闭待办提醒；
  若用户坚持完全不提醒，唯一办法是**连同截止时间一起清空**（`deadline: {}`，会一并删掉截止时间），须先向用户确认再操作。

### 「xx 时间截止，并提前 yy 提醒」

`deadline` **永远填用户说的 xx 截止时间**，不要填提前后的提醒时刻。
当前入参**不能直接设置「提前 yy」**。创建/更新后用返回的 `extra_info` 判断系统提醒时间是否刚好满足 yy：

- 匹配 → 说明已满足。
- 不匹配或无 `extra_info` → 按固定话术说明：
  `目前不支持直接创建您需要的提醒时间，已为您设置截止时间为 XX，请到企业微信待办功能中手动修改提醒时间。`（XX 填本次 `deadline.value`）

### 提醒说明的输出要求

本次传了 `remind_at_deadline: true` 或用户提到提醒诉求，且操作成功时，**必须**在回显之后附上提醒说明：

- 用户要「截止时/到点提醒」→ 只有 `type=datetime` 才该传 `true`；若 `extra_info` 不等于 `deadline.value` 或缺失，仍要引导到企业微信待办功能里改提醒时间。
- 有 `extra_info`（且非「提前 X 提醒」场景）→ 引用 `extra_info` 里的时刻告诉用户届时会自动提醒。
- 无 `extra_info`（且非「提前 X 提醒」场景）→ 说明返回未确认提醒时间，引导用户到企业微信待办应用里检查/修改。
- **不要另建定时任务来模拟待办提醒**，会重复提醒。
- 仅带 `deadline` 但未要求提醒的普通待办，**无需**额外提醒说明。

## 参数速查

> flag 与 JSON 字段一一对应：`--items` ↔ `items`，`--status-filter` ↔ `status_filter`，其余同理。
> `create` / `update` / `finish` / `delete` / `get` 五个方法的参数只有 `items` 一项，**必须用 `--json`**。
> 完整 schema 用 `wecom-cli todo <method> --help` 或 `--doc` 查。

| 方法 | 参数 | 上限与要点 |
|---|---|---|
| `todo create` | `items[]`：`title`（必填，1~4000）、`description`（≤4000）、`follower_ids`（**字符串数组**，≤50）、`deadline`、`remind_at_deadline` | `items` 1~20 |
| `todo update` | `items[]`：`todo_id`（必填）、`title`、`description`、`followers`（**对象数组** `[{"userid":"..."}]`，≤50，**全量替换**）、`deadline`（`{}` = 清空）、`remind_at_deadline` | `items` 1~20 |
| `todo finish` | `items[]`：`todo_id`（必填）、`finished_all`（默认 false） | `items` 1~20 |
| `todo delete` | `items[]`：`todo_id`（必填） | `items` 1~20 |
| `todo get` | `items[]`：`todo_id` | `items` 1~20 |
| `todo list` | `create_begin_time` / `create_end_time` / `deadline_begin_time` / `deadline_end_time` / `status_filter`（`finished` \| `proceed`）/ `keywords` / `limit` / `cursor` | `limit` 1~20（默认 10）；`keywords` ≤100；命令行 `--page-count N` 自动翻页 |

**时间格式**：`create_*` / `deadline_*` 过滤参数与 `deadline.type=datetime` 都用 `YYYY-MM-DD HH:mm:ss`；
`deadline.type=date` 用 `YYYY-MM-DD`。必须先把「明天」「下周三」解析成具体日期再传。

## 状态枚举

| 字段 | 取值 |
|---|---|
| `status`（待办整体） | `proceed` 进行中 / `finished` 已完成 / `deleted` 已删除（**只出现在返回里，不能传给 `status_filter`**） |
| `user_status`（当前用户在该待办的状态） | `accept` / `reject` / `finished` / `removed` / `notshow` |
| `source`（来源） | `single_chat` 单聊 / `group_chat` 群聊 / `doc` 文档 / `ai_summary` 智能总结 / `meeting_summary` 会议纪要 / `face_chat` 面聊 / `fused_doc` 融合文档 / `smart_sheet` 智能表格 / `smart_doc` 智能文档 / `JSAPI` |

## 输出格式

- **禁止把 `todo_id` 展示给用户**，任何场景、任何理由都不放宽。
- 参与人 / 创建人一律展示 `user_name`（格式如 `zhangsan(张三)`，原样使用），**禁止展示 `userid`**。
- `cursor` / `next_cursor` 属内部标识，同样禁止展示。
- 不存在的字段直接缺省，**不要硬写「无」**。

## 易错点

- **`items` 标着「可选」，但不传就失败**：schema 里 `items` 不在 `required` 数组里、`--help` 也不给 `[必填]` 标记，
  但它带 `@minItems 1` —— **不传或传空数组一律调用失败**。这是 `create` / `update` / `finish` / `delete` / `get`
  五个方法共有的陷阱，唯一不受影响的是 `list`（参数平铺、不进 `items` 壳）。
- **`todo update` 的 `followers` 是全量替换，不是增量添加**：漏传等于**把人踢出待办**。
  必须先 `list` / `get` 取现有名单，本地合并后把**完整名单**重新传入。这是本技能最危险的一个字段。
- **`create` 用 `follower_ids`（字符串数组），`update` 用 `followers`（对象数组）** —— 字段名和形状**都不一样**，
  互相照抄必失败。`create`：`"follower_ids": ["woxxx"]`；`update`：`"followers": [{"userid": "woxxx"}]`。
- **`update` 的 `followers` 子对象只接收 `userid`**：从 `list` / `get` 拿到的 `followers[]` 还带
  `user_name` / `user_status` / `update_time`，转入更新入参前必须全部剥掉。
- **`status_filter` 不传只返回进行中**：查「已完成」「全部」必须显式传；删除和完成前的定位一律传 `["finished","proceed"]`，否则可能找不到。
- **`status_filter` 不接受 `deleted`**（枚举只有 `finished` / `proceed`），尽管返回体的 `status` 里有 `deleted`。
- **`remind_at_deadline=false` 不是关闭提醒**，而是按后台默认提前时间提醒；入参层面根本没有关闭提醒这一档。
- **`remind_at_deadline` 脱离 `deadline` 单独传无效**，且对 `deadline.type=date` 会被忽略。
- **返回体不回传 `deadline`**：回显截止时间必须用本次入参的 `deadline.value`，别去返回里找。
- **`finish` 没有反向操作**：本技能无法「取消完成」，标完就只能到客户端处理。执行前的幂等检查不能省。
- **`finished_all: true` 会代全员完成**：表达不明确时不要自作主张传 true，交给后端的 `ask_finish_all` 流程。
- **`delete` 对非创建人是「退出」不是「删除」**：不要拒绝非创建人的删除请求，也别用「无权删除」的话术。
- **`keywords` 是字面匹配不是语义检索**：用户描述与待办原文用词不同就搜不到，此时该放宽关键词或改按时间范围列，而不是断言「没有这条待办」。
- **统计类问题必须翻完全部分页**：`limit` 上限只有 20，只看首页就报数会严重少算。
- **`--page-count` 是命令行参数**，写在 `--json '...'` 之外，塞进 JSON 体里不生效。
- **别把 `description` 写成 `title` 的复述**：没有额外信息就不传。
- **别另建定时任务模拟待办提醒**，会造成重复提醒。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-todo`。
