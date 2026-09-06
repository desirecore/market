---
name: invoice-workflow
description: >-
  发票整理总纲：七步工作流、工作目录布局、状态索引结构、去重主键与幂等判据、能力边界。
  Use when 用户要整理 / 收集 / 归档发票或报销票据（「整理一下上个月的发票」「把邮箱里的发票收一下」
  「这张发票记过了吗」「重新出一遍台账」），或任何发票任务开工前需要确认目录与状态文件位置时。
  Also covers invoice collection, expense receipt intake, VAT invoice archiving and dedupe.
  解析细则见 invoice-extract；台账与报告格式见 invoice-ledger；邮件规则与定时任务见 invoice-automation。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - invoice
  - workflow
  - archive
metadata:
  category: workflow
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 发票整理总纲
      short_desc: 七步工作流、目录布局、状态索引与幂等判据
    en-US:
      name: Invoice Workflow
      short_desc: Seven-step pipeline, directory layout, state index and idempotency rules
  requires:
    tools:
      - MailOperations
      - Read
      - Write
      - FileDigest
---

# 发票整理总纲

## L0

七步，顺序固定，每一步都幂等：**接入检查 → 收集 → 解析 → 去重 → 归档 → 台账 → 报告**。

状态只写工作目录里的三个索引文件。任何一步中断，重跑都从索引恢复，不会重复入账。

单份发票内部的落盘顺序是固定的（`ledger.json` 必须先于删除原件、`emails.json` 必须最后写），
见下面的「单份发票的落盘顺序」——写反了会永久丢记录，且没有任何一次重跑能发现。

## L1

### 第 1 步 · 接入检查（Preflight）

只在会话里第一次做发票任务时跑一遍，之后复用结论，除非出错。

1. **邮箱**：`MailOperations{path:'/api/accounts-with-settings'}` 拿到全部已接入账户（跨 provider 的总表，同时带账户设置；只要账户列表也可用 `/api/accounts`）。一个账户都没有 → 停下，告诉用户先在 DesireCore 的邮箱界面完成一次授权，**不要**去猜端点或试别的路子。
2. **工作目录**：`ManageWorkDirs{action:'list'}`。已安装的 Agent 会自动拿到一个默认工作区，但那个路径用户在文件管理器里几乎找不到。**主动建议用户加一个看得见的目录**：

   ```
   ManageWorkDirs{action:'add', path:'<用户家目录>/Documents/发票', label:'发票'}
   ManageWorkDirs{action:'set_primary', path:'<同上>'}
   ```

   已登记的工作目录会出现在「文件工作台」里，用户能直接点开台账。这一步会弹审批卡，属正常。
3. **报销主体**：问一次用户的报销抬头（购买方名称），记进记忆条目。此后每张票都比对，用于标记「抬头不符」。
4. **解析能力**：不需要额外自检。PDF / OFD / 图片都由 `Read` 直接处理，不需要 Python、不需要安装任何东西。只有生成 `.xlsx` 台账才可能需要额外依赖，见 `invoice-ledger`。

Preflight 的结论用一段话说给用户听：找到几个邮箱、产物会落在哪个目录。

### 第 2 步 · 收集（Intake）

目标：把候选邮件的附件落到 `_inbox/`，并把邮件来源写进 `emails.json`。

**先确定范围**，永远不要在没有范围的情况下全量拉取。范围三要素：时间区间、可选的发件人、可选的关键词。用户说「上个月」时按当前日期换算成明确起止日期，说给他听再开工。

**按 provider 选检索通道**（三家能力差别很大，别用同一套写法）：

| provider | 通道 | 说明 |
| --- | --- | --- |
| Gmail | `POST /api/gmail/messages/fetch?email=..&query=..` | `query` **透传 Gmail 原生搜索语法**，最强的一条通道。带 `pageToken` 游标翻页，`limit` 控制单页条数 |
| Gmail（已缓存） | `GET /api/gmail/search?email=..&hasAttachment=true&dateFrom=..&dateTo=..` | 本地缓存搜索，不是 Gmail 搜索。**`q` 实际只按主题过滤**（见下），发件人用独立的 `from` 参数 |
| Outlook / IMAP | `GET /api/{outlook,imap}/messages?email=..&offset=..&limit=..&folder=..` | **没有服务端搜索**，只有这三个过滤参数。拉本地缓存后由你自己按主题/发件人/日期过滤 |
| Outlook / IMAP（补拉） | `POST /api/{outlook,imap}/messages/fetch?email=..&folder=..` | 缓存不够新或要拉 INBOX 以外的文件夹时先补拉 |

