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

状态只写工作目录里的三个索引文件。任何一步中断，重跑都从索引恢复，不会产生第二条记录。

## L1

### 第 1 步 · 接入检查（Preflight）

只在会话里第一次做发票任务时跑一遍，之后复用结论，除非出错。

1. **邮箱**：`MailOperations{path:'/api/accounts-with-settings'}` 拿到全部已接入账户（跨 provider 的唯一一张总表）。一个账户都没有 → 停下，告诉用户先在 DesireCore 的邮箱界面完成一次授权，**不要**去猜端点或试别的路子。
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
| Gmail（已缓存） | `GET /api/gmail/search?email=..&hasAttachment=true&dateFrom=..&dateTo=..` | 本地缓存搜索，不是 Gmail 搜索。`q` 只搜主题与正文，**不搜发件人**，发件人用独立的 `from` 参数 |
| Outlook / IMAP | `GET /api/{outlook,imap}/messages?email=..&offset=..&limit=..&folder=..` | **没有服务端搜索**，只有这三个过滤参数。拉本地缓存后由你自己按主题/发件人/日期过滤 |
| Outlook / IMAP（补拉） | `POST /api/{outlook,imap}/messages/fetch?email=..&folder=..` | 缓存不够新或要拉 INBOX 以外的文件夹时先补拉 |

Gmail 原生查询串的实用写法：

```
has:attachment (发票 OR invoice OR 電子發票 OR 行程单 OR 报销) after:2024/08/01 before:2024/09/01
```

**轮询只覆盖 INBOX。** 用户把发票归到别的文件夹时，必须显式 `POST /api/{p}/messages/fetch?folder=<名字>` 补拉，否则你永远看不到。

**列表项不带附件清单。** 列表返回的是 `{id, subject, from, toRecipients, receivedDateTime, bodyPreview, hasAttachments, labelIds}`——注意字段名是 `toRecipients` / `receivedDateTime` / `bodyPreview` / `labelIds`，不是 `to` / `date` / `snippet` / `labels`。`attachments[]` 只在**详情**里有，所以对每封 `hasAttachments: true` 的邮件要再取一次详情：

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

不带 `save_to` 时附件以 base64 塞进响应，并在 100KB 处被**从中间截断**——发票附件普遍 100KB–2MB，拿到的一定是不可解码的垃圾。带上之后回执直接给绝对路径、字节数和 SHA-256，base64 一个字节都不进上下文。

各 provider 的下载入参：

| provider | path | body |
| --- | --- | --- |
| Gmail | `POST /api/gmail/messages/{messageId}/attachment` | `{email, attachmentId}` |
| Outlook | `POST /api/outlook/attachment` | `{email, messageId, attachmentId}` |
| IMAP | `POST /api/imap/attachment` | `{email, messageId, attachmentId, folder}` |

IMAP 的两个坑：`messageId` 必须是 `"imap:<uid>"` 形式；`attachmentId` 是**数组下标的字符串**（`"0"`、`"1"`），不是文件名。

**过滤掉内联图片。** Gmail 把签名档里的图片也算成附件。按扩展名（保留 `.pdf` / `.ofd` / `.jpg` / `.jpeg` / `.png`）加大小（小于 20KB 的图片基本都是签名档）先筛一遍，省下大量无谓下载。

每封处理完就把邮件 id 写进 `emails.json`；下次遇到同一个 id 直接跳过。

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
3. 两者都缺（行程单、定额发票等）：兜底键 `sellerTaxId + invoiceDate + totalAmount`
4. 文件 `sha256` 完全相同 → 同一个文件被下载了两次，直接跳过

**疑似重复不自动合并。** 发票号码只差一位、其余字段全同 → 记进结果里的 `suspectedDuplicates`，收尾时列给用户，让他判断是「真的开了两张」还是「抄错了一位」。

### 第 5 步 · 归档（Archive）

按开票日期归到 `归档/<年>/<月>/`，文件名固定格式：

```
<YYYYMMDD>_<销售方名称>_<价税合计>_<发票号码>.<原扩展名>
```

例：`20240815_示范酒店管理有限公司_1959.98_24312000000000020002.pdf`

销售方名称里的 `/ \ : * ? " < > |` 替换成 `_`，超过 40 个字符截断。目标已存在且 SHA-256 一致 → 静默跳过；哈希不同 → 保留两份（第二份加 `_2` 后缀）并在收尾里提示用户。

归档完把 `_inbox/` 里的原件删掉（它已经在归档目录里了），解析失败的移到 `_quarantine/` 并写同名 `.reason.txt`。

### 第 6 步 · 台账（Ledger）

加载 `invoice-ledger`。台账**每次全量重建**，数据源是 `.index/ledger.json` 而不是重新解析文件。重建前先把现有台账另存为 `台账.bak.<扩展名>`。

### 第 7 步 · 报告（Report）

加载 `invoice-ledger` 里的报告模板，写 `报告/<YYYY-MM>.md`。用户要 PDF 时用 `ExportDocument` 从这份 Markdown 转。

### 工作目录布局

