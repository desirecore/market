# 会议室与办公楼查询 — `meeting rooms buildings list` / `meeting rooms search`

两个方法都是**只读查询**（risk: read），只告诉你「哪间会议室这个时段能订」，**不占用**。
真正的占用发生在下游：`calendar schedules create` / `calendar schedules update` /
`meeting create` / `meeting update` 传入 `meeting_room_id`。

> 本文件是会议室查询的唯一信息源。`wecom-meeting` 技能创建/更新会议要订会议室时，
> **反向调用本文件**（`wecom-meeting` 自身不含 `rooms.*` 方法）。

## 命令

```bash
# 列出我可访问的办公楼（无入参）
wecom-cli meeting rooms buildings list

# 查会议室可订性
wecom-cli meeting rooms search --json '{
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "room_name": "1605",
  "floor_name": "16",
  "capacity_min": 4
}'

# 指定办公楼查（city_name 与 building_name 同传或同省略）
wecom-cli meeting rooms search --json '{
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "city_name": "北京",
  "building_name": "创新大厦A座",
  "capacity_min": 6
}'

# 同城跨楼推荐（仅用户明确要求才加）
wecom-cli meeting rooms search --json '{
  "begin_time": "2026-09-01 14:00:00",
  "end_time": "2026-09-01 15:00:00",
  "expand_to_other_buildings": true
}'
```

> ⚠️ **参数名以 CLI 1.2.0 schema 为准**。上游 `wecomcli-calendar` 的同名文档写的是
> `room_keyword` / `min_capacity` / `building_city`，**这三个名字已经过时**，实际是
> `room_name` / `capacity_min` / `city_name`。照抄上游会直接调用失败。

---

## `meeting rooms buildings list` — 办公楼清单

**无入参**。返回当前用户可访问的办公楼全量列表。

### 返回

| 字段 | 说明 |
|---|---|
| `total_count` | 大楼总数 |
| `buildings[].name` | 大楼名称（不含城市前缀） |
| `buildings[].city` | 城市，展示时拼 `{city} {name}` |
| `buildings[].is_current` | 是否为当前办公大楼；无法判断时全为 `false` |

**没有 `building_id`** —— 下游 `rooms search` 靠 `city_name` + `building_name` 两个字符串引用某栋楼。

### 用法

- **仅当用户提到楼名时才调用**。没提楼就跳过，让 `rooms search` 用当前所在楼兜底。
- 用户口语楼名（「北京创新 A」）与标准名往往写法不同（简称、漏字、少写 A/B 座、带不带城市前缀），
  应做**模糊匹配**，不要求逐字相同：
  - 命中唯一最接近项 → 文字确认一句「你是指【{city} {name}】吗？」，确认后取该条目的 `city` + `name`。
  - 命中多个相近项 → 只列这几个（展示 `{city} {name}`）让用户选。
  - 确实匹配不到 → 让用户补充或自由输入楼名。**禁止从全量列表里随机挑几个充数，禁止编造列表里没有的楼名。**
- 展示给用户的楼名、以及最终喂给 `rooms search` 的 `city_name` / `building_name`，
  **必须逐字取自 `buildings list` 的返回条目**。
- `buildings` 为空数组 → 提示「暂无可预订办公地点」。

---

## `meeting rooms search` — 会议室可订性

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:--:|---|---|
| `begin_time` | string | 是 | — | `YYYY-MM-DD HH:MM:SS`，须晚于当前时刻 |
| `end_time` | string | 是 | — | 晚于 `begin_time` |
| `room_name` | string | 否 | — | 会议室名/号（如 `"1605"`、`"创新室"`）。传了才会有 `target` |
| `building_name` | string | 否 | 当前所在楼 | 与 `city_name` 同传或同省略 |
| `city_name` | string | 否 | 当前所在楼城市 | 同上 |
| `floor_name` | string | 否 | — | 楼层。**直接用用户原始表述**，不做归一化（说「16 楼」就传 `"16 楼"`，说「16F」就传 `"16F"`） |
| `capacity_min` | int | 否 | — | 容量下限，取 `参与人数 + 1`（含组织者） |
| `expand_to_other_buildings` | bool | 否 | `false` | 同城跨楼推荐，**仅用户明确要求才传** |
| `limit` | int | 否 | 20 | 上限 100 |
| `cursor` | string | 否 | — | 分页游标 |

`city_name` / `building_name` 均不传时用当前所在楼兜底。