Gmail 原生查询串的实用写法：

```
has:attachment (发票 OR invoice OR 電子發票 OR 行程单 OR 报销) after:2024/08/01 before:2024/09/01
```

**⚠️ 缓存搜索的 `q` 搜不到正文里的关键词。** 实现上 `q` 先在索引层按**主题**筛一遍，之后那次
「正文搜索」只在**已经被主题筛剩下的候选集**上再跑一次——所以**正文命中、主题不命中的邮件永远出不来**。

发票场景里这条最要命：大量开票平台的主题是「您有一份新的电子凭证」「XX 平台通知」「账单已生成」，
「发票」两个字只在正文里。把 `q=发票` 当成搜过正文，就会**静默漏掉这一整批**，而收尾只会说
「在给定范围内找到 N 封候选」，用户根本无从发现少了什么。

要真的覆盖正文关键词：

- **Gmail**：用 `POST /api/gmail/messages/fetch` 的原生 `query`（Gmail 服务端搜索确实搜正文），
  不要用缓存搜索的 `q`
- **Outlook / IMAP**：没有服务端搜索，只能把范围内的邮件拉回本地，自己逐封扫 `bodyPreview` 与
  `body.content`。别指望任何一个查询参数替你做这件事
- 只用主题筛时，**必须在收尾里说明「本次只按主题匹配关键词」**，别让用户以为搜过正文

**轮询范围三家不一样，别一律说「只覆盖收件箱」：**

| provider | 增量轮询实际覆盖 |
| --- | --- |
| Gmail | `history.list(historyTypes:['messageAdded'])`，**不带 label 过滤 → 整个邮箱** |
| Outlook | `/me/messages/delta`，**整个邮箱**（只有 delta 不可用时的降级轮询才只拉 inbox） |
| IMAP | **硬编码 `INBOX`**，其它文件夹一概看不到 |

所以只有 **IMAP** 用户把发票归到别的文件夹时才必须显式
`POST /api/imap/messages/fetch?folder=<名字>` 补拉；Gmail / Outlook 不受这条限制。
补拉本身**不重放规则**（见 `invoice-automation`）。

**列表项的字段，三家不一样。** 三家共有的是
`{id, subject, from, toRecipients, receivedDateTime, bodyPreview, hasAttachments}`——
字段名是 `toRecipients` / `receivedDateTime` / `bodyPreview`，不是 `to` / `date` / `snippet`；
`from` 是**对象** `{name?, address}` 而不是字符串，拼发件人时取 `from.address`。

> **本节的字段说明覆盖市场内置技能 `mail-operations` 里的那一份。** 那份写的是
> `to` / `date` / `snippet` / `labels` / `mimeType`，与本平台的实际返回不一致。
> 两份同时出现在上下文里时，**以这里为准**。

差异在这两处：

| provider | 列表里有没有 `attachments[]` | 标签字段 |
| --- | --- | --- |
| Gmail | **有**（列表内部逐封用 `format:'full'` 重取，附件元数据已经填好） | `labelIds`（**Gmail 专有**，可选字段） |
| IMAP | **有**（列表本来就是逐封拉回源码解析出来的） | 两个都没有 |
| Outlook | **没有**（列表的 `$select` 不含 attachments） | `categories`（不是 `labelIds`） |

所以**只有 Outlook** 需要对每封 `hasAttachments: true` 的邮件再取一次详情；Gmail / IMAP 直接用
列表里的 `attachments[]`，省掉一整轮往返。取详情的端点：

