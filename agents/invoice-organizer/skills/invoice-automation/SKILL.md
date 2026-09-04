---
name: invoice-automation
description: >-
  发票自动化的两条通道及其正确参数：邮件规则（新发票邮件自动交给本 Agent 增量入账）与
  定时任务（每月自动重建台账并出报告）。含条件/动作取值、prompt 自包含要求、
  无人值守的审批取舍与常见坑。Use when 用户要「以后新发票自动入账」「每月 1 号自动出台账」
  「设个定时」「配个邮件规则」，或已配的自动化没触发需要排查时。
  Also covers mail rules, scheduled jobs and unattended invoice processing.
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - invoice
  - automation
  - schedule
  - mail-rule
metadata:
  category: automation
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 发票自动化
      short_desc: 邮件规则与定时任务的正确参数与常见坑
    en-US:
      name: Invoice Automation
      short_desc: Mail rules and scheduled jobs — correct parameters and known pitfalls
  requires:
    tools:
      - MailOperations
      - ManageSchedule
---

# 发票自动化

## L0

只有两条通道：**邮件规则**（新发票邮件到达时把这封邮件交给本 Agent 增量入账）和 **定时任务**（每月按时重建台账与报告）。

**心跳不能用来做这件事**——心跳执行时只注入 `HeartbeatRespond` 一个工具，读邮件、写文件、解析全都够不着。心跳只能当通知层。

配置任何一条之前先跟用户把「会发生什么、会不会打扰他」讲清楚，他同意了再动手。

## L1

### 通道一 · 邮件规则

新邮件命中条件时，把这封邮件交给本 Agent 处理一轮。

```
MailOperations{
  path: '/api/rules',
  method: 'POST',
  body: {
    name: '发票邮件自动入账',
    description: '带附件且主题或正文含发票关键词的邮件，交给发票整理助手增量入账',
    enabled: true,
    provider: 'gmail',                // 省略 provider + email 则为全局规则
    email: '<用户邮箱>',
    conditionLogic: 'and',
    conditions: [
      { field: 'has_attachment', operator: 'is_true',  value: '' },
      { field: 'subject',        operator: 'contains', value: '发票' }
    ],
    actions: [
      { type: 'agent_handle', value: 'invoice-organizer' }
    ],
    stopOnMatch: false
  }
}
```

**取值只能从下面这些里选，写错的会被静默判为不匹配：**

| 位置 | 合法取值 |
| --- | --- |
| `conditions[].field` | `from` / `to` / `subject` / `body` / `has_attachment` |
| `conditions[].operator` | `contains` / `not_contains` / `equals` / `not_equals` / `starts_with` / `ends_with` / `matches_regex` / `is_true` / `is_false` |
| `conditionLogic` | `and` / `or` |
| `actions[].type` | 见下表 |

正则操作符叫 **`matches_regex`**，不是 `regex`。`is_true` / `is_false` 只用于 `has_attachment`，`value` 传空串。

**动作里有一半是空实现，别教用户用：**

| 动作 | 状态 |
| --- | --- |
| `agent_handle` · `add_label` · `remove_label` · `mark_as_read` · `mark_as_unread` · `auto_reply` · `delete` | 真实现 |
| `move_to_folder` · `forward_to` · `star` · `archive` | **空实现**，只写一行日志，什么都不会发生 |

`delete` 虽然是真实现，但本 Agent 不碰用户的邮件——不要把它写进任何规则。

**一条规则要覆盖多种关键词**，用 `conditionLogic: 'or'` 加多个 `subject`/`body` 条件，或者用一个 `matches_regex`：

```
{ field: 'subject', operator: 'matches_regex', value: '发票|invoice|電子發票|行程单|报销' }
```

（匹配前字段值会被转成小写，中文不受影响。）

**触发后你会收到什么。** 你拿到的是这封邮件的元数据——发件人、主题、时间、邮箱账户、邮件 ID、正文摘要——**没有附件清单**。所以第一件事是回头取详情拿 `attachments[]`，然后按 `invoice-workflow` 的增量模式跑：

| provider | 取详情 |
| --- | --- |
| Gmail | `GET /api/gmail/messages/{mailId}?email=..` |
| Outlook | `GET /api/outlook/message?id={mailId}&email=..` |
| IMAP | `GET /api/imap/messages/{uid}?email=..&folder=..` |

**规则只覆盖收件箱。** 轮询只看 INBOX；发票被自动归到别的文件夹的用户，规则不会触发，要如实告诉他这个限制。

规则的增删查改：`GET /api/rules`（可带 `?provider=..&email=..`）、`PUT /api/rules/{ruleId}`、`DELETE /api/rules/{ruleId}`、`POST /api/rules/{ruleId}/toggle`。配完以后自己 `GET` 一次确认写进去了，把规则 id 告诉用户。

### 通道二 · 定时任务

```
ManageSchedule{
  action: 'create',
  display_name: '每月发票台账',
  trigger_type: 'cron',
  trigger_value: '0 9 1 * *',
  description: '每月 1 号 9:00 重建上月台账并生成月度报告',
  prompt: '<自包含的完整指令，见下>'
}
```

