---
name: wecom-meeting
description: >-
  企业微信在线会议管理：创建/查询/搜索/更新/取消含会议号与入会链接的在线会议，查看会议详情与参会人，
  读取会议智能纪要与待办，拉取会议逐字转写原文，以及基于纪要或原文做会议总结。
  当用户说「开个视频会议 / 发个入会链接 / 查一下明天的会议 / 搜下项目评审会 / 这个会不开了 /
  改个时间加个人 / 帮我总结下 xx 会 / 这个会讲了啥 / 把会上原话发我 / 看下这个会的待办」时使用。
  只负责『在线会议』——含会议号/入会链接、可远程或视频参会；用户要的是不含会议链接的『日程』（含纯线下碰头）时改用 wecom-calendar。
  用户只说「开会/约个会/xx 会」而未说明是日程还是会议时，创建场景必须先逐字追问这一句、不得改写：
  `需要创建日程还是会议？（请回复：日程 / 会议）`（禁止改成「在线会议/视频会议/线下会议/日程安排」等任何变体）；
  查询场景则严禁追问，日程与会议两边都查再合并。
  不负责：忙闲查询与会议室/办公楼查询（都在 wecom-calendar）、待办事项（wecom-todo）、姓名转 userid（wecom-contact）。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - meeting
  - video-conference
---

# 企业微信在线会议

管理带会议号与入会链接的在线会议：约会、查会、改会、取消，以及会后取纪要、待办和逐字转写。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 已安装、版本达标、`auth show --status` 返回 `authorized`；具体版本门槛以 `wecom-shared` 为准）。
> 未通过前置检查时不得执行本技能任何命令。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 按时间范围列会议 | `wecom-cli meeting list` | read |
| 按关键词搜会议 | `wecom-cli meeting search` | read |
| 批量取会议详情（含参会人、状态、纪要、待办） | `wecom-cli meeting get` | read |
| 拉会议逐字转写原文 | `wecom-cli meeting original get` | read |
| 创建在线会议 | `wecom-cli meeting create` | **write-high** |
| 更新会议（改时间/主题/地点/加减人/换会议室） | `wecom-cli meeting update` | **write-high** |
| 取消会议 | `wecom-cli meeting cancel` | **write-high** |

### 跨技能依赖（本技能没有这些方法，必须反向调用 `wecom-calendar`）

| 需要做的事 | 去哪儿 |
|---|---|
| 查参会人共同空闲 / 某人什么时候有空 | `wecom-calendar` 的 `calendar schedules free list` |
| 查办公楼清单 | `wecom-calendar` 的 `meeting rooms buildings list` |
| 查会议室可订性、拿 `meeting_room_id` | `wecom-calendar` 的 `meeting rooms search`，编排见 `../wecom-calendar/references/meeting-room.md` |
| 查/改不含会议链接的纯日程 | `wecom-calendar` 的 `calendar schedules *` |

> 注意反直觉的归属：`meeting rooms search` 与 `meeting rooms buildings list` 虽然命令前缀是 `meeting`，
> 但**归 `wecom-calendar` 技能**。本技能只在拿到 `meeting_room_id` 后把它传进 `create` / `update`。

### 三个高风险方法的确认要求

> ⚠️ **高风险操作**：`meeting create` 会向全体参会人发出会议邀请、生成入会链接并同时创建对应日程，
> 传 `meeting_room_id` 时还会真实占用会议室。执行前必须向用户复述
> 「将创建会议「<主题>」，时间 <开始>-<结束>，邀请 <人名列表>，会议室 <会议室名>」并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作**：`meeting update` 改时间/参会人/地点会通知全体参会人，被移除的人会直接失去这场会议。
> 执行前必须向用户复述
> 「将把会议「<主题>」的 <改动项> 改为 <新值>，参会人会收到变更通知」并取得明确同意；用户未明确同意时不得执行。

> ⚠️ **高风险操作**：`meeting cancel` 会取消会议、通知全体参会人并作废入会链接，CLI **没有任何恢复接口**。
> 执行前必须向用户复述
> 「将取消会议「<主题>」（<时间>），参会人会收到取消通知，入会链接作废，且无法撤回」并取得明确同意；用户未明确同意时不得执行。