| provider | 详情 |
| --- | --- |
| Gmail | `GET /api/gmail/messages/{id}?email=..` |
| Outlook | `GET /api/outlook/message?id=..&email=..`（注意是单数 `message`，且 id 走查询参数） |
| IMAP | `GET /api/imap/messages/{uid}?email=..&folder=..` |

附件元数据是 `{id, filename, contentType, size}`——是 `contentType`，不是 `mimeType`。

**下载附件必须带 `save_to`：**

```
MailOperations{
  path: '/api/gmail/messages/<messageId>/attachment',
  method: 'POST',
  body: { email: '<账户>', attachmentId: '<附件 id>' },
  save_to: '<工作目录>/发票/_inbox/<原文件名>'
}
```

不带 `save_to` 时**工具会直接拒绝这次调用**并给出可操作的错误（大意：响应含大块 base64，
请用同样的 path/method/body 加上 `save_to` 重来）——不是截断、不是降级，是一次白跑。判据是
「路径命中三个附件端点之一 + 响应 2xx + `result.data` 超过 4096 字符」，发票附件普遍 100KB–2MB，
必然命中。带上 `save_to` 之后回执直接给绝对路径、字节数和 SHA-256，base64 一个字节都不进上下文。

各 provider 的下载入参：

| provider | path | body |
| --- | --- | --- |
| Gmail | `POST /api/gmail/messages/{messageId}/attachment` | `{email, attachmentId}` |
| Outlook | `POST /api/outlook/attachment` | `{email, messageId, attachmentId}` |
| IMAP | `POST /api/imap/attachment` | `{email, messageId, attachmentId, folder}` |

IMAP 的两个坑：`messageId` 用 `"imap:<uid>"` 形式（列表返回的 `id` 就长这样，直接抄）——
服务端做的是 `parseInt(messageId.replace('imap:',''), 10)`，裸 UID 其实也接受，但**别自己拼**，
用列表给的原值最省事；`attachmentId` 是**数组下标的字符串**（`"0"`、`"1"`），不是文件名。

**过滤掉内联图片。** Gmail 把签名档里的图片也算成附件。按扩展名（保留 `.pdf` / `.ofd` / `.jpg` / `.jpeg` / `.png`）加大小（小于 20KB 的图片基本都是签名档）先筛一遍，省下大量无谓下载。

**邮件 id 不在这一步写。** `emails.json` 一旦记下某个 id，收集阶段就永远跳过这封邮件——
所以它必须等到**这封邮件的发票记录已经落进 `ledger.json`** 之后才写，见下面的「单份发票的落盘顺序」
第 8 步。在下载完就写，中间任何一次崩溃都会让这封邮件的票永久失踪。

### 第 3 步 · 解析（Extract）

对 `_inbox/` 里每个文件：

1. `FileDigest{paths:[...]}` 取 SHA-256（一次可以传最多 100 个路径，批量算比逐个快得多）
2. 哈希命中 `.index/files.json` → 直接复用上次结果，**不重复解析**
3. 未命中 → 加载 `invoice-extract` 技能，按里面的规则解析，把原始解析输出写到 `.index/raw/<sha256>.json`，并把 `<sha256> → 记录` 写进 `files.json`

解析结果必须包含 `extractedBy`（`ofd-xml` / `text-layer` / `vision`）与 `confidence`（0–1）。

### 第 4 步 · 去重（Dedupe）

**去重主键，按优先级：**

1. 数电票：`invoiceNumber`（20 位，本身唯一）
2. 旧版票：`invoiceCode + invoiceNumber`
3. 票面没有 `发票号码：` 标签、但有等价的唯一编号（铁路旧版报销凭证的 21 位电子客票号、
   航空行程单的电子客票号码）：按 `invoice-extract` 的约定把它填进 `invoiceNumber`，走第 1 条
4. 确实找不到任何唯一编号（少数手写票、部分定额票）：兜底键
   `sellerTaxId + invoiceDate + totalAmount`。此时 `invoiceNumber` 留空，**不隔离**，
   但整条记录 `confidence` 上限 0.7 并标「待复核」——兜底键撞车的概率远高于发票号码，
   同一天、同一家、同一金额的两张真票会被它误判成一张
