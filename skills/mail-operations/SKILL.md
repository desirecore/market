---
name: 邮箱操作
description: >-
  Use this skill whenever the user wants to interact with email. This includes
  reading inbox, sending emails, replying, searching messages, managing labels
  and categories, downloading attachments, setting up auto-reply rules, or
  triggering agents to handle incoming emails. Supports Gmail, Outlook, and
  IMAP/SMTP (QQ Mail, 163, Yahoo, etc.) through DesireCore's local REST API.
  Use when 用户提到 邮件、邮箱、收件箱、发邮件、回复邮件、查邮件、Gmail、
  Outlook、QQ邮箱、163邮箱、附件、标签、草稿、自动回复、邮件规则、
  转发、抄送、未读邮件、收信、发信、邮件同步、邮件搜索。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: false
tags:
  - mail
  - email
  - gmail
  - outlook
  - imap
  - smtp
metadata:
  author: desirecore
  updated_at: '2026-04-10'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ml-a" x1="2" y1="4" x2="22"
    y2="20" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><rect x="2" y="4"
    width="20" height="16" rx="2" fill="url(#ml-a)" fill-opacity="0.1"
    stroke="url(#ml-a)" stroke-width="1.5"/><path d="m22 7-8.97 5.7a1.94 1.94
    0 0 1-2.06 0L2 7" stroke="url(#ml-a)" stroke-width="1.5"
    stroke-linecap="round" stroke-linejoin="round"/></svg>
  short_desc: 邮件收发、搜索、标签管理、自动规则与智能体邮件处理
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# 邮箱操作

通过 DesireCore 本地 REST API 操作邮件系统，支持 Gmail / Outlook / IMAP（QQ、163 等）。

## API 基础信息

- **Base URL**: `https://127.0.0.1:62000/api`
- **认证**: 无需认证（本地服务）
- **Content-Type**: `application/json`
- **SSL**: 使用 `curl -k` 跳过自签名证书验证
- **响应格式**: 成功 `{"code": 1, "msg": "Success", "result": ...}`，失败 `{"code": 0, "msg": "错误信息"}`

---

## 强制行为规则

以下规则优先级最高，每次操作必须遵守。

### 规则 1：只能通过本地 API 操作

所有邮件操作**必须且只能**通过 `https://127.0.0.1:62000` 完成。**禁止**调用外部邮件客户端或浏览器。

如果 API 返回 **401（授权过期）**：
1. 告知用户该账户授权已失效
2. 提示在 DesireCore 中重新授权
3. Gmail: `POST /api/gmail/auth/initiate?loginHint={email}`，Outlook: `POST /api/outlook/auth/initiate`

### 规则 2：操作前先确认账户

执行任何操作前，**必须先调用 `GET /api/accounts`** 获取账户列表：
- 按邮箱地址或域名匹配用户指定的账户（"QQ 邮箱"→ imap 中 `qq.com`）
- 仅有一个账户且用户说"我的邮箱"→ 直接使用
- 找不到匹配账户 → 告知用户并提示添加

### 规则 3：查询为空时自动同步

查询返回空列表或找不到指定数据时：
1. 调用 `POST /{provider}/messages/fetch` 同步远程数据
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
| 邮件详情 | 路径参数 `/{id}` | 查询参数 `?id={id}` | UID `/{uid}?folder=` |
| 搜索 | 支持 | 不支持 | 不支持 |
| 草稿 | 支持 | 不支持 | 不支持 |
| 附件下载 | 支持 | 不支持 | 不支持 |
| 标签/分类 | 原生标签 | Categories | 仅本地标签 |
| 自动规则 | 支持 | 支持 | 支持 |

---

## 核心操作

以下 `{p}` 代表 provider（`gmail`、`outlook`、`imap`），`{email}` 需 URL 编码。

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
| 测试 IMAP 连接 | POST | `/imap/test` — body: `{email, password, imap: {host, port, secure}, smtp: {host, port, secure}}` |
| 添加 IMAP 账户 | POST | `/imap/accounts` — body 同上，加 `displayName` |

### 2. 邮件列表与同步

| 操作 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 查询本地缓存 | GET | `/{p}/messages` | `email, offset, limit, folder` |
| 远程同步 | POST | `/{p}/messages/fetch` | `email, limit, folder` |
| 手动触发同步 | POST | `/sync` | `provider, email` |

**folder 取值**：Gmail/Outlook: `inbox, sent, drafts, trash, spam, archive`；IMAP: `INBOX, Sent, Drafts, Trash` 等。

**响应格式**（邮件列表项）：
```json
{
  "id": "消息ID", "subject": "主题",
  "from": {"name": "...", "address": "..."},
  "to": [{"name": "...", "address": "..."}],
  "date": "ISO8601", "snippet": "摘要",
  "isRead": true, "hasAttachments": false,
  "labels": ["INBOX"], "folder": "inbox"
}
```

### 3. 单封邮件操作

| 操作 | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| 获取详情 | GET `/{id}?email=` | GET `/message?id={id}&email=` | GET `/{uid}?email=&folder=` |
| 标记已读 | POST `/{id}/read?email=` | POST `/message/read?id={id}&email=` | POST `/{uid}/read?email=&folder=` |
| 标记未读 | POST `/{id}/unread?email=` | POST `/message/unread?id={id}&email=` | POST `/{uid}/unread?email=&folder=` |
| 删除 | DELETE `/{id}?email=` | DELETE `/message?id={id}&email=` | DELETE `/{uid}?email=&folder=` |

> 所有路径前缀为 `/api/{provider}/messages`（Gmail/IMAP）或 `/api/outlook/`（Outlook 特殊路由）。

**邮件详情额外字段**：`body: {content, contentType}`, `cc`, `attachments: [{id, filename, mimeType, size}]`

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

**回复邮件**：

| Provider | 端点 | Body |
|----------|------|------|
| Gmail | POST `/gmail/reply` | `{email, messageId, body, contentType}` |
| Outlook | POST `/outlook/message/reply?id={id}&email=` | `{body, contentType}` |
| IMAP | POST `/imap/reply` | `{email, uid, folder, body, contentType}` |

### 5. 搜索（仅 Gmail）

`GET /api/gmail/search?email={email}&q={keyword}`

| 参数 | 说明 |
|------|------|
| `q` | 关键词（搜索主题、正文、发件人） |
| `from` | 发件人地址 |
| `dateFrom` / `dateTo` | 日期范围 YYYY-MM-DD |
| `hasAttachment` | true/false |
| `isUnread` | true/false |
| `offset` / `limit` | 分页 |

### 6. 附件下载（仅 Gmail）

`POST /api/gmail/messages/{messageId}/attachment` — body: `{"email": "...", "attachmentId": "..."}`

响应 `result.data` 为 base64 编码，解码后保存文件。

> 使用 POST 因为 Gmail attachmentId 可能超出 URL 长度限制。

### 7. 草稿管理（仅 Gmail）

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取草稿列表 | GET | `/gmail/drafts?email=&limit=` |
| 获取草稿详情 | GET | `/gmail/drafts/{draftId}?email=` |
| 创建草稿 | POST | `/gmail/drafts` — body: `{email, to, cc, subject, body, contentType}` |
| 更新草稿 | PUT | `/gmail/drafts/{draftId}` — body 同创建 |
| 删除草稿 | DELETE | `/gmail/drafts/{draftId}?email=` |

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
| 获取标签下邮件 | GET | `/labels/{labelId}/mails?provider=&email=&limit=&offset=` |

**Gmail 原生标签**：`POST /api/gmail/messages/{id}/labels` — body: `{email, addLabelIds, removeLabelIds}`
**Gmail 标签同步**：`POST /api/gmail/labels/sync?email=`

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
    {"field": "from|to|subject|body|has_attachment", "operator": "contains|equals|regex|...", "value": "..."}
  ],
  "conditionLogic": "and",
  "actions": [
    {"type": "add_label|remove_label|mark_as_read|mark_as_unread|archive|delete|auto_reply|agent_handle", "value": "..."}
  ],
  "priority": 1,
  "stopOnMatch": false
}
```

**动作类型说明**：

| type | value | 说明 |
|------|-------|------|
| `add_label` | 标签 ID | 添加标签 |
| `remove_label` | 标签 ID | 移除标签 |
| `mark_as_read` | 省略 | 标记已读 |
| `mark_as_unread` | 省略 | 标记未读 |
| `archive` | 省略 | 归档 |
| `delete` | 省略 | 删除 |
| `auto_reply` | 回复文本 | 自动回复固定内容 |
| `agent_handle` | Agent ID | 触发智能体处理邮件 |

> 规则在轮询引擎检测到新邮件时**自动执行**，无需手动调用。`auto_reply` 和 `agent_handle` 支持全部三种邮箱类型。

### 11. 授权管理

| 操作 | 方法 | 端点 |
|------|------|------|
| Gmail OAuth | POST | `/gmail/auth/initiate?loginHint={email}` — 打开浏览器授权 |
| Gmail 状态 | GET | `/gmail/auth/status?email=` |
| Outlook OAuth | POST | `/outlook/auth/initiate` — 打开浏览器授权 |
| Outlook 状态 | GET | `/outlook/auth/status?email=` |

### 12. 文件夹

| 操作 | 方法 | 端点 |
|------|------|------|
| IMAP 文件夹列表 | GET | `/imap/folders?email=` |
| Outlook 文件夹列表 | GET | `/outlook/folders?email=` |

> Gmail 文件夹固定：inbox, sent, drafts, trash, spam, archive。

---

## 数据同步机制

邮件系统采用**本地缓存 + 定期轮询**：

- **写操作**（发送、标记、删除、标签）：同时更新本地和远程，无延迟
- **读操作**（查询、搜索）：返回本地缓存，可能有延迟（默认 30 秒轮询）
- **远程变更**（用户在官方页面操作）：需等待下次轮询同步

**存储路径**：`~/.desirecore/mail/{provider}/{email}/`（index.json, messages/, sync.json）

---

## 错误处理

| 状态码 | 原因 | 处理 |
|--------|------|------|
| 400 | 参数错误 | 检查请求参数 |
| 401 | 授权过期 | **按规则 1 处理**，不要尝试其他途径 |
| 404 | 资源不存在 | 先同步再重试（规则 3） |
| 500 | 内部错误 | 告知用户稍后重试 |

**IMAP 注意**：国内邮箱（QQ、163）需使用"授权码"而非登录密码。用 `/imap/test` 预先验证配置。
