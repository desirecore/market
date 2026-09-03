---
name: wecom-calendar
description: >-
  企业微信日程与会议室管理：预约/查看/搜索/改期/取消日程，查多人共同空闲时段，查办公楼与会议室可订性并预订会议室。
  当用户说「约个日程 / 明天有什么安排 / 我的日历 / 项目评审是什么时候 / 挪一下时间 / 这个不开了 /
  张三什么时候有空 / 大家什么时候都有空 / 订个会议室 / 1605 空不空 / 公司有哪些楼」时使用。
  只负责『日程』——不含在线会议链接的安排（含纯线下面对面碰头）；用户要的是含会议号/入会链接的『在线会议』时改用 wecom-meeting。
  用户只说「开会/约个会/xx 会」而未说明是日程还是会议时，创建场景必须先逐字追问这一句、不得改写：
  `需要创建日程还是会议？（请回复：日程 / 会议）`（禁止改成「在线会议/视频会议/线下会议/日程安排」等任何变体）；
  查询场景则严禁追问，日程与会议两边都查再合并。
  不负责：待办事项（wecom-todo）、姓名转 userid（wecom-contact）、发消息通知（wecom-message）。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - calendar
  - schedule
  - meeting-room
---

# 企业微信日程与会议室

帮用户把「什么时候、和谁、在哪儿」这件事落到企业微信日历上：约日程、看安排、找时间、订会议室、改期、取消。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 已安装、版本达标、`auth show --status` 返回 `authorized`；具体版本门槛以 `wecom-shared` 为准）。
> 未通过前置检查时不得执行本技能任何命令。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 查某段时间的日程列表 | `wecom-cli calendar schedules list` | read |
| 按关键词/组织人/参与人搜索日程 | `wecom-cli calendar schedules search` | read |
| 按 ID 批量取日程详情 | `wecom-cli calendar schedules get` | read |
| 查多人共同空闲时段 | `wecom-cli calendar schedules free list` | read |
| 查企业办公楼清单 | `wecom-cli meeting rooms buildings list` | read |
| 查会议室可订性 | `wecom-cli meeting rooms search` | read |
| 创建日程（可邀请参与人、可占会议室） | `wecom-cli calendar schedules create` | **write-high** |
| 更新日程（改时间/地点/人/会议室） | `wecom-cli calendar schedules update` | **write-high** |
| 取消（删除）日程 | `wecom-cli calendar schedules cancel` | **write-high** |

> 会议室与办公楼查询虽然命令前缀是 `meeting`，但**归本技能**（`wecom-meeting` 要订会议室须反向调用本技能）。

### 三个高风险方法的确认要求

> ⚠️ **高风险操作**：`calendar schedules create` 带 `attendees` 时会向他人发出日程邀请，对方日历上立刻出现这条安排；传 `meeting_room_id` 时会真实占用会议室。执行前必须向用户复述
> 「将创建日程「<主题>」，时间 <开始>-<结束>，邀请 <人名列表>，会议室 <会议室名>」并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作**：`calendar schedules update` 改时间/地点/参与人/会议室会通知全体参与人，且被移除的人会直接失去这条日程。执行前必须向用户复述
> 「将把日程「<主题>」的 <改动项> 改为 <新值>，参与人会收到变更通知」并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作**：`calendar schedules cancel` 会删除日程并通知全体参与人，CLI **没有任何恢复接口**。执行前必须向用户复述
> 「将取消日程「<主题>」（<时间>），参与人会收到取消通知，且无法撤回」并取得明确同意；用户未明确同意时不得执行。

## 日程 vs 会议消歧 [CRITICAL｜措辞逐字固定]

企业微信里「会」有两种载体，判据只有一条：

- **含会议号（`meeting.meeting_code`）/ 入会链接（`meeting.meeting_link`）的是「会议」** → 归 `wecom-meeting`
- **不含会议号与入会链接的是「日程」**（包括纯线下面对面碰头、订了会议室的线下会）→ 归本技能

