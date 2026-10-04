<!-- locale: zh-CN -->

# mail-operations 技能

## L0：一句话摘要

通过本地 REST API 收发邮件、搜索、标签管理和自动规则，支持 Gmail / Outlook / IMAP。

## L1：概述与使用场景

### 能力描述

mail-operations 是一个**流程型技能（Procedural Skill）**，通过 DesireCore 本地 REST API（由内置工具 `MailOperations` 调用）操作邮件系统。支持 Gmail（OAuth2）、Outlook（MSAL）和 IMAP/SMTP（QQ、163、Yahoo 等）三种邮箱类型，涵盖收发邮件、搜索、标签管理、附件下载、草稿管理和自动规则。

### 使用场景

- 用户需要查看收件箱、发送或回复邮件
- 用户需要搜索特定邮件或管理邮件标签/分类
- 用户需要下载附件或管理草稿
- 用户需要设置自动回复规则或触发智能体处理邮件

### 核心价值

- **统一接口**：三种邮箱通过统一 API 操作，降低使用复杂度
- **本地安全**：所有操作通过本地 API 完成，无需暴露凭证
- **智能联动**：支持自动规则和智能体邮件处理

## L2：详细规范

## 如何进入邮箱服务

用户可通过以下路径进入邮箱管理界面：

1. 点击左侧导航栏的第三个图标（文件夹图标）进入**资源管理器**
2. 在资源管理器首页找到**「邮箱」**卡片，点击进入邮箱管理

> 如果用户不知道如何打开邮箱页面，引导他们按上述步骤操作即可。也可以在对话界面右上角点击「打开资源管理器」快捷入口，再选择邮箱卡片。

---

## API 基础信息

- **调用方式**：使用内置工具 `MailOperations`，参数为 `path`（以 `/api/` 开头的相对路径，查询参数直接拼在 path 里）、`method`（默认 `GET`）、`body`（JSON 对象）和 `save_to`（仅下载附件时使用，见第 6 节）。工具自动定位本机 Mail Service 并携带访问凭证，Agent 不需要、也不能自行提供 token。
- **路径写法**：下文端点均省略 `/api` 前缀，调用时要补上，例如 `/imap/messages?email=me%40example.com&limit=20` 对应 `path: "/api/imap/messages?email=me%40example.com&limit=20"`。唯一例外是健康检查 `/ping`（不带 `/api`）。
- **不要直连端口**：不要用 `curl` 访问 `https://127.0.0.1:62000`。端口从 62000 起动态分配（同时运行多个 DesireCore 实例时，62000 可能属于另一个实例），严格能力模式下不带凭证的直连请求一律返回 401。
- **参数位置**：GET / DELETE 的参数全部放查询串；POST / PUT 按下文表格区分查询串与 body。`messages/fetch`、标记已读/未读、Outlook 单封操作、IMAP 草稿发送等端点的 `email` 必须放在查询串，放进 body 会返回 400 `Missing email parameter`。`/sync` 的 `provider` 与 `email` 都必须放查询串：`provider` 放进 body 返回 400 `Invalid provider`，只有 `email` 放进 body 则不会报参数错误，但同步不会生效。
- **Content-Type**: `application/json`（传 `body` 时工具自动设置）
- **响应格式**: 成功 `{"code": 1, "msg": "Success", "result": ...}`，失败 `{"code": 0, "msg": "错误信息"}`，部分错误另带稳定错误码字段 `error`（如 `smtp_unverified`）

---

## 强制行为规则

以下规则优先级最高，每次操作必须遵守。

### 规则 1：只能通过 MailOperations 工具操作

所有邮件操作**必须且只能**通过内置工具 `MailOperations` 调用本机 Mail Service 完成。**禁止**调用外部邮件客户端或浏览器，也不要用 `curl` / `HttpRequest` 直连本机端口（`MailOperations` 错误提示中明确给出的大附件流式落盘办法除外）。

如果返回 **401**，先按 `msg` 区分原因：
1. Gmail / Outlook 返回 `Not authorized` 或 `Authorization expired`：告知用户该账户授权已失效，引导用户在 DesireCore 邮箱页面重新授权。如需代为发起，调用 Gmail `POST /api/gmail/auth/initiate?loginHint={email}` 或 Outlook `POST /api/outlook/auth/initiate`，把返回的 `result.authUrl` 交给用户在浏览器中打开（服务不会自动打开浏览器）
2. IMAP 返回 `Account not configured`：账户未配置或配置已损坏，与授权过期无关，需要用户重新添加账户（先 `/imap/test`，再 `/imap/accounts`）
3. 返回 `error: "unauthorized"`（缺少或无效的 Mail Service capability）：说明请求没有经过 `MailOperations`，改用该工具重试