5. 文件 `sha256` 完全相同 → 同一个文件被下载了两次，直接跳过

**疑似重复不自动合并。** 发票号码只差一位、其余字段全同 → 记进结果里的 `suspectedDuplicates`，收尾时列给用户，让他判断是「真的开了两张」还是「抄错了一位」。

### 第 5 步 · 归档（Archive）

按开票日期归到 `归档/<年>/<月>/`，文件名固定格式：

```
归档/<YYYY>/<MM>/<YYYYMMDD>_<销售方名称>_<价税合计>_<发票号码>.<原扩展名>
```

例：`归档/2024/08/20240815_示范酒店管理有限公司_1959.98_24312000000000020002.pdf`

**这条路径是死的，不许「优化」。** 写盘前逐项对照，四项全中才允许写：

1. 第一层必须是 `归档/`——不是工作目录根，也不是 `archive/` / `已归档/`
2. 年、月两层之后**直接放文件**——不要再插一层 `<发票类型>/`（类型已经在台账的「发票类型」列里，
   再切一层目录只会让「2024 年 8 月一共几张」需要跨目录数）
3. 日期是 `YYYYMMDD` **八位连写**，不是 `YYYY-MM-DD`——文件名按字典序排就是按日期排，
   加了横杠仍然对，但与台账、报告、`.index` 里的其它日期写法不一致，也和这里的例子对不上
4. 最后一段是**发票号码**；旧版票的发票代码写在号码前面用 `-` 连接（`011002100311-08811701`），
   数电票没有代码就只有号码

实测踩过：同样是空目录起步，有一轮把七张票归成了
`<工作目录>/2022/11/增值税电子普通发票/2022-11-18_….pdf`——三条同时违反。
四条都对照一遍再写，不要凭印象。

销售方名称里的 `/ \ : * ? " < > |` 替换成 `_`，超过 40 个字符截断。目标已存在且 SHA-256 一致 → 静默跳过；哈希不同 → 保留两份（第二份加 `_2` 后缀）并在收尾里提示用户。

归档是**复制**，不是移动：复制到一半崩溃时 `_inbox/` 里的原件还在，重跑能接上。
只有在 `ledger.json` 里这条记录的 `archivedPath` 已经回填并落盘之后，才允许删掉 `_inbox/` 里的原件
（顺序见下面的「单份发票的落盘顺序」）。解析失败的移到 `_quarantine/` 并写同名 `.reason.txt`。

### 第 6 步 · 台账（Ledger）

加载 `invoice-ledger`。台账**每次全量重建**，数据源是 `.index/ledger.json` 而不是重新解析文件。重建前先把现有台账另存为 `台账.bak.<扩展名>`。

### 第 7 步 · 报告（Report）

加载 `invoice-ledger` 里的报告模板。**文件名按本次整理覆盖的开票月份数决定，不许自己另起一套**：

判据是**本次入账的发票，其开票月份落在几个不同的 `YYYY-MM` 里**——不是用户给的
时间范围有多长。「整理 8 月 1 到 15 日」只要票都开在 2024-08，就是单月；
「整理最近两个月」若恰好只有 9 月的票入账，同样是单月。

| 本次入账发票的开票月份 | 文件名 | 例 |
| --- | --- | --- |
| 全部落在同一个 `YYYY-MM` | `报告/<YYYY-MM>.md` | `报告/2024-08.md` |
| 分布在两个及以上 `YYYY-MM` | `报告/<最早 YYYY-MM>_<最晚 YYYY-MM>.md` | `报告/2020-08_2024-09.md` |

月份按**开票日期**归属（与台账同口径），不按收件日期，更不按今天的日期。

**不要用「整理报告-<今天>.md」这类以运行日期命名的文件。** 定时任务每月重建的是
`报告/<上月 YYYY-MM>.md`（见 `invoice-automation`）；一旦手工整理写出按运行日期命名的报告，
两套命名永远不会互相覆盖，用户目录里会攒下一堆内容重叠、谁也不知道哪份是最新的报告。

同一文件名重复生成时**直接覆盖**（报告是从 `.index/ledger.json` 全量重建的派生产物，
不像台账那样需要先备份）。用户要 PDF 时用 `ExportDocument` 从这份 Markdown 转。