`search` / `list` / `get` 返回的每条日程都带 `meeting` 字段，**直接读 `meeting.meeting_code` 是否非空即可判定，不需要额外补一次 `get`**。

### 规则一：创建场景必须逐字追问

用户只说「开会 / 约个会 / 安排个会 / xx 会 / xx 会议」等而未明确是日程还是会议时，**必须先用文字追问**，问题与选项**逐字固定、不得改写、不得增减、不得翻译**：

```
需要创建日程还是会议？（请回复：日程 / 会议）
```

- 用户答「日程」→ 留在本技能，走「场景：约一个日程」。
- 用户答「会议」→ 转 `wecom-meeting` 创建会议（创建会议会自动生成对应日程，**不要**在本技能再建一条）。
- 「会议」「会」「开会」这些词**本身不构成「明确」**，禁止因 query 里出现「会议」二字就默认创建日程，也禁止反向默认成会议。
- **只给了地点或会议室号**（「在 1605 开会」「订个会议室开会」）**也不构成明确** —— 会议室里同样可能要远程接入，仍须追问。
- 只有出现「碰个面 / 创建日程 / 面对面聊」等纯线下信号时才直接留在本技能；出现「入会链接 / 会议号 / 视频会议 / 远程参会 / 外地同事接入」等信号时直接转 `wecom-meeting`，都无需追问。

### 规则二：查询场景严禁追问，两边都查再合并

查询场景**严禁**用上面那句话追问（那句话只用于创建）。按两个独立维度处理：

**维度一 —— 查哪一边**

| 用户表述 | 动作 |
|---|---|
| 明确提到「在线会议 / 视频会议 / 入会链接 / 会议号 / 腾讯会议 / 远程参会」 | 只查会议（转 `wecom-meeting`） |
| 明确说「日程 / 安排 / 我的安排 / 日历 / 今天有什么安排」且无在线会议特征 | 只查日程（本技能） |
| 模糊表述：「会 / xx 会 / xx 会议 / 开会 / 最近有什么会 / 有哪些会 / 找下 xx 会议」 | **日程和会议两边都查**，再合并 |

**维度二 —— 每一边用 `search` 还是 `list`（与维度一独立，逐边各判）**

- 有**主题/名称关键词**（「项目评审是什么时候」「找下 xx 会」）→ 该边用 `search`，关键词进 `keywords`。
- **只有时间/日期或泛浏览**（「今天有什么安排」「最近有什么会」）→ 该边用 `list`。
  **禁止把日期当 `keywords` 喂给 `search`。**

**合并展示**：两边都查时，按是否含在线会议链接分成「（会议）」与「（日程）」两部分（日程中 `meeting.meeting_code` 非空的归「（会议）」），同一场按「主题 + 时间」去重只保留一条，末尾汇总「共 N 场，其中会议 X 场、日程 Y 场」。只有一类时不分部分、不加小标题。

### 规则三：改约禁止拆成 cancel + create

「改约 / 改时间 / 挪到 / 顺延 / 重新约」等改期意图，**即使用户说「取消……再约到……」也算改期**，一律走 `update`：

1. 先 `search` 或 `list` 定位，直接读返回里的 `meeting.meeting_code`。
2. `meeting_code` **为空**（纯日程）→ `calendar schedules update` 改时间。
3. `meeting_code` **非空**（会议形态日程）→ 转 `wecom-meeting`，把 `meeting.meeting_id` 传给 `meeting update`，**无需再 search 一次**。

> **根因**：`calendar schedules create` 只能建纯日程、**重建不出会议链接**（能拆不能合）。cancel + create 会让**会议链接永久丢失**，参与人拿到的旧链接全部作废。这条禁令没有例外，不得以「用户自己说要先取消」为由绕过。

## 场景：约一个日程

### 步骤

1. **消歧**（见上文规则一）。确认是「日程」后继续。
2. **补必填参数**：`subject` / `begin_time` / `end_time` 缺失，或参与人无法从上下文推断时，用文字询问；其余可选参数（地点、提醒）用户没提就走默认，不专门问。
   - `end_time` 用户没给 → 默认 `begin_time + 1 小时`，不追问。
   - 询问时间时候选必须是**精确到分钟的具体时刻**（「明天 14:00」「周六 10:30」），禁止给「上午 / 下午 / 下班前」这类模糊选项。