## 日程 vs 会议消歧 [CRITICAL｜措辞逐字固定]

企业微信里「会」有两种载体，判据只有一条：

- **含会议号（`meeting_code`）/ 入会链接（`meeting_link`）的是「会议」** → 归本技能
- **不含会议号与入会链接的是「日程」**（包括纯线下面对面碰头、订了会议室的线下会）→ 归 `wecom-calendar`

判定一条已有记录属于哪边：`wecom-calendar` 的 `schedules list` / `search` / `get` 返回的每条日程都带
`meeting` 字段，读 `meeting.meeting_code` 是否非空即可，**不需要额外补一次 `get`**。

### 规则一：创建场景必须逐字追问

用户只说「开会 / 约个会 / 安排个会 / xx 会 / xx 会议」等而未明确是日程还是会议时，**必须先用文字追问**，问题与选项**逐字固定、不得改写、不得增减、不得翻译**：

```
需要创建日程还是会议？（请回复：日程 / 会议）
```

- 用户答「会议」→ 留在本技能创建会议。
- 用户答「日程」→ 转 `wecom-calendar` 创建日程。
- 「会议」「会」「开会」这些词**本身不构成「明确」**，禁止因 query 里出现「会议」二字就默认创建会议，也禁止反向默认成日程。
- **只给了地点或会议室号**（「在 1605 开会」「订个会议室开会」）**也不构成明确** —— 会议室里同样可能只是纯线下安排，仍须追问。
- 只有出现「入会链接 / 会议号 / 视频会议 / 远程参会 / 外地同事接入」等信号时才直接留在本技能；出现「碰个面 / 创建日程 / 面对面聊」等纯线下信号时直接转 `wecom-calendar`，都无需追问。
- **同时支持线下与远程参会**（「线下开、外地同事远程接入」）含在线会议链接，归本技能；创建会议会自动生成对应日程，**不要**再去 `wecom-calendar` 另建一条日程。

### 规则二：查询场景严禁追问，两边都查再合并

查询场景**严禁**用上面那句话追问（那句话只用于创建）。按两个独立维度处理：

**维度一 —— 查哪一边**

| 用户表述 | 动作 |
|---|---|
| 明确提到「在线会议 / 视频会议 / 入会链接 / 会议号 / 腾讯会议 / 远程参会」 | 只查会议（本技能） |
| 明确说「日程 / 安排 / 我的安排 / 日历」且无在线会议特征 | 只查日程（转 `wecom-calendar`） |
| 模糊表述：「会 / xx 会 / xx 会议 / 开会 / 最近有什么会 / 有哪些会 / 找下 xx 会议」 | **日程和会议两边都查**，再合并 |

即使本技能已经查到结果，模糊表述也**必须**同时用相同时间范围/关键词去 `wecom-calendar` 查日程，
**禁止因为会议侧有结果就跳过日程侧**。反过来，明确指向在线会议时只查会议；**查无结果时兜底去日程查一把**
（命中则说明「这是一条日程，未关联在线会议链接」，两边都无再告知）。

**维度二 —— 每一边用 `search` 还是 `list`（与维度一独立，逐边各判）**

- 有**主题/名称关键词**（「搜一下项目评审会议」）→ 该边用 `search`，关键词进 `keywords`。
- **只有时间/日期或泛浏览**（「最近有什么会」「查一下明天的会议」）→ 该边用 `list`。
  **禁止把日期当 `keywords` 喂给 `search`。**

**合并展示**：按是否含在线会议链接分成「（会议）」与「（日程）」两部分，
同一场按「主题 + 时间」去重只保留一条，末尾汇总「共 N 场，其中会议 X 场、日程 Y 场」。
只有一类时不分部分、不加小标题。

### 规则三：改约禁止拆成 cancel + create

「改约 / 改时间 / 挪到 / 顺延 / 重新约」等改期意图，**即使用户说「取消……再约到……」也算改期**，一律走 `update`：