### 规则 2：操作前先确认账户

执行任何操作前，**必须先调用 `GET /api/accounts`** 获取账户列表：
- 按邮箱地址或域名匹配用户指定的账户（"QQ 邮箱"→ imap 中 `qq.com`）
- 仅有一个账户且用户说"我的邮箱"→ 直接使用
- 找不到匹配账户 → 告知用户并提示添加

### 规则 3：查询为空时自动同步

查询返回空列表或找不到指定数据时：
1. 调用 `POST /{provider}/messages/fetch?email={email}` 同步远程数据（`email` 放查询串）
2. **自动重试**原查询
3. 仍为空才告知用户

### 规则 4：写操作后提示刷新

发送、回复、删除、标记、标签变更等写操作成功后，提示：`操作已完成。需要我帮你刷新当前邮箱页面以查看最新状态吗？`

---

## 三种邮箱的差异速查

| 功能 | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| 授权 | OAuth2 | OAuth2 (MSAL) | 密码/授权码 |
| Provider 路径 | `/gmail/` | `/outlook/` | `/imap/` |
| 邮件详情 | 路径参数 `/{id}` | 查询参数 `?id={id}` | 路径参数 `/{uid}`（列表返回的 `imap:<uid>` 或纯数字 UID）+ `?folder=` |
| 搜索（本地缓存） | 支持 | 支持 | 支持 |
| 远程同步翻页 | `pageToken`（不支持 `offset`） | `skip` / `offset` | `offset` |
| 草稿 | 支持（含列表/详情） | 支持（创建/更新/删除/发送） | 支持（创建/更新/删除/发送） |
| 附件下载 | 支持 | 支持 | 支持 |
| 标签/分类 | 原生标签 | Categories | 仅本地标签 |
| 发信前提 | 已授权 | 已授权 | SMTP 已验证（`smtpStatus: verified`） |
| 自动规则 | 支持 | 支持 | 支持 |

---

## 核心操作

以下 `{p}` 代表 provider（`gmail`、`outlook`、`imap`），`{email}` 需 URL 编码（`@` → `%40`，`+` → `%2B`）。

### 1. 账户管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取所有账户 | GET | `/accounts` |
| 获取账户含设置 | GET | `/accounts-with-settings` |
| 删除账户 | DELETE | `/accounts/{p}/{email}` |
| 获取账户设置 | GET | `/accounts/{p}/{email}/settings` |
| 更新账户设置 | PUT | `/accounts/{p}/{email}/settings` |
| 更新显示名称 | PUT | `/accounts/{p}/{email}/displayName` — body: `{"displayName": "..."}` |

**IMAP 专属**：

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取预设邮箱配置 | GET | `/imap/presets` — 返回 QQ/163/Yahoo 等服务器配置 |
| 测试 IMAP 连接 | POST | `/imap/test` — body: `{email, password, imap?: {host, port, secure}, smtp?: {host, port, secure}}`；域名在预设中时 `imap` / `smtp` 可省略。**连接失败也返回 HTTP 200**，须检查 `result.imap.success` 与 `result.smtp.success` |
| 添加 IMAP 账户 | POST | `/imap/accounts` — body 同上，另可加 `displayName`、`allowUnverifiedSmtp`；成功返回 201 与 `{email, smtpStatus, smtp}`。SMTP 测试失败时默认返回 400（`error: smtp_verification_failed`），只有用户同意「仅收信」时才传 `allowUnverifiedSmtp: true` |
| 重新验证 SMTP | POST | `/imap/accounts/verify-smtp` — body: `{email}`；验证失败也返回 200，要看 `result.smtp.success` 与 `result.smtpStatus`：通过时 `smtpStatus` 恢复为 `verified`，失败时需要用户更新授权码后再验证 |

### 2. 邮件列表与同步