3. **姓名 → userid**：调 `wecom-contact` 解析，多候选时列 2~4 个（姓名 + 部门）让用户选。**禁止**把姓名当 userid 拼接，**禁止**凭记忆编造。
4. **查忙闲**（多人时必做）：`calendar schedules free list`，把冲突摆给用户拍板。
5. **订会议室**（用户提到会议室时必做）：见「场景：订会议室」。必须先拿到真实 `meeting_room_id` 再建日程。
6. **复述并取得同意**（write-high 确认要求）。
7. **执行创建**。

### 命令

```bash
# 只给自己的日程（无参与人）
wecom-cli calendar schedules create \
  --subject '午餐' \
  --begin-time '2026-09-01 12:00:00' \
  --end-time '2026-09-01 13:00:00'

# 带参与人 —— attendees 是对象数组
wecom-cli calendar schedules create --json '{
  "subject": "产品评审",
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "attendees": [{"userid": "woxxxa"}, {"userid": "woxxxb"}]
}'

# 全天日程
wecom-cli calendar schedules create --json '{
  "subject": "年假",
  "begin_time": "2026-09-10 00:00:00",
  "end_time": "2026-09-10 23:59:59",
  "is_all_day": true
}'

# 建日程 + 原子占用会议室（meeting_room_id 来自 rooms search）
wecom-cli calendar schedules create --json '{
  "subject": "产品评审",
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "attendees": [{"userid": "woxxxa"}],
  "meeting_room_id": "mrmxxxx"
}'

# 自定义提醒（提前 30 分钟；不传时默认 [-900] 即提前 15 分钟）
wecom-cli calendar schedules create --json '{
  "subject": "客户拜访",
  "begin_time": "2026-09-02 09:00:00",
  "end_time": "2026-09-02 10:00:00",
  "location": "客户现场",
  "reminders": {"is_remind": true, "reminder_time": [-1800]}
}'
```

**创建返回**只有 `schedule_id` 一个字段（内部标识，禁止展示）。需要回显完整信息时用本次入参回显，或用 `schedules get` 补齐。

### 创建成功后的回复格式

只输出三行，不加寒暄、不加建议、不展示地点/提醒/`schedule_id`：

```
主题：{subject}
时间：{M月D日} {HH:mm}-{HH:mm}
参与人：{人名1}、{人名2}
```

## 场景：看看我今天/这周有什么安排

只给了时间、没有主题关键词 → **走 `list`**。

```bash
# 今天
wecom-cli calendar schedules list --begin-time '2026-09-01 00:00:00' --end-time '2026-09-01 23:59:59'

# 本周
wecom-cli calendar schedules list --json '{"begin_time": "2026-08-31 00:00:00", "end_time": "2026-09-06 23:59:59"}'
```

返回 `schedule_list[]`，每条已含 `subject` / `begin_time` / `end_time` / `attendees[].name` / `creator_name` / `repeat_rule` / `meeting` / `meeting_room`，**不必再调 `get`**。

若用户表述模糊（「最近有什么会」），按消歧规则二**同时**转 `wecom-meeting` 用相同时间范围拉 `meeting list`，合并展示。

## 场景：项目评审是什么时候（按关键词找日程）

有主题关键词 → **走 `search`**。`keywords` / `organizer` / `has_attendees` **至少传其一**，三者都不传会失败。

```bash
# 按关键词
wecom-cli calendar schedules search --keywords '项目评审'

# 关键词 + 时间范围
wecom-cli calendar schedules search --json '{
  "keywords": ["周会"],
  "begin_time": "2026-09-01 00:00:00",
  "end_time": "2026-09-07 23:59:59"
}'

# 按组织人（organizer 是单值字符串，不是数组）
wecom-cli calendar schedules search --json '{"organizer": "woxxx"}'

# 按参与人（has_attendees 是对象数组）
wecom-cli calendar schedules search --json '{"has_attendees": [{"userid": "woxxx"}]}'

# 翻页
wecom-cli calendar schedules search --json '{"keywords": ["周会"], "cursor": "<next_cursor>", "limit": 50}'
```