1. 先 `search` 或 `list` 定位拿 `meeting_id`（或从 `wecom-calendar` 的日程返回里取 `meeting.meeting_id`，此时**无需再 search 一次**）。
2. 用 `meeting update` 改时间。

> **根因**：`calendar schedules create` 只能建纯日程、**重建不出会议链接**（能拆不能合）。
> cancel + create 会让**会议链接永久丢失**，参会人手里的旧链接全部作废。
> 这条禁令没有例外，不得以「用户自己说要先取消」为由绕过。

## 场景：帮我开个会

### 步骤

1. **消歧**（见上文规则一）。确认是「会议」后继续。
2. **补必填参数**：`subject` / `begin_time` 缺失或参会人无法从上下文推断时，用文字询问。
   - `end_time` 缺失**不追问**，默认 `begin_time + 1 小时`。
   - 仅描述参会方式或动作的词（「视频会议」「开个会」「远程接入」）**不构成有效 `subject`**，按缺失处理去问。
   - 询问时间时候选必须是**精确到分钟的具体时刻**，禁止「上午 / 下午 / 下班前」这类模糊选项。
3. **姓名 → userid**：调 `wecom-contact` 解析。多候选时列 2~4 个（姓名 + 部门）让用户选。**禁止**把姓名当 userid 拼接，**禁止**凭记忆编造。
4. **忙闲门禁**：调 `wecom-calendar` 的 `calendar schedules free list`。
   - 查询对象 = **当前用户自己 + 其他内部参会人**（`wo` 前缀）。**自己也必须查**，否则会约到自己已占用的时段。
   - 外部联系人（`wm` 前缀）忙闲不可查，**不纳入查询对象，但不因此跳过整体检查**。
   - 检测到冲突时必须用文字让用户在「坚持这个时间 / 换一个时间」中拍板，**不得自行决定**。
   - 仅当忙闲接口**调用失败**时才降级放行。
5. **会议室门禁**：用户提到会议室时，必须先经 `wecom-calendar` 的会议室查询拿到真实 `meeting_room_id`
   并经用户确认，才能调 `create`。**「提到会议室但 `meeting_room_id` 仍为空」就禁止 create。**
   严禁「先把会议建起来、会议室随后补」。
6. **复述并取得同意**（write-high 确认要求）。
7. **执行创建**，再用返回的 `meeting_id` 调 `meeting get` 拿 `attendees[].name` 回显。

### 命令

```bash
# 最小创建
wecom-cli meeting create \
  --subject '产品评审会' \
  --begin-time '2026-09-01 14:00:00' \
  --end-time '2026-09-01 15:00:00'

# 带参会人 —— attendees 是对象数组
wecom-cli meeting create --json '{
  "subject": "产品评审会",
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "attendees": [{"userid": "woxxxa"}, {"userid": "woxxxb"}],
  "description": "评审 Q4 路线图"
}'

# 带会议室（meeting_room_id 来自 wecom-calendar 的 rooms search）
wecom-cli meeting create --json '{
  "subject": "产品评审会",
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "attendees": [{"userid": "woxxxa"}],
  "meeting_room_id": "mrmxxxx"
}'

# 跨时区会议
wecom-cli meeting create --json '{
  "subject": "全球同步会",
  "begin_time": "2026-09-01 09:00:00",
  "end_time": "2026-09-01 10:00:00",
  "timezone": {"timezone_id": "America/New_York", "timezone_offset": -18000}
}'
```

**创建返回**：`meeting_id` / `meeting_code` / `meeting_link`。
后两个是会议号与入会链接 —— **禁止展示给用户**（见「输出格式」）。

### 创建成功后的回复格式

只输出三行，不加寒暄、不加建议、不展示地点/会议室/会议号/入会链接/`meeting_id`：

```
主题：{subject}
时间：{M月D日} {HH:mm}-{HH:mm}
参会人：{人名1}、{人名2}
```

## 场景：查一下我最近的会

只给时间或泛浏览 → **走 `list`**。