### 工作目录布局

```
<primary 工作目录>/发票/
├── 台账.xlsx（或 台账.csv）
├── 报告/2024-08.md             票都开在同一月；跨月时是 报告/2020-08_2024-09.md
├── 归档/2024/08/20240815_示范酒店管理有限公司_1959.98_24312000000000020002.pdf
├── _inbox/                     刚下载、尚未处理
├── _quarantine/                解析失败或判定为非发票（+ 同名 .reason.txt）
└── .index/
    ├── ledger.json             发票主键 → 记录（主索引）
    ├── emails.json             已处理邮件 id
    ├── files.json              文件 sha256 → 解析结果
    └── raw/<sha256>.json       单文件原始解析输出
```

### 三个索引文件的顶层结构（硬规则，不许自己另起一套）

**新建**时必须是下面这个形状。容器键名与嵌套形态都钉死——台账、报告、幂等判据全部从这里
派生，键名一漂，跨轮次和外部工具就都对不上：

```jsonc
// .index/ledger.json —— 发票主键 → 记录（是**字典**，不是数组）
{ "schemaVersion": 1, "updatedAt": "<ISO8601>",
  "invoices": { "<发票主键>": { /* 单张发票的记录 */ } },
  "suspectedDuplicates": [ /* 疑似重复，交人工确认，不并入 invoices */ ],
  "quarantined": [ /* 隔离项摘要，与 _quarantine/ 里的 .reason.txt 对应 */ ] }

// .index/files.json —— 文件 sha256 → 解析结果
{ "schemaVersion": 1, "updatedAt": "<ISO8601>",
  "files": { "<sha256>": { /* 该文件的解析结果与去向 */ } } }

// .index/emails.json —— 已处理邮件 id
{ "schemaVersion": 1, "updatedAt": "<ISO8601>",
  "emails": { "<provider>:<email>:<mailId 原值>": { /* 处理结论 */ } } }
// mailId 一律用列表接口返回的 id **原值**，不做任何清洗。IMAP 的 id 本身就带
// "imap:" 前缀，所以它的 key 长这样（前缀出现两次是对的，别"修正"）：
//   "imap:me@example.com:imap:123"
//   "gmail:me@example.com:18f2c9a1b7e4"
```

**读到旧形态时不要重写容器。** 历史目录里 `ledger.json` 可能是
`{schemaVersion, updatedAt, records: [ … ]}`（**数组**）。这种目录要**原样读、原样写回**，
只增改里面的条目——不要顺手"规范化"成 `invoices`。理由：容器一换，本轮之外的字段
（旧版写过、当前规格没覆盖的）就会静默丢掉，而用户毫无察觉。判据很简单：
**顶层出现 `records` 就一路沿用 `records`，出现 `invoices` 就用 `invoices`，新建才用 `invoices`。**

实测踩过：同一个 Agent 在不同轮次分别产出过这两种不兼容结构，`updatedAt` 也时有时无。

产物必须落在**已登记的工作目录**里。Agent 的 AgentFS 私有目录不在文件工作台的可见范围内，别把台账放那儿。

用 `Write` 落盘，不要用 Bash 重定向——`Write` 会产生「本轮修改了哪些文件」卡片，用户能直接点开台账；Bash 写的文件不会。

### 单份发票的落盘顺序（硬规则，不许调换）

`ledger.json` 是唯一事实源——但这句话只有在**它先于任何删除动作落盘**时才成立。
每份文件固定按这个顺序走，每一步都各自落盘一次：

```
1. 解析                                  ← 此时还没有任何持久化
2. 写 .index/raw/<sha256>.json           ← 原始解析输出
3. 写 .index/files.json                  ← sha256 → 解析结果
4. 写 .index/ledger.json                 ← 记录入账，archivedPath 先留空占位
5. 复制到 归档/<年>/<月>/<规范文件名>      ← 复制，不是移动
6. 回填 ledger.json 的 archivedPath       ← 再落盘一次
7. 删除 _inbox/ 里的原件                  ← 到这一步才允许删
8. 写 emails.json 里这封邮件的 id          ← 这封邮件的 ledger 记录已落盘才写
```