搜索无结果时给恢复建议：换关键词 / 改按组织人搜 / 改按参与人搜，不要静默失败。

## 场景：拿到 ID 后补日程详情

`list` 与 `search` 返回已足够完整，只有在**手上只有 `schedule_id`** 时才用：

```bash
wecom-cli calendar schedules get --json '{"schedule_ids": ["<schedule_id1>", "<schedule_id2>"]}'
```

> `schedule_ids` 是**纯字符串数组**，不是对象数组 —— 与 `attendees` / `meeting_ids` 的形状不同，最容易写错。

## 场景：大家什么时候都有空

```bash
wecom-cli calendar schedules free list --json '{
  "userids": [{"userid": "woxxx"}, {"userid": "woyyy"}],
  "begin_time": "2026-09-01 09:00:00",
  "end_time": "2026-09-01 18:00:00",
  "min_duration_minutes": 60,
  "limit": 5
}'
```

- `userids` **是对象数组** `[{"userid": "..."}]`，尽管字段名叫 `userids`。单人合法（退化为「某人什么时候有空」）。
- 单次窗口 **≤ 24 小时**；`begin_time` 早于当前时刻的部分会被服务端**自动截断**，传纯历史窗口返回空 `slots`。
- 返回 `slots[]`，每项含 `begin_time` / `end_time` / `available_users[]`（含 `name`）/ `available_count` / `busy_users[]`，另有 `total_count`（入参人数）与 `extra_info`（降级提示）。
- `available_count < total_count` 说明降级了：告诉用户哪些人冲突、几人能参加，由用户决定是否按降级时段安排。
- `slots` 为空 → 引导扩大窗口或减少参与人，**不要在同一窗口反复重试**。
- 展示时只用 `available_users[].name` / `busy_users[].name`，**输出正文里绝不允许出现 `wo` 前缀字符串**。

## 场景：订会议室 / 查会议室空不空 / 公司有哪些楼

完整编排、返回结构与五条硬性规则见 [`references/meeting-room.md`](references/meeting-room.md)。要点：

```bash
# 列出我可访问的办公楼（无入参）
wecom-cli meeting rooms buildings list

# 查会议室可订性（begin-time / end-time 必填）
wecom-cli meeting rooms search --json '{
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "room_name": "1605",
  "floor_name": "16",
  "capacity_min": 4
}'
```

- **只有用户提到楼名时才调 `buildings list`**；没提楼就跳过，让 `rooms search` 用当前所在楼兜底。
- `rooms search` 返回 `target[]`（传了 `room_name` 时的命中项，每项含 `status`：`bookable` / `unavailable` / `not_found`）+ `recommendations[]`（同楼候选）+ `inferred_building`。
- 拿 `target[].room.meeting_room_id` 或 `recommendations[].meeting_room_id` 传给 `schedules create` / `schedules update` 才算真正占用。
- **会议室名绝不能只写进 `location`** —— 那样不会占用会议室。
- `meeting_room_id` 仅工具链流转，对用户只展示会议室 `name` + 楼层 + 容量。

## 场景：改期 / 改地点 / 加减人 / 换会议室

先按消歧规则三判定归属，确认是纯日程后：

```bash
# 改时间
wecom-cli calendar schedules update --json '{
  "schedule_id": "<schedule_id>",
  "begin_time": "2026-09-02 14:00:00",
  "end_time": "2026-09-02 15:00:00"
}'

# 加人 / 减人（Patch 语义，只传要改的）
wecom-cli calendar schedules update --json '{
  "schedule_id": "<schedule_id>",
  "add_attendees": [{"userid": "woxxxc"}],
  "remove_attendees": [{"userid": "woxxxb"}]
}'

# 换会议室（新会议室须先经 rooms search 确认 status=bookable）
wecom-cli calendar schedules update --json '{"schedule_id": "<schedule_id>", "meeting_room_id": "mrmyyyy"}'

# 清空地点/备注：传空字符串
wecom-cli calendar schedules update --json '{"schedule_id": "<schedule_id>", "location": "", "description": ""}'
```