```bash
# 指定时间范围（begin_time 与 end_time 必须同传或同省略）
wecom-cli meeting list --begin-time '2026-09-01 00:00:00' --end-time '2026-09-30 23:59:59'

# 都不传 = 当前时间到 30 天后
wecom-cli meeting list --limit 50
```

- 返回 `created_meetings[]`（我创建的）与 `attended_meetings[]`（我参加的）两个数组，
  以及 `has_more` / `next_cursor`。这两个数组只用来区分展示，**不用于判断能不能取消/更新**。
- 列表条目**不含 `meeting_status`**，也不含参会人姓名 —— 需要这些字段必须再调 `meeting get`。
- 展示流程：拉完所有页 → 按开始时间升序 → **只对要展示的前 10 条**调 `meeting get` 反查
  `attendees[].name`（每批 ≤ 10 个）→ 顺序输出 → 余下计入「还有 N 条」。
- 若本次是模糊查询，按规则二**同时**转 `wecom-calendar` 拉日程 `list` 合并。
- 列表为空时**不要直接说「无会议」**：先去 `wecom-calendar` 用相同条件查日程，
  命中则一并呈现并说明「这是一条日程，未关联在线会议链接」；两边都无再告知并建议扩大时间范围。

## 场景：搜一下项目评审会

有主题关键词 → **走 `search`**。`keywords` 必填。

```bash
wecom-cli meeting search --json '{"keywords": ["项目评审"], "limit": 20}'

# 限定时间范围
wecom-cli meeting search --json '{
  "keywords": ["周会"],
  "begin_time": "2026-08-01 00:00:00",
  "end_time": "2026-09-01 00:00:00",
  "limit": 20
}'

# 组合逻辑：元素之间 OR，元素内空格 AND
wecom-cli meeting search --json '{"keywords": ["周会 项目", "评审"], "limit": 20}'
```

- `keywords` 可匹配会议主题、参会人姓名、会议纪要内容、会议室名称。
- `limit` 最大 20（默认 20）；翻页用 `cursor` 传上次的 `next_cursor`。
- `begin_time` 不传默认 0 值、`end_time` 不传默认 `2999-01-01 00:00:00`，等于全时段搜。
- 返回 `meetings[]`，字段与 `list` 的条目相同（`meeting_id` / `sub_meeting_id` / `subject` /
  `begin_time` / `end_time` / `creator_name` / `attendee_count` / `location` / `meeting_room` / `is_repeat_meeting`）。
- 模糊搜索时按规则二**同时**去 `wecom-calendar` 用同样关键词搜日程再合并。

## 场景：看看这个会的详情和参会人

```bash
# meeting_ids 是对象数组，每项至少含 meeting_id
wecom-cli meeting get --json '{"meeting_ids": [{"meeting_id": "<meeting_id>"}]}'

# 周期会议的某一场：补 sub_meeting_id
wecom-cli meeting get --json '{"meeting_ids": [{"meeting_id": "<meeting_id>", "sub_meeting_id": "<sub_meeting_id>"}]}'

# 也支持用会议 URL 反查
wecom-cli meeting get --json '{"urls": ["<会议链接>"]}'
```

- **`meeting_ids` + `urls` 合计上限 10**，超出必须分批。
- 返回 `meetings[]`，含 `subject` / `begin_time` / `end_time` / `location` / `meeting_room` /
  `description` / `attendees[]`（含 `name`、`is_external`、`is_attended`、`duration`）/
  `meeting_status`（`init` 未开始 / `started` 进行中 / `end` 已结束，终止态不回退）/
  `repeat_rule`（周期会议才返回）/ `has_note_permission` / `notes[]` / `note_url` / `record_url` /
  `current_user_enter_time` / `current_user_quit_time`。

## 场景：帮我总结下 xx 会 / 这个会讲了啥 / 看下这个会的待办

这是对 `meeting get`（现成纪要与待办）与 `meeting original get`（转写原文）两个接口的**编排**，没有新接口。
**纪要与待办同属此逻辑，处理方式一致。**

**唯一分叉维度：本次总结是否带「自定义要求 / 描述」。**