| 操作 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 查询本地缓存 | GET | `/{p}/messages` | 查询串：`email, offset, limit, folder`；返回 `{messages, total, offset, limit}` |
| 远程同步 | POST | `/{p}/messages/fetch?email=` | `email` 必须放查询串；body（或查询串）：`folder`、`limit`（1–1000，默认 20）；翻页：IMAP `offset`、Outlook `skip` / `offset`、Gmail `pageToken`（Gmail 传 `offset` 返回 400）；返回 `messages` 与分页信息 `pagination` |
| 手动触发同步 | POST | `/sync?provider=&email=` | 参数放查询串；**仅支持 gmail / outlook**，IMAP 返回 400，请改用 `messages/fetch` |

**IMAP 远程同步较慢**：每封邮件都要下载并解析完整内容（实测约 0.65 封/秒），单批 `limit` 建议不超过 100；更早的邮件用 `offset`（跳过最新的多少封）分批拉取。

**folder 取值**：
- 本地缓存列表与搜索：`inbox, sent, drafts, trash, spam, archive, other`，大小写不敏感，也接受服务器原名（如 `INBOX`、`Sent Messages`）；IMAP 的自定义文件夹在本地统一归为 `other`。
- 远程同步：通用名（`inbox`、`sent` 等）会自动映射到 IMAP 实际文件夹、Outlook 文件夹或 Gmail 标签；IMAP 也可直接传 `GET /imap/folders` 返回的 `path`。Gmail 的 `archive` 没有对应标签，会不加过滤地拉取。
- **IMAP 单封操作**（详情未命中缓存、标记已读/未读、删除、回复、附件下载）的 `folder` 会原样交给 IMAP 服务器，必须是 `GET /imap/folders` 返回的真实 `path`（如 `INBOX`、`Sent Messages`），省略时默认 `INBOX`。列表项里的 `folder` 是归一化后的值（如 `sent`），不能直接当作 IMAP 文件夹名。

**响应格式**（邮件列表项）：
```json
{
  "id": "消息ID（IMAP 为 imap:<uid>）", "provider": "gmail",
  "subject": "主题",
  "from": {"name": "...", "address": "..."},
  "toRecipients": [{"name": "...", "address": "..."}],
  "receivedDateTime": "ISO8601", "sentDateTime": "ISO8601",
  "bodyPreview": "摘要",
  "isRead": true, "hasAttachments": false,
  "folder": "inbox", "labelIds": ["INBOX"]
}
```

`labelIds` 只在 Gmail 邮件中出现，`categories` 只在 Outlook 邮件中出现。

### 3. 单封邮件操作

| 操作 | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| 获取详情 | GET `/{id}?email=` | GET `/message?id={id}&email=` | GET `/{uid}?email=&folder=` |
| 标记已读 | POST `/{id}/read?email=` | POST `/message/read?id={id}&email=` | POST `/{uid}/read?email=&folder=` |
| 标记未读 | POST `/{id}/unread?email=` | POST `/message/unread?id={id}&email=` | POST `/{uid}/unread?email=&folder=` |
| 删除 | DELETE `/{id}?email=` | DELETE `/message?id={id}&email=` | DELETE `/{uid}?email=&folder=` |

> 所有路径前缀为 `/api/{provider}/messages`（Gmail/IMAP）或 `/api/outlook/`（Outlook 特殊路由）。IMAP 的 `{uid}` 可直接用列表返回的 `id`（`imap:<uid>`），`folder` 规则见第 2 节，INBOX 可省略。

**邮件详情额外字段**：`body: {content, contentType}`, `ccRecipients`, `attachments: [{id, filename, contentType, size}]`。IMAP 附件的 `id` 是附件在该邮件中的序号字符串（`"0"`、`"1"`……）。

### 4. 发送与回复

**发送新邮件** — `POST /api/{p}/send`：
```json
{
  "email": "sender@example.com",
  "toRecipients": [{"name": "收件人", "address": "to@example.com"}],
  "ccRecipients": [],
  "bccRecipients": [],
  "subject": "主题",
  "body": "正文（支持 HTML）",
  "contentType": "html",
  "attachments": []
}
```

`attachments` 每项为 `{filename, content（base64）, contentType}`。Gmail 要求至少一个非空收件人。IMAP 账户的 `smtpStatus` 为 `unverified`（仅收信接入）时，发送、回复、发送草稿均返回 409（`error: smtp_unverified`），需先引导用户重新验证 SMTP。

**回复邮件**：