- **周期日程（`repeat_rule.is_repeat = true`）不支持更新**，告知用户并引导其到企业微信客户端操作；禁止逐场 `update` 拼凑、禁止 cancel + create 重建。
- **不预先按「是不是本人创建」拦截**：直接执行，返回权限错误时再告知用户并建议联系创建人。
- 返回 `detail`（更新后的完整 `ScheduleInfo`），可据此回显。

## 场景：取消日程

1. 定位（有主题关键词走 `search`，只给时间走 `list`）。
2. 读 `repeat_rule.is_repeat` —— **周期日程不支持取消**，引导到客户端。
3. 判断用户是真取消还是改期（带「取消」字样也可能是改期，见规则三）。
4. 复述并取得同意（write-high 确认要求）。
5. 执行：

```bash
wecom-cli calendar schedules cancel --schedule-id '<schedule_id>'
```

成功返回空对象 `{}`；无权限返回错误 —— 此时告知用户并建议联系创建人。

## 参数速查

> flag 与 JSON 字段一一对应：`--begin-time` ↔ `begin_time`，`--meeting-room-id` ↔ `meeting_room_id`，其余同理。嵌套结构（`attendees` / `reminders` / `timezone`）建议直接用 `--json`。完整 schema 用 `wecom-cli <service> <method> --help` 或 `--doc` 查。

| 方法 | 必填 | 关键可选 |
|---|---|---|
| `calendar schedules create` | `subject`、`begin_time`、`end_time` | `attendees`（对象数组）、`location`、`meeting_room_id`、`description`、`is_all_day`、`allow_self_join`（默认 true）、`reminders`（`{is_remind, reminder_time:[秒]}`，默认 `[-900]`）、`timezone`、`mark_optional_attendees`（**字符串数组**） |
| `calendar schedules update` | `schedule_id` | `subject`、`begin_time`、`end_time`、`add_attendees`、`remove_attendees`、`location`（空串=清空）、`description`（空串=清空）、`meeting_room_id`、`is_all_day`、`allow_self_join` |
| `calendar schedules cancel` | `schedule_id` | — |
| `calendar schedules list` | 无 | `begin_time`（默认当前时间）、`end_time`（默认起点 +30 天） |
| `calendar schedules search` | 无（但 `keywords` / `organizer` / `has_attendees` **至少传其一**） | `begin_time`、`end_time`、`limit`（默认 10，最大 1000）、`cursor` |
| `calendar schedules get` | `schedule_ids`（**字符串数组**） | — |
| `calendar schedules free list` | `begin_time`、`end_time`、`userids`（**对象数组**，≥1） | `min_duration_minutes`（默认 30）、`limit`（默认 10，最大 100）、`strategy`（仅 `max_attendees`） |
| `meeting rooms search` | `begin_time`、`end_time` | `room_name`、`building_name`、`city_name`、`floor_name`、`capacity_min`、`expand_to_other_buildings`、`limit`（默认 20，上限 100）、`cursor` |
| `meeting rooms buildings list` | 无入参 | — |

**时间格式**统一 `YYYY-MM-DD HH:MM:SS`，且必须先把「明天」「下周三」解析成具体时刻再传。

## 输出格式