### A. 只说「总结下」，不带任何自定义描述

触发语：「总结下 xx 会」「这个会讲了啥」「纪要发我」「看下这个会的待办」「有哪些待办」。

1. 定位会议（`search` / `list`）→ 调 `meeting get`。
2. 要纪要 → 读 `notes[].note_content`；要待办 → 读 `notes[].todo_content`。
3. **可用则直接返回官方现成内容**（判据：`has_note_permission == true` 且目标字段有实质内容），
   无需再调转写原文接口。
4. **不可用**（目标字段为空 / `has_note_permission == false`）→ 走下方「原文兜底」。

### B. 带了任何自定义要求 / 描述

触发语：「按决策点整理」「用三段式」「列出每人发言重点」「重点讲预算那部分」「写成正式会议纪要」「一句话概括」。

**跳过 `get`，直接 `meeting original get` 拉全部转写**，按用户的要求加工总结。
理由：官方 `notes` 是固定视角的成品，满足不了任何定制诉求，必须回到原文重新加工。

### 原文兜底顺序

凡需要走原文（A 的第 4 步，或 B），一律先调 `meeting original get` 并**翻页到底**，再按结果处理：

- 接口报错（无权限 / 其他）→ 按接口返回如实提示，**不静默失败**。
- 成功但 `original_data` 为空 → 告知「该会议暂无智能纪要，也没有转写原文（可能未开启会议转写、会议未开始或无发言记录）」，**不编造**。
- 成功且有内容 → 按默认或用户指定的结构总结。

## 场景：把会上的原话发我 / 逐字记录

```bash
# 默认不传 media_index → 返回全部段
wecom-cli meeting original get --json '{"meeting_id": "<meeting_id>"}'

# 只要第 3 段（用户说「第 3 段」→ 传 2，从 0 开始）
wecom-cli meeting original get --json '{"meeting_id": "<meeting_id>", "media_index": 2}'

# 翻页
wecom-cli meeting original get --json '{"meeting_id": "<meeting_id>", "cursor": "<next_cursor>", "limit": 500}'

# 周期会议的某一场
wecom-cli meeting original get --json '{"meeting_id": "<meeting_id>", "sub_meeting_id": "<sub_meeting_id>"}'
```

- **转写原文 ≠ 智能纪要**：`original_data`（逐句原始发言）与 `meeting get` 里 AI 总结的 `notes` 是两种内容，
  **禁止用纪要替代转写原文**。
- **`media_index` 默认不传**（不传返回全部段），仅当用户明确要「第 N 段」时才传 `N-1`，**不主动追问要哪一段**。
- `has_more` 为 true 时**必须翻页到底**并按序拼接 `original_data`。
- 用户要「原话 / 逐字记录」时**原样输出**，保留时间戳 + 说话人的逐行格式，**不总结、不改写、不裁剪**；
  只有作为总结素材时才允许加工。
- 会议逐字转写属**隐私高度敏感**内容，只在用户明确索取时拉取，不主动拉、不转发给会议之外的人。

## 场景：改会议 / 加人 / 换会议室

```bash
# 改时间
wecom-cli meeting update --json '{
  "meeting_id": "<meeting_id>",
  "begin_time": "2026-09-02 14:00:00",
  "end_time": "2026-09-02 15:00:00"
}'

# 加人 / 减人（不传的字段保持原状）
wecom-cli meeting update --json '{
  "meeting_id": "<meeting_id>",
  "add_attendees": [{"userid": "woxxxc"}],
  "remove_attendees": [{"userid": "woxxxb"}]
}'

# 换会议室（先经 wecom-calendar 的 rooms search 确认 status=bookable）
wecom-cli meeting update --json '{"meeting_id": "<meeting_id>", "meeting_room_id": "mrmyyyy"}'

# 清空地点 / 备注：传空字符串
wecom-cli meeting update --json '{"meeting_id": "<meeting_id>", "location": "", "description": ""}'
```