两条次序写反了会**永久丢记录**，而且没有任何一次重跑能发现：

- **第 4 步必须早于第 7 步。** 「归档完了、原件删了、ledger 还没写」的窗口里崩溃 → 文件孤零零躺在
  `归档/2024/08/` 里，`_inbox/` 是空的，`ledger.json` 里没有它，之后每一次重跑都不会再看它一眼。
- **第 8 步必须晚于第 4 步。** 邮件 id 一进 `emails.json`，收集阶段就永远跳过这封邮件；此时若
  ledger 里还没有对应记录，这张票就再也没有第二次入账的机会。

一封邮件里有多个附件时，逐个附件走完 1–7，全部走完才走第 8 步。

### 发票记录字段

**必填**：`invoiceDate`（`YYYY-MM-DD`）、`sellerName`、`totalAmount`（价税合计），
外加**一个唯一票据编号**——优先 `invoiceNumber`；没有 `发票号码：` 标签的票种按 `invoice-extract`
的约定取替代编号填进 `invoiceNumber`（铁路旧版报销凭证取 21 位电子客票号、航空行程单取电子客票号码）。
三者齐全但确实找不到任何唯一编号时，按去重主键第 4 条走兜底键入账并标「待复核」，
**不因为「没有发票号码」就隔离**——隔离的判据是「日期 / 销售方 / 价税合计里有抽不到的」。

**选填**：`invoiceCode`、`invoiceType`、`buyerName`、`buyerTaxId`、`sellerTaxId`、`amountExcludingTax`、`taxAmount`、`taxRate`、`items[]`、`checkCode`、`currency`（默认 `CNY`）、`isVoid`

**溯源（必填）**：`sourceEmailId`、`sourceEmailSubject`、`sourceFrom`、`sourceReceivedAt`、`sourceAttachmentName`、`fileSha256`、`archivedPath`、`format`（`pdf`/`ofd`/`image`）、`extractedBy`、`confidence`、`extractedAt`

抽不到的选填字段就留空（`null`），不要用空字符串冒充「有值但为空」，更不要按常见格式补全。

### 幂等与恢复

- 索引文件是唯一事实源。每完成一批就落盘一次，不要攒到最后统一写——中途出错时已完成的部分要能保住。
- 重跑时先读三个索引，只处理索引里没有的邮件 / 文件。
- 台账可以从 `ledger.json` 完整重建。反方向只能**部分**重建：归档目录能还原发票主体字段
  （文件名里就带日期、销售方、价税合计、发票号码），但溯源字段（来自哪封邮件）恢复不了。
  所以**永远不要**只改台账不改索引，也不要把归档目录当成 ledger 的等价备份。
- 状态**不写记忆条目**。记忆检索是关键词打分且有硬 token 预算，几百张发票必然漏检，定时任务路径还根本不带检索 query。记忆条目只放稳定偏好：报销主体抬头、科目映射、月度出账日、某个供应商单独归类。

### 判定：这是不是发票

按顺序，命中即停：

1. 文本层 / OFD 结构化数据里**同时**出现带标签的发票号码（`发票号码：` 或 OFD 的 `InvoiceNo`）
   与**一个合计项**——`价税合计` 或 `合计金额` 或（`金额` 与 `税额` 成对出现）→ **是**
2. 只命中票据关键词（`铁路电子客票报销凭证` / `航空运输电子客票行程单` / `定额发票` /
   `出租车` / `网约车` / `通行费` / `客运`）→ **是**，按对应子类型处理
3. 出现 `对账单` / `合同` / `报价单` / `账单` 且没有带标签的发票号码 → **否**
4. 没有文本层，**或文本层抽出的内容不足以判定**（乱码、字序错乱、只剩零星几个字）→
   走视觉识别（见 `invoice-extract`），拿到视觉结果再回到第 1 条判定
5. 仍不确定 → `_quarantine/`，写清原因，**绝不猜**