- **姓名原样展示**：一律用接口返回的 `attendees[].name`，返回 `zhangsan(张三)` 就展示 `zhangsan(张三)`，不做加工。
- **年份**：默认只到月日；跨年时才补 `{YYYY}年M月D日`。
- **相对日期**：昨天/今天/明天在月日前加相对词，如 `时间：明天 9月1日 14:00-15:00`。
- **列表**：禁止 markdown 表格；按开始时间升序，每条独立条目，只含主题/时间/参与人；超过 10 条只展示前 10 条并告知「还有 N 条，需要查看更多吗？」。
- **时区标注**：`timezone.timezone_offset != 28800` 时必须标注，格式 `14:00-15:00（纽约时间 UTC-5）`；`UTC±N = timezone_offset / 3600`，地区中文名由 `timezone_id` 推导，`timezone_id` 为空时只留 `（UTC-5）`。东八区不标注。忙闲 `slots` 不适用。
- **禁止展示**：`schedule_id`、`userid`、`meeting_room_id`、`cal_id`、`cursor` / `next_cursor` 等一切内部标识。

## 不支持的事（直接告知，禁止变通绕过）

| 不支持 | 正确做法 |
|---|---|
| 创建 / 更新 / 取消**周期（重复）日程** | 告知不支持，引导到企业微信客户端；禁止用「建多条单次日程」「逐场 update」「cancel + create」变通 |
| **RSVP**（接受 / 拒绝 / 待定日程邀请） | 告知不支持，建议在客户端对该邀请操作，或私信发起人 |
| 给机器人授予某个日历本权限 | 不存在该能力 |

## 易错点

- **消歧措辞不得改写**：创建场景那句问话必须逐字是 `需要创建日程还是会议？（请回复：日程 / 会议）`，不得改成「线上还是线下」「视频会议还是普通日程」等任何变体。
- **查询场景严禁追问**，模糊表述必须日程 + 会议两边都查再合并 —— 追问本身就是错误。
- **改约禁止 cancel + create**：会议链接不可重建，一旦拆开就永久丢失。
- **三种 ID 集合形状各不相同**：`schedules get` 用 `schedule_ids: ["a","b"]`（字符串数组）；`attendees` / `add_attendees` / `remove_attendees` / `has_attendees` / `free list` 的 `userids` 用 `[{"userid":"wo..."}]`（对象数组）；`organizer` 用单值字符串。写错会静默失败或邀请到错误的人。
- **`mark_optional_attendees` 是字符串数组**，不是对象数组 —— 与同一条命令里的 `attendees` 形状相反。
- **`schedules search` 三选一**：`keywords` / `organizer` / `has_attendees` 至少传其一；只传时间范围的搜索是无效调用。
- **只给时间就用 `list`，别把日期塞进 `keywords`** 去 `search`。
- **`schedules list` 窗口限当前时刻前后 30 天**，超出服务端直接不返回（不是报错）。超范围时告知用户重新给一个更短的范围，别自行截断后假装查全了。
- **`free list` 窗口 ≤ 24 小时**，且早于当前时刻的部分被自动截断 —— 查「昨天大家什么时候有空」永远返回空。
- **时间是日程时区下的墙上时间，后台不做转换**：禁止自行把用户给的时间换算成东八区再传。
- **会议室只写 `location` 等于没订**：提到会议室就必须经 `rooms search` 拿 `meeting_room_id` 传入，且订房是 create 的**前置阻塞项**，不能「先建了日程回头补会议室」。
- **上游技能的会议室参数名已过时**：上游 `wecomcli-calendar` 写的是 `room_keyword` / `min_capacity` / `building_city`，CLI 1.2.0 实际是 `room_name` / `capacity_min` / `city_name` / `building_name`。照抄上游会直接调用失败。
- **指定的会议室查无或被占时，必须先告知、禁止静默替换**，哪怕 `recommendations` 只有 1 个候选也要用户确认。
- **`buildings list` 没有 building_id**：下游 `rooms search` 用 `city_name` + `building_name` 引用某栋楼，且这两个值必须逐字取自 `buildings list` 返回，禁止编造。
- **判定会议形态不必补 `get`**：`search` / `list` / `get` 都直接返回 `meeting` 字段。
- **`schedules create` 只返回 `schedule_id`**：想回显完整内容要么用本次入参，要么再调 `get`，别编造返回字段。
- **写操作前的复述确认不可省**：本技能三个写方法全是 write-high，均对外可见或不可逆。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-calendar`。