| Provider | 端点 | Body |
|----------|------|------|
| Gmail | POST `/gmail/reply` | `{email, messageId, body, contentType}` |
| Outlook | POST `/outlook/message/reply?id={id}&email=` | `{body, contentType}` |
| IMAP | POST `/imap/reply` | `{email, uid, folder, body, contentType}`（`uid` 可用 `imap:<uid>`，`folder` 默认 `INBOX`） |

### 5. 搜索（三种邮箱均支持）

`GET /api/{p}/search?email={email}&q={keyword}`（`{p}` 为 `gmail`、`outlook` 或 `imap`）

搜索只查**本地缓存**，不访问邮件服务器；搜不到时先按规则 3 远程同步再搜。

| 参数 | 说明 |
|------|------|
| `q` | 关键词，**只匹配主题**（大小写不敏感） |
| `from` | 发件人地址（包含匹配） |
| `dateFrom` / `dateTo` | 日期范围 YYYY-MM-DD（按本机时区，含首尾两天） |
| `hasAttachment` | `true` 时只返回带附件的邮件（`false` 不做筛选） |
| `isUnread` | `true` 时只返回未读邮件（`false` 不做筛选） |
| `folder` | 文件夹过滤，取值同本地缓存列表 |
| `offset` / `limit` | 分页，`limit` 最大 200 |

参数名必须完全一致，未知参数（如 `query`、`hasAttachments`）直接返回 400。返回 `{messages, total, offset, limit}`。

需要按正文或发件人在 Gmail 服务器上全文检索时，改用 `POST /gmail/messages/fetch?email=` 的 `query` 参数：它原样交给 Gmail API，支持 Gmail 搜索语法（如 `from:`、`has:attachment`），结果同时写入本地缓存。Outlook 与 IMAP 没有对应的远程检索参数。较旧的客户端若对 `/outlook/search` 或 `/imap/search` 返回 404，改为分页读取 `GET /{p}/messages` 后自行筛选。

### 6. 附件下载

| Provider | 方法 | 端点 | Body |
|----------|------|------|------|
| Gmail | POST | `/gmail/messages/{messageId}/attachment` | `{email, attachmentId}` |
| Outlook | POST | `/outlook/attachment` | `{email, messageId, attachmentId}` |
| IMAP | POST | `/imap/attachment` | `{email, messageId, attachmentId, folder?}` |

- `attachmentId` 取自邮件详情的 `attachments[].id`，先调用详情接口拿到附件列表。
- IMAP：`messageId` 直接用列表返回的 `id`（如 `imap:12345`）；`attachmentId` 是附件序号字符串（第一个附件为 `"0"`）；`folder` 为服务器上的真实文件夹路径，INBOX 可省略。
- **下载附件时必须给 `MailOperations` 传 `save_to`**（目标文件路径）：工具在进程内完成 base64 解码并写入文件，只返回绝对路径、字节数与 SHA-256；不传 `save_to` 时附件响应会被工具拒绝返回。目标路径须位于允许写入的工作目录内。
- 端点原始响应为 `result: {data: <base64>, size}`；响应超过约 32MB 时工具会拒绝解析，此时按工具错误提示中的流式落盘办法处理，或请用户在邮箱页面手工导出附件。

示例（IMAP）：

```json
{
  "path": "/api/imap/attachment",
  "method": "POST",
  "body": {"email": "me@example.com", "messageId": "imap:12345", "attachmentId": "0"},
  "save_to": "./attachments/report.pdf"
}
```

> Gmail 使用 POST 因为 attachmentId 可能超出 URL 长度限制。

### 7. 草稿管理

**Gmail**：

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取草稿列表 | GET | `/gmail/drafts?email=&limit=` |
| 获取草稿详情 | GET | `/gmail/drafts/{draftId}?email=` |
| 创建草稿 | POST | `/gmail/drafts` — body: `{email, to, cc, subject, body, contentType}`（`to` / `cc` 是逗号分隔的地址字符串） |
| 更新草稿 | PUT | `/gmail/drafts/{draftId}` — body 同创建 |
| 删除草稿 | DELETE | `/gmail/drafts/{draftId}?email=` |

**Outlook**：

| 操作 | 方法 | 端点 |
|------|------|------|
| 创建草稿 | POST | `/outlook/drafts` — body: `{email, toRecipients, subject, body, contentType}` |
| 更新草稿 | PUT | `/outlook/drafts?id={draftId}&email=` — body 同创建 |
| 删除草稿 | DELETE | `/outlook/drafts?id={draftId}&email=` |
| 发送草稿 | POST | `/outlook/drafts/send?id={draftId}&email=` |