```
<primary 工作目录>/发票/
├── 台账.xlsx（或 台账.csv）
├── 报告/2024-08.md
├── 归档/2024/08/20240815_示范酒店管理有限公司_1959.98_24312000000000020002.pdf
├── _inbox/                     刚下载、尚未处理
├── _quarantine/                解析失败或判定为非发票（+ 同名 .reason.txt）
└── .index/
    ├── ledger.json             发票主键 → 记录（主索引）
    ├── emails.json             已处理邮件 id
    ├── files.json              文件 sha256 → 解析结果
    └── raw/<sha256>.json       单文件原始解析输出
```

产物必须落在**已登记的工作目录**里。Agent 的 AgentFS 私有目录不在文件工作台的可见范围内，别把台账放那儿。

用 `Write` 落盘，不要用 Bash 重定向——`Write` 会产生「本轮修改了哪些文件」卡片，用户能直接点开台账；Bash 写的文件不会。

### 发票记录字段

**必填**：`invoiceNumber`、`invoiceDate`（`YYYY-MM-DD`）、`sellerName`、`totalAmount`（价税合计）

**选填**：`invoiceCode`、`invoiceType`、`buyerName`、`buyerTaxId`、`sellerTaxId`、`amountExcludingTax`、`taxAmount`、`taxRate`、`items[]`、`checkCode`、`currency`（默认 `CNY`）、`isVoid`

**溯源（必填）**：`sourceEmailId`、`sourceEmailSubject`、`sourceFrom`、`sourceReceivedAt`、`sourceAttachmentName`、`fileSha256`、`archivedPath`、`format`（`pdf`/`ofd`/`image`）、`extractedBy`、`confidence`、`extractedAt`

抽不到的选填字段就留空（`null`），不要用空字符串冒充「有值但为空」，更不要按常见格式补全。

### 幂等与恢复

- 索引文件是唯一事实源。每完成一批就落盘一次，不要攒到最后统一写——中途出错时已完成的部分要能保住。
- 重跑时先读三个索引，只处理索引里没有的邮件 / 文件。
- 归档目录与台账都可以从 `ledger.json` 完整重建；反过来不行。所以**永远不要**只改台账不改索引。
- 状态**不写记忆条目**。记忆检索是关键词打分且有硬 token 预算，几百张发票必然漏检，定时任务路径还根本不带检索 query。记忆条目只放稳定偏好：报销主体抬头、科目映射、月度出账日、某个供应商单独归类。

### 判定：这是不是发票

按顺序，命中即停：

1. 文本层 / OFD 结构化 XML 里**同时**出现带标签的发票号码（`发票号码：` 或 OFD 的 `InvoiceNo`）与 `价税合计` → **是**
2. 只命中票据关键词（`铁路电子客票报销凭证` / `航空运输电子客票行程单` / `定额发票`）→ **是**，按对应子类型处理
3. 出现 `对账单` / `合同` / `报价单` / `账单` 且没有带标签的发票号码 → **否**
4. 没有文本层 → 走视觉识别（见 `invoice-extract`）再回到第 1 条判定
5. 仍不确定 → `_quarantine/`，写清原因，**绝不猜**

第 3 条不能省：对账单正文里会列一整列「关联发票号码」，只按 20 位数字模式匹配一定会误判。判据是**带标签的**发票号码加 `价税合计`。

### 能力边界

- 不做真伪查验（无官方通道）。只做形式校验：必填字段齐全、`金额 + 税额 = 价税合计`、大小写金额一致、开票日期落在范围内。
- 不做记账凭证、不做纳税申报、不做进项抵扣判断。
- 不删除、不移动、不转发用户的邮件。
- 不做汇率换算。外币票按票面原样记，`currency` 单列。
- 收尾只承诺「在给定范围内找到 N 封候选、成功解析 M 张」，不承诺「已全部找到」。

## L2

### 增量模式：只处理一封邮件

邮件规则触发时（见 `invoice-automation`），你拿到的是单封邮件的元数据，没有附件清单。此时跳过第 1 步，从第 2 步的「取详情」开始，只跑这一封，第 6/7 步按需——通常增量只更新 `ledger.json` 与归档，台账等到定时任务或用户主动要求时再重建。

增量处理完给用户一条短消息即可：`已入账：<销售方> ¥<金额>（<发票号码>），归档到 <路径>`。

### 多邮箱

`accounts-with-settings` 返回多个账户时，默认全都扫，收集阶段按账户循环，`emails.json` 的 key 用 `<provider>:<email>:<mailId>` 避免不同账户的 id 撞车。用户明确指定某个邮箱时只扫那个。

### 多工作目录

产物固定放 primary 工作目录。用户有多个工作目录（比如按公司主体分）时，让他明确指定这次整理放哪个，不要自己挑，也不要在多个目录里各存一份。

### 中断恢复

上一轮跑到一半被中止时：`_inbox/` 里会剩下已下载未处理的文件，`emails.json` 里那封邮件已经记过。直接重跑即可——收集阶段会跳过已记邮件，解析阶段会重新处理 `_inbox/` 里的残留。不需要手工清理。

如果 `.index/` 整个丢了但归档目录还在：可以从归档目录重建索引（文件名里就带日期、销售方、金额、发票号码），但溯源字段（来自哪封邮件）无法恢复，重建时把这些字段留空并在报告里注明。