> 上游文档声明了三个业务错误码（`current_building_unknown` 兜底失败 / `building_not_found` 楼名无匹配 /
> `time_in_past` 起始时间已过），但**这些错误码不在 CLI 的 JSON Schema 里**，属上游声明、未经实测。
> 遇到错误时以 CLI 实际返回的 `error.code` 与 `error.message` 为准，不要硬编码上面三个字符串做分支判断。

### 返回

| 字段 | 说明 |
|---|---|
| `inferred_building.name` / `.city` | 实际查询的办公楼，可展示给用户确认 |
| `inferred_building.source` | 来源标记（如兜底 vs 来自入参） |
| `target[]` | 传了 `room_name` 时为命中项（**可能多间**）；未传时为空数组 |
| `target[].status` | `bookable` / `unavailable` / `not_found` |
| `target[].room` | 房间元数据；`not_found` 时可能为 null |
| `recommendations[]` | 同楼候选，已按「同楼层优先 → 容量恰好够用」排序 |
| `*.meeting_room_id` / `name` / `capacity` / `floor` | 房间字段。**`meeting_room_id` 仅工具链流转，禁止出现在回复正文** |
| `has_more` / `next_cursor` | 分页 |

> `meeting_rooms` / `meeting_rooms_count` 在 schema 里标注为**废弃**字段，不要使用。

### 边界

- `status = unavailable` 时**不返回占用方信息**，不要告诉用户「被谁占了」。
- 同楼无可用时 `recommendations` 为空数组，由你决定是否询问用户开 `expand_to_other_buildings`。
- 抢订竞态（查到 bookable、下单时已被抢）发生在 `create` 阶段，按创建返回的错误处理并重新查一轮。

---

## 编排

```
├─ 用户提了楼名 → buildings list → 模糊匹配 + 确认 → city_name + building_name
│  用户没提楼   → 跳过（rooms search 用当前所在楼兜底）
│
└─ rooms search（begin/end + 可选楼 + 可选 room_name + capacity_min = 参与人数 + 1）
    ├─ 用户指定了具体会议室（传了 room_name）→ 看 target：
    │    ├─ target 中有 status = bookable：
    │    │     ├─ 仅 1 个 → 直接取其 target[].room.meeting_room_id
    │    │     └─ 多个     → 用文字让用户选（禁止自动取第一个）
    │    ├─ target = []（查无此名）→ 先告知「未查到你指定的『xxx』会议室」，
    │    │     再让用户决定改订其他会议室或换时间（候选仅 1 个也须确认）
    │    └─ target 全是 unavailable → 先告知「『xxx』该时段已被占用」，再让用户选替代或换时间
    ├─ 用户未指定具体会议室（target = []）：
    │    ├─ recommendations 多个 → 必须让用户选
    │    └─ recommendations 仅 1 个 → 可直接使用
    └─ recommendations = [] → 问是否跨楼（expand_to_other_buildings = true 重查）或换时间
```

`rooms search` 需要**确定的起止时间**。用户只给了「明天下午」这种范围时，
先用 `calendar schedules free list` 查共同空闲、让用户选定一个具体时段，再拿该时段查会议室。

## 五条硬性规则（下游 create / update 必须遵守）

1. **先查询、后推荐、后创建**：`meeting_room_id` 必须来自本次 `rooms search` 的真实返回值。
   在拿到真实结果之前，**禁止**凭记忆、上下文、历史会话罗列或推荐任何具体会议室
   —— 包括回复正文里提到的会议室名 / 房间号 / 楼层 / 容量。
2. **多个候选必须让用户选**，禁止自动替用户挑。
3. **会议室禁止只写进 `location`**：那样不会真正占用会议室。只要用户提到会议室，
   就必须经 `rooms search` 拿到 `meeting_room_id` 传入。
4. **先订房、后建程/建会**：会议室查询与选择是 create 的**前置阻塞项**，
   不得以「先把会议建起来、会议室随后补」跳过。事后要换会议室可用 `update` 传新 `meeting_room_id` 改订
   （须先经 `rooms search` 确认新会议室 `status = bookable`），不必取消重建。
5. **查无 / 不可用时必须先告知、禁止静默替换**：即使 `recommendations` 只有 1 个候选也要用户确认。
   「仅 1 个可直接用」只适用于用户**未指定**具体会议室的情形。

## 展示约束

- 给用户的候选 **2~4 个**，展示 `name` + 楼层 + 容量。
- **`meeting_room_id` 禁止出现在用户可见的任何文字里**，对用户只说会议室名称。