- **周期会议（`repeat_rule` 非空）不支持更新**，告知用户并引导到企业微信客户端。
- **只给已有会议加人、不改时间时的忙闲查询**：只针对**新增参会人**、查会议原时段。
  **禁止**把当前用户和已有参会人纳入 —— 他们正被本会议占用、必然显示「忙」，纳入会误报冲突。
- **不预先按「是不是本人创建」拦截**，也不看条目来自 `created_meetings` 还是 `attended_meetings`：
  直接执行，返回权限错误时再告知用户并建议联系发起人。
- 返回更新后的 `subject` / `begin_time` / `end_time` / `location` / `description` / `attendees[]`（含 `name`）。

## 场景：这个会不开了

1. 定位会议拿 `meeting_id`（`search` / `list`，或从 `wecom-calendar` 日程返回的 `meeting.meeting_id` 取）。
2. 判断是真取消还是改期（带「取消」字样也可能是改期，见规则三）。
3. 读 `repeat_rule` —— **周期会议不支持取消**，引导到客户端。
4. 复述并取得同意（write-high 确认要求）。
5. 执行：

```bash
wecom-cli meeting cancel --meeting-id '<meeting_id>'
```

成功返回空对象 `{}`；无权限返回错误 —— 此时告知用户并建议联系发起人。

## 参数速查

> flag 与 JSON 字段一一对应：`--begin-time` ↔ `begin_time`，`--meeting-id` ↔ `meeting_id`，其余同理。
> 嵌套结构（`attendees` / `meeting_ids` / `timezone`）建议直接用 `--json`。完整 schema 用 `--help` 或 `--doc` 查。

| 方法 | 必填 | 关键可选 |
|---|---|---|
| `meeting create` | `subject`（1~255 字节）、`begin_time`、`end_time` | `attendees`（对象数组）、`location`（≤128 字节）、`meeting_room_id`、`description`（≤500 字）、`timezone`、`cal_id`、`mark_optional_attendees`（**字符串数组**） |
| `meeting update` | `meeting_id` | `subject`（≤128）、`begin_time`、`end_time`、`add_attendees` / `remove_attendees`（各 ≤100）、`location`（空串=清空）、`description`（空串=清空，≤5000）、`meeting_room_id` |
| `meeting cancel` | `meeting_id` | — |
| `meeting list` | 无 | `begin_time` / `end_time`（**须同传或同省略**；都不传 = 当前时间到 30 天后）、`limit`（默认 20，上限 100）、`cursor` |
| `meeting search` | `keywords`（字符串数组，≥1） | `begin_time`、`end_time`、`limit`（最大 20）、`cursor`、`bot_source` |
| `meeting get` | 无硬必填，但 `meeting_ids` 与 `urls` **至少传其一**，合计 ≤10 | `meeting_ids[].sub_meeting_id`（周期会议某场） |
| `meeting original get` | 无硬必填，但 `meeting_id` 与 `url` **至少传其一** | `sub_meeting_id`、`media_index`（默认不传=全部段）、`limit`（默认 100，上限 500）、`cursor`、`bot_source` |

**时间格式**统一 `YYYY-MM-DD HH:MM:SS`，且必须先把「明天」「下周三」解析成具体时刻再传。

## 核心概念

- **`meeting_id`**：API 用的会议唯一标识，`mt` 前缀的长字符串。
- **`meeting_code`**：**9 位纯数字**会议号，只给人入会用，**不能当 `meeting_id` 传**。
- **`sub_meeting_id`**：周期会议里某一场的标识。`get` / `original get` 查周期会议某场时需要。
- **周期会议**：`repeat_rule` 非空。`create` / `update` / `cancel` **全不支持**。

## 输出格式