**IMAP**：

| 操作 | 方法 | 端点 |
|------|------|------|
| 创建草稿 | POST | `/imap/drafts` — body: `{email, to, cc, subject, body, contentType}`（`to` / `cc` 是逗号分隔的地址字符串，不是 `toRecipients` 数组）；返回 `{uid, id}` |
| 更新草稿 | PUT | `/imap/drafts/{uid}` — body 同创建；实现是删掉旧草稿再新建，返回**新的** `{uid, id}`，之后发送或删除要用新 uid（拿旧 uid 会得到 404 `Draft not found`）。服务器不支持 UIDPLUS 时返回的 uid 为 0，此时先重新读取草稿列表再操作 |
| 删除草稿 | DELETE | `/imap/drafts/{uid}?email=` |
| 发送草稿 | POST | `/imap/drafts/{uid}/send?email=` — `email` 放查询串，无需 body |

### 8. 标签管理（统一接口）

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取标签列表 | GET | `/labels?provider=&email=` |
| 获取单个标签 | GET | `/labels/{labelId}` |
| 创建标签 | POST | `/labels` — body: `{name, color, provider, email, visible}` |
| 更新标签 | PUT | `/labels/{labelId}` — body: `{name, color, order, visible}` |
| 删除标签 | DELETE | `/labels/{labelId}` |
| 获取邮件标签 | GET | `/mails/{p}/{email}/labels?mailId=` |
| 添加邮件标签 | POST | `/mails/{p}/{email}/labels?mailId=` — body: `{"labelId": "..."}` |
| 批量设置标签 | PUT | `/mails/{p}/{email}/labels?mailId=` — body: `{"labelIds": [...]}` |
| 移除邮件标签 | DELETE | `/mails/{p}/{email}/labels?mailId=&labelId=` |
| 获取标签下邮件 | GET | `/labels/{labelId}/mails?provider=&email=&limit=&offset=` — 返回 `mailIds`（不含邮件内容） |

统一标签接口只修改 DesireCore 本地数据，不会同步到邮件服务器。需要改动服务器侧标签时，使用下方 Gmail 原生标签或第 9 节 Outlook 分类。

**Gmail 原生标签**：
- 获取标签列表：`GET /api/gmail/labels?email=`
- 修改邮件标签：`POST /api/gmail/messages/{id}/labels` — body: `{email, addLabelIds, removeLabelIds}`
- 同步远程标签：`POST /api/gmail/labels/sync?email=`

### 9. Outlook 分类

Outlook 使用 Categories 而非 Labels。

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取分类 | GET | `/outlook/categories?email=` |
| 同步分类 | POST | `/outlook/categories/sync?email=` |
| 创建分类 | POST | `/outlook/categories/create?email=` — body: `{displayName, color}` |
| 更新分类 | PUT | `/outlook/categories/update?email=&categoryId=` — body: `{displayName, color}` |
| 删除分类 | DELETE | `/outlook/categories/delete?email=&categoryId=` |
| 修改邮件分类 | POST | `/outlook/message/categories?id=&email=` — body: `{addCategories, removeCategories}` |

> `color` 使用 Outlook 预设值 `preset0` ~ `preset24`。

### 10. 自动规则

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取所有规则 | GET | `/rules?provider=&email=` |
| 获取单个规则 | GET | `/rules/{ruleId}` |
| 创建规则 | POST | `/rules` |
| 更新规则 | PUT | `/rules/{ruleId}` |
| 删除规则 | DELETE | `/rules/{ruleId}` |
| 启用/禁用 | POST | `/rules/{ruleId}/toggle` |
| 对邮件执行规则 | POST | `/rules/execute` — body: `{provider, email, mailId}` |
| 测试规则匹配 | POST | `/rules/{ruleId}/test` — body 同上 |

**创建规则 body**：
```json
{
  "name": "规则名",
  "description": "说明",
  "provider": "gmail",
  "email": "xxx@gmail.com",
  "enabled": true,
  "conditions": [
    {"field": "from|to|subject|body|has_attachment", "operator": "contains|not_contains|equals|not_equals|starts_with|ends_with|matches_regex|is_true|is_false", "value": "..."}
  ],
  "conditionLogic": "and",
  "actions": [
    {"type": "add_label|remove_label|mark_as_read|mark_as_unread|delete|auto_reply|agent_handle", "value": "..."}
  ],
  "priority": 1,
  "stopOnMatch": false
}
```