第 1 条的合计项**不能只认 `价税合计` 四个字**：卷式与机打的出租车票、通行费票、部分定额票
票面上只写「金额」「合计」，从来不出现「价税合计」（**现在主流的网约车发票不在此列**，那是标准数电票，
带完整的价税合计）。只认那一种写法，这批纸质票会一条条掉到第 5 条被隔离，而对外文案承诺支持它们。

第 4 条**不能只挂在「没有文本层」上**：现实里大量扫描件带着一层劣质 OCR 文字，`Read` 认为这页有文字
就不会自动渲染成图，于是永远走不到视觉路径。判据是「抽出来的内容够不够判定」，不是「有没有文字层」。

第 3 条不能省：对账单正文里会列一整列「关联发票号码」，只按 20 位数字模式匹配一定会误判。
判据是**带标签的**发票号码加上一个合计项。

### 能力边界

- 不做真伪查验（无官方通道）。只做形式校验：必填字段齐全、`金额 + 税额 = 价税合计`、大小写金额一致、开票日期落在范围内。
- 不做记账凭证、不做纳税申报、不做进项抵扣判断。
- 不删除、不移动、不转发用户的邮件。
- 不做汇率换算。外币结算票的票面仍以人民币计价，`currency` 记 `CNY`，原币金额与汇率照抄进备注。
- 收尾只承诺「在给定范围内找到 N 封候选、成功解析 M 张」，不承诺「已全部找到」。

## L2

### 增量模式：只处理一封邮件

邮件规则触发时（见 `invoice-automation`），你拿到的是单封邮件的元数据，没有附件清单。此时跳过第 1 步，从第 2 步的「取详情」开始，只跑这一封，第 6/7 步按需——通常增量只更新 `ledger.json` 与归档，台账等到定时任务或用户主动要求时再重建。

增量处理完给用户一条短消息即可：`已入账：<销售方> ¥<金额>（<发票号码>），归档到 <路径>`。

### 多邮箱

`accounts-with-settings` 返回多个账户时，默认全都扫，收集阶段按账户循环，`emails.json` 的 key 用 `<provider>:<email>:<mailId 原值>` 避免不同账户的 id 撞车。**`mailId` 用列表接口返回的 id 原值，一个字符都不改**——IMAP 的 id 自带 `imap:` 前缀，拼出来就是 `imap:me@example.com:imap:123`，前缀出现两次是对的。如果这一轮抄原值、下一轮又把前缀剥掉，同一封邮件会产生两个 key，「已处理」判定直接失效、邮件被重复入账。用户明确指定某个邮箱时只扫那个。

### 多工作目录

产物固定放 primary 工作目录。用户有多个工作目录（比如按公司主体分）时，让他明确指定这次整理放哪个，不要自己挑，也不要在多个目录里各存一份。

### 中断恢复

上一轮跑到一半被中止时，下面三条**每次整理都各扫一遍**，不要等用户报错才查：

1. **`_inbox/` 残留**：里面是已下载、未解析或解析到一半的文件。直接重跑即可——收集阶段跳过
   `emails.json` 里已记的邮件，解析阶段把残留重新走一遍「单份发票的落盘顺序」。
2. **归档目录反查**：遍历 `归档/**`，把**不在 `ledger.json` 里**的文件挑出来重新入账。
   这是「落盘顺序」第 4–7 步之间崩溃时唯一的出路——那种文件既不在 `_inbox/`、又不在索引里，
   不主动扫就永远没人发现。文件名里带着开票日期、销售方、价税合计、发票号码，`FileDigest`
   再算一次 sha256 就能补齐 `fileSha256` 与 `archivedPath`；溯源字段恢复不了，留空并在收尾里注明。
3. **`ledger.json` 里 `archivedPath` 为空的记录**（第 4 步落了盘、第 5/6 步没走完）：按
   `fileSha256` 去 `_inbox/` 和归档目录找回文件，找到就补 `archivedPath`，找不到就在异常表里
   列成「已入账但原件丢失」。

如果 `.index/` 整个丢了但归档目录还在：整份索引按第 2 条的办法从归档目录重建，同样只能恢复
票面字段，溯源字段留空并在报告里注明。