- **禁止展示会议号（`meeting_code`）与入会链接（`meeting_link`）** —— 创建反馈、列表、搜索、详情，任何场景都不展示。
- **姓名原样展示**：用 `attendees[].name`，返回 `zhangsan(张三)` 就展示 `zhangsan(张三)`。`name` 为空时用 `wecom-contact` 反查，**禁止直接展示 userid**。
- **年份**：默认只到月日；跨年时才补 `{YYYY}年M月D日`。
- **相对日期**：昨天/今天/明天在月日前加相对词，如 `时间：明天 9月1日 14:00-15:00`。
- **列表**：禁止 markdown 表格；按开始时间升序，每条独立条目，只含主题/时间/参会人（不含状态标签、参会人数、地点、会议号、入会链接）；超过 10 条只展示前 10 条并告知「还有 N 条，需要查看更多吗？」。
- **单条详情**可多展示 `location`，仍不展示会议号与入会链接。
- **禁止展示**：`meeting_id`、`sub_meeting_id`、`userid`、`meeting_room_id`、`cal_id`、`cursor` / `next_cursor` 等一切内部标识。

## 不支持的事（直接告知，禁止变通绕过）

| 不支持 | 正确做法 |
|---|---|
| 创建 / 更新 / 取消**周期（重复）会议** | 告知不支持，引导到企业微信客户端；禁止用「批量建多场单次会议」「传未公开参数」变通 |
| **RSVP**（接受 / 拒绝 / 待定会议邀请） | 告知不支持，建议在客户端对该邀请操作，或私信发起人 |
| **单场超过 24 小时**的会议 | 直接告知不支持并拒绝；**禁止自行拆成多场**。用户确需多天安排时，由其明确拆分要求后再分别创建 |
| 在本技能里查忙闲 / 查会议室 | 反向调用 `wecom-calendar` |

## 易错点

- **消歧措辞不得改写**：创建场景那句问话必须逐字是 `需要创建日程还是会议？（请回复：日程 / 会议）`，不得改成「线上还是线下」「视频会议还是普通日程」等任何变体。
- **查询场景严禁追问**，模糊表述必须日程 + 会议两边都查再合并 —— 追问本身就是错误，「会议侧已有结果」也不是跳过日程侧的理由。
- **改约禁止 cancel + create**：会议链接不可重建，一旦拆开就永久丢失。
- **9 位数字是 `meeting_code` 不是 `meeting_id`**：把会议号当 `meeting_id` 传是最常见的调用失败原因。`meeting_id` 是 `mt` 前缀长字符串。
- **`meeting_ids` 是对象数组** `[{"meeting_id": "..."}]`，不是字符串数组；而 `attendees` 也是对象数组 `[{"userid": "..."}]`，**不接受** `["woxxx"]` 或 `["张三"]`。同一条命令里 `mark_optional_attendees` 却是**字符串数组**。
- **`meeting get` 上限 10**（`meeting_ids` + `urls` 合计），超出必须分批再合并，别指望服务端截断后还完整。
- **`meeting list` 不返回 `meeting_status`，也不返回参会人姓名**：以为 list 够用而不调 `get`，会导致展示缺参会人。
- **`list` 的 `begin_time` / `end_time` 必须同传或同省略**，只传其一是无效调用。
- **`search` 的 `limit` 最大 20**，`list` 的最大 100 —— 两个方法上限不同，别互相照抄。
- **创建时忙闲必须把自己算进去**，但**给已有会议加人时绝不能把自己和老参会人算进去**（他们必然显示忙）。这两条方向相反，最容易搞反。
- **会议室只写 `location` 等于没订**：必须经 `wecom-calendar` 的 `rooms search` 拿 `meeting_room_id` 传入，且这是 create 的前置阻塞项。
- **`attendees` 上限存在矛盾且未实测**：schema 写 `@maxItems 300`，上游 SKILL.md 写 100。**保守按 100 用**，超过时先与用户确认。
- **时间是会议时区下的墙上时间，后台不做转换**：禁止自行把用户给的时间换算成东八区再传。
- **`meeting original get` 的 `media_index` 从 0 开始**：用户说「第 3 段」要传 `2`；且默认不传就是全部段，不要主动追问。
- **转写原文不可用纪要顶替**，反之亦然；`notes` 为空或 `has_note_permission == false` 时要走原文兜底，而不是编一段。
- **写操作前的复述确认不可省**：本技能三个写方法全是 write-high，均对外可见或不可逆。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-meeting`。