正则条件的 operator 是 `matches_regex`（写成 `regex` 会被当作未知操作符，永远不匹配）；`is_true` / `is_false` 只用于 `has_attachment`。

**动作类型说明**：

| type | value | 说明 |
|------|-------|------|
| `add_label` | 标签 ID | 添加本地标签 |
| `remove_label` | 标签 ID | 移除本地标签 |
| `mark_as_read` | 省略 | 仅在本地缓存中标记已读 |
| `mark_as_unread` | 省略 | 仅在本地缓存中标记未读 |
| `delete` | 省略 | 仅从本地缓存删除，服务器上的邮件不受影响 |
| `auto_reply` | 回复文本 | 自动回复固定内容 |
| `agent_handle` | Agent ID | 触发智能体处理邮件 |

> 规则在轮询引擎检测到新邮件时**自动执行**，无需手动调用（IMAP 只覆盖收件箱的新邮件）。`auto_reply` 和 `agent_handle` 支持全部三种邮箱类型；`agent_handle` 在创建或更新规则时绑定当时的 Agent Service 连接。`archive`、`move_to_folder`、`forward_to`、`star` 可以保存，但当前执行时不做任何操作，不要向用户承诺这些效果。

### 11. 授权管理

| 操作 | 方法 | 端点 |
|------|------|------|
| Gmail OAuth | POST | `/gmail/auth/initiate?loginHint={email}` — 返回 `result.authUrl`，由用户在浏览器中打开完成授权 |
| Gmail 状态 | GET | `/gmail/auth/status?email=` |
| Outlook OAuth | POST | `/outlook/auth/initiate` — 返回 `result.authUrl`，由用户在浏览器中打开完成授权 |
| Outlook 状态 | GET | `/outlook/auth/status?email=` |

### 12. 文件夹

| 操作 | 方法 | 端点 |
|------|------|------|
| IMAP 文件夹列表 | GET | `/imap/folders?email=` — 返回 `[{name, path, specialUse, flags}]`，IMAP 单封操作的 `folder` 使用其中的 `path` |
| Outlook 文件夹列表 | GET | `/outlook/folders?email=` |

> Gmail 文件夹固定：inbox, sent, drafts, trash, spam, archive。

---

## 数据同步机制

邮件系统采用**本地缓存 + 定期轮询**：

- **写操作**（发送、标记、删除、Gmail 原生标签、Outlook 分类）：通过对应 provider 端点同时更新本地和远程，无延迟；统一标签接口（第 8 节）和自动规则中的标记、删除、标签动作只修改本地
- **读操作**（查询、搜索）：返回本地缓存，可能有延迟（默认 30 秒轮询）
- **远程变更**（用户在官方页面操作）：Gmail / Outlook 需等待下次轮询同步；IMAP 轮询只拉取收件箱的新邮件，其他文件夹需主动调用 `messages/fetch`，服务器上对已缓存邮件做的已读、删除等变更不会回写到本地

**存储路径**：`${DESIRECORE_ROOT}/mail/{provider}/{email}/`（meta.json, index.json, messages/）

---

## 错误处理

| 状态码 | 原因 | 处理 |
|--------|------|------|
| 400 | 参数错误（包括参数放错位置，如把查询串参数放进 body） | 按 `msg` 检查参数名与位置 |
| 401 | Gmail/Outlook 授权失效、IMAP 账户未配置，或缺少 Mail Service capability | **按规则 1 处理**，不要尝试其他途径 |
| 404 | 资源不存在 | 先同步再重试（规则 3） |
| 409 | IMAP 账户 SMTP 未验证（`error: smtp_unverified`） | 引导用户重新验证 SMTP（`POST /imap/accounts/verify-smtp`） |
| 500 | 内部错误（IMAP 常见原因：`folder` 不是服务器上存在的文件夹） | 先检查 `folder`，仍失败则告知用户稍后重试 |

**IMAP 注意**：国内邮箱（QQ、163）需使用"授权码"而非登录密码。用 `/imap/test` 预先验证配置，并检查返回的 `result.imap.success` 与 `result.smtp.success`。