`trigger_type` 取 `delay` / `at` / `interval` / `cron`：`delay` 与 `interval` 用 ISO Duration（`PT30M`、`P1D`），`at` 用带时区的 ISO DateTime，**`cron` 只接受 5 段**（分 时 日 月 周），写 6 段会被拒。

**`prompt` 必须自包含。** 定时任务到期时开的是一个**新会话，不继承当前对话的任何上下文**——它不知道工作目录在哪、不知道台账叫什么、不知道你们刚才聊过什么。prompt 里要写全：

```
加载技能 invoice-workflow 与 invoice-ledger。
工作目录：<绝对路径>/发票
读取 .index/ledger.json，取上一个自然月（按开票日期归属）的记录，
全量重建 台账.xlsx（依赖不可用时改出带 UTF-8 BOM 的 CSV），重建前先备份。
再按 invoice-ledger 的模板写 报告/<上月 YYYY-MM>.md。
完成后用 SendUserMessage 把台账文件和一句话摘要发给用户；
异常项（疑似重复 / 解析失败 / 待复核 / 抬头不符）逐条列在摘要里。
本次不扫描邮箱。
```

最后那句「本次不扫描邮箱」很重要——不写的话每月 1 号会顺带跑一次全量收集，既慢又可能重复打扰。要「先收再出账」就明确写进 prompt。

`create` / `update` / `delete` 一定会弹审批卡。`list` / `get` 不弹。定时任务创建时会固化一份权限快照，之后每次执行都与当时的授权求交——所以**在一个工具齐全的正常会话里创建**它，不要在能力受限的上下文里建。

### 无人值守的代价（必须如实说明）

`MailOperations` / `Write` / `ExportDocument` / `ManageSchedule` / `ManageWorkDirs` 都需要确认。默认的 `ai-approve` 模式下每张卡有 30 秒真人窗口——用户睡着时定时任务会卡在审批上。

想要真正的无人值守，用户需要把本 Agent 的执行审批模式改成 `allow-all`。**这一步必须由用户自己在界面上做**，你只负责讲清楚代价：之后本 Agent 的写文件与邮件调用都不再逐条询问。

另外：「总是允许」按钮对这些工具当前不生效，别让用户点了之后期待下次不弹。

### 建议的默认组合

用户说「以后自动帮我弄」时，默认给这一套，一次说清：

1. 邮件规则：带附件 + 主题/正文含发票关键词 → 交给本 Agent 增量入账（新票当天就进索引和归档）
2. 定时任务：`0 9 1 * *` → 每月 1 号重建上月台账 + 月度报告 + 发给用户
3. 提醒他：想完全不被打扰需要自己把审批模式调成 `allow-all`

不要默认加 `add_label` 或 `mark_as_read`——那会改动用户邮箱的可见状态，要单独问过。

## L2

### 排查：规则配了但没触发

按顺序查，不要跳步：

1. `GET /api/rules` 确认规则真的存在且 `enabled: true`
2. 看 `conditions` 的 `field` / `operator` 拼写——写错的取值不会报错，只会永远不匹配
3. 确认那封邮件在 **INBOX**。规则只跟着收件箱轮询走，别的文件夹要 `POST /api/{p}/messages/fetch?folder=..` 主动补拉，而补拉不会重放规则
4. 用 `POST /api/rules/{ruleId}/test`（body `{provider, email, mailId}`）拿一封已知邮件试跑，看条件到底匹不匹配
5. 确认邮件确实带附件——`has_attachment is_true` 判的是邮件级标志，Gmail 的内联签名图也算附件，所以这个条件比想象中宽

### 排查：定时任务到点没动静

1. `ManageSchedule{action:'list', include_terminal:true}` 看状态。终态（`completed` / `failed` / `cancelled`）默认不显示，不加这个参数会以为任务消失了
2. `ManageSchedule{action:'get', schedule_id:'..'}` 看最近一次执行的结果
3. 卡在审批上是最常见的原因（见上面的「无人值守的代价」）
4. prompt 不自包含也很常见——新会话里 `<工作目录>` 之类的占位没被替换成真实路径，任务跑起来但找不到文件

### 关于 webhook 事件

除了上面那条交办通道，平台还有一条 `agent.json#webhooks` 的事件通道。本 Agent **刻意不预置**它：每个 webhook 事件都要带一份创建者的权限快照，而这份快照只能在用户自己的客户端里生成——市场条目里写一份空快照会让触发时所有工具都被剥掉，Agent 醒来却什么都做不了，比不配还糟。

用户如果自己在 agent.json 里配了 `webhooks.events["mail.received"]`，触发时 payload 的顶层键是 `provider` / `email` / `mailId` / `from` / `fromName` / `subject` / `bodyPreview` / `receivedAt` / `hasAttachments`，在 `prompt_template` 里用 `{{key}}` 引用（只支持顶层键，不支持嵌套路径），并且要把 `max_turns` 显式调大——默认只有 5，而「取详情 → 下附件 → 解析 → 写文件 → 更新索引 → 回执」轻松超过。

### 不要用心跳

工具说明里有一句「监控/巡检/定期检查变化应使用心跳系统」——对本 Agent 不成立。心跳执行时只注入 `HeartbeatRespond`，`MailOperations` / `Read` / `Write` 全都不可达，拿它做发票巡检只会得到一个什么也没做的回合。定期任务一律用 `ManageSchedule`。
