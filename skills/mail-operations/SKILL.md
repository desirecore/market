---
name: mail-operations
description: >-
  Use this skill whenever the user wants to interact with email. This includes
  reading inbox, sending emails, replying, searching messages, managing labels
  and categories, downloading attachments, setting up auto-reply rules, or
  triggering agents to handle incoming emails. Supports Gmail, Outlook, and
  IMAP/SMTP (QQ Mail, 163, Yahoo, etc.) through DesireCore's local REST API.
  Use when 用户提到 邮件、邮箱、收件箱、发邮件、回复邮件、查邮件、Gmail、
  Outlook、QQ邮箱、163邮箱、附件、标签、草稿、自动回复、邮件规则、
  转发、抄送、未读邮件、收信、发信、邮件同步、邮件搜索。
version: 1.0.4
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - mail
  - email
  - gmail
  - outlook
  - imap
  - smtp
metadata:
  author: desirecore
  updated_at: '2026-06-20'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 邮箱操作
      short_desc: 邮件收发、搜索、标签管理、自动规则与智能体邮件处理
      description: >-
        Use this skill whenever the user wants to interact with email. This includes reading inbox, sending emails, replying, searching messages, managing labels and categories, downloading attachments, setting up auto-reply rules, or triggering agents to handle incoming emails. Supports Gmail, Outlook, and IMAP/SMTP (QQ Mail, 163, Yahoo, etc.) through DesireCore's local REST API. Use when 用户提到 邮件、邮箱、收件箱、发邮件、回复邮件、查邮件、Gmail、 Outlook、QQ邮箱、163邮箱、附件、标签、草稿、自动回复、邮件规则、 转发、抄送、未读邮件、收信、发信、邮件同步、邮件搜索。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:24bffbade0dc09a7
      translated_by: human
    en-US:
      name: Email Operations
      short_desc: Email send/receive, search, label management, auto-rules, and Agent-driven email handling
      description: >-
        Use this skill whenever the user wants to interact with email. This includes reading inbox, sending emails, replying, searching messages, managing labels and categories, downloading attachments, setting up auto-reply rules, or triggering agents to handle incoming emails. Supports Gmail, Outlook, and IMAP/SMTP (QQ Mail, 163, Yahoo, etc.) through DesireCore's local REST API. Use when the user mentions email, mailbox, inbox, sending email, replying, checking email, Gmail, Outlook, QQ Mail, 163 Mail, attachments, labels, drafts, auto-reply, email rules, forwarding, CC, unread email, receiving, sending, email sync, or email search.
      body: ./SKILL.md
      source_hash: sha256:0ee04ebff49d92ea
      translated_by: human
      translated_at: '2026-05-03'
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
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# mail-operations Skill

## L0: One-line Summary

Send and receive email, search, manage labels, and run automation rules via a local REST API; supports Gmail / Outlook / IMAP.

## L1: Overview and Use Cases

### Capability

mail-operations is a **Procedural Skill** that operates email systems through DesireCore's local REST API. It supports three mailbox types—Gmail (OAuth2), Outlook (MSAL), and IMAP/SMTP (QQ, 163, Yahoo, etc.)—covering send/receive, search, label management, attachment download, draft management, and automation rules.

### Use Cases

- The user wants to view the inbox, send, or reply to email
- The user wants to search for specific emails or manage email labels/categories
- The user wants to download attachments or manage drafts
- The user wants to set up auto-reply rules or trigger an Agent to handle email

### Core Value

- **Unified interface**: three mailbox types are operated through a unified API, lowering complexity
- **Local and secure**: all operations go through the local API; no need to expose credentials
- **Smart integration**: supports automation rules and Agent-based email handling

## L2: Detailed Specification

## How to Access the Email Service

Users can reach the email management interface via:

1. Click the **third icon** (folder icon) in the left navigation rail to open the **Resource Explorer**
2. On the Resource Explorer home page, find and click the **"Emails"** card to enter email management

> If a user doesn't know how to open the email page, guide them through the steps above. They can also click "Open Resource Explorer" from the top-right corner of the chat interface, then select the Emails card.

---

## API Basics

- **Base URL**: `https://127.0.0.1:62000/api`
- **Authentication**: none required (local service)
- **Content-Type**: `application/json`
- **SSL**: use `curl -k` to skip self-signed certificate verification
- **Response format**: success `{"code": 1, "msg": "Success", "result": ...}`, failure `{"code": 0, "msg": "error message"}`

---

## Mandatory Behavior Rules

The following rules have the highest priority and must be obeyed on every operation.

### Rule 1: Operate Only Through the Local API

All email operations **must and may only** be done through `https://127.0.0.1:62000`. **Never** call an external email client or browser.

If the API returns **401 (authorization expired)**:
1. Tell the user the account's authorization has expired
2. Prompt the user to re-authorize in DesireCore
3. Gmail: `POST /api/gmail/auth/initiate?loginHint={email}`, Outlook: `POST /api/outlook/auth/initiate`

### Rule 2: Confirm the Account Before Operating

Before performing any operation, **you must first call `GET /api/accounts`** to obtain the account list:
- Match the user's specified account by email address or domain ("QQ mailbox" → IMAP `qq.com`)
- Only one account exists and the user says "my mailbox" → use it directly
- No matching account found → tell the user and prompt them to add one

### Rule 3: Auto-Sync When the Query Is Empty

When a query returns an empty list or cannot find the specified data:
1. Call `POST /{provider}/messages/fetch` to sync remote data
2. **Automatically retry** the original query
3. Only inform the user if it is still empty

### Rule 4: Prompt for a Refresh After Write Operations

After a write operation (send, reply, delete, mark, label change, etc.) succeeds, prompt: `Operation completed. Do you want me to refresh the current mailbox view to see the latest state?`

---

## Quick Reference: Differences Between the Three Mailbox Types

| Feature | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| Authorization | OAuth2 | OAuth2 (MSAL) | password / app password |
| Provider path | `/gmail/` | `/outlook/` | `/imap/` |
| Message detail | path param `/{id}` | query param `?id={id}` | UID `/{uid}?folder=` |
| Search | supported | not supported | not supported |
| Drafts | supported (incl. list/detail) | supported (create/send) | supported (create/send) |
| Attachment download | supported | supported | supported |
| Labels/categories | native labels | Categories | local labels only |
| Auto-rules | supported | supported | supported |

---

## Core Operations

In the following, `{p}` denotes the provider (`gmail`, `outlook`, `imap`); `{email}` must be URL-encoded.

### 1. Account Management

| Operation | Method | Endpoint |
|------|------|------|
| Get all accounts | GET | `/accounts` |
| Get accounts with settings | GET | `/accounts-with-settings` |
| Delete account | DELETE | `/accounts/{p}/{email}` |
| Get account settings | GET | `/accounts/{p}/{email}/settings` |
| Update account settings | PUT | `/accounts/{p}/{email}/settings` |
| Update display name | PUT | `/accounts/{p}/{email}/displayName` — body: `{"displayName": "..."}` |

**IMAP-specific**:

| Operation | Method | Endpoint |
|------|------|------|
| Get preset mailbox configs | GET | `/imap/presets` — returns server configs for QQ/163/Yahoo, etc. |
| Test IMAP connection | POST | `/imap/test` — body: `{email, password, imap: {host, port, secure}, smtp: {host, port, secure}}` |
| Add IMAP account | POST | `/imap/accounts` — same body as above plus `displayName` |

### 2. Message List and Sync

| Operation | Method | Endpoint | Parameters |
|------|------|------|------|
| Query local cache | GET | `/{p}/messages` | `email, offset, limit, folder` |
| Remote sync | POST | `/{p}/messages/fetch` | `email, limit, folder` |
| Manually trigger sync | POST | `/sync` | `provider, email` |

**folder values**: Gmail/Outlook: `inbox, sent, drafts, trash, spam, archive`; IMAP: `INBOX, Sent, Drafts, Trash`, etc.

**Response format** (message list item):
```json
{
  "id": "messageID", "subject": "subject",
  "from": {"name": "...", "address": "..."},
  "to": [{"name": "...", "address": "..."}],
  "date": "ISO8601", "snippet": "snippet",
  "isRead": true, "hasAttachments": false,
  "labels": ["INBOX"], "folder": "inbox"
}
```

### 3. Single Message Operations

| Operation | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| Get detail | GET `/{id}?email=` | GET `/message?id={id}&email=` | GET `/{uid}?email=&folder=` |
| Mark as read | POST `/{id}/read?email=` | POST `/message/read?id={id}&email=` | POST `/{uid}/read?email=&folder=` |
| Mark as unread | POST `/{id}/unread?email=` | POST `/message/unread?id={id}&email=` | POST `/{uid}/unread?email=&folder=` |
| Delete | DELETE `/{id}?email=` | DELETE `/message?id={id}&email=` | DELETE `/{uid}?email=&folder=` |

> All paths are prefixed with `/api/{provider}/messages` (Gmail/IMAP) or `/api/outlook/` (Outlook's special routing).

**Extra fields in message detail**: `body: {content, contentType}`, `cc`, `attachments: [{id, filename, mimeType, size}]`

### 4. Send and Reply

**Send a new email** — `POST /api/{p}/send`:
```json
{
  "email": "sender@example.com",
  "toRecipients": [{"name": "recipient", "address": "to@example.com"}],
  "ccRecipients": [],
  "bccRecipients": [],
  "subject": "subject",
  "body": "body (HTML supported)",
  "contentType": "html",
  "attachments": []
}
```

**Reply to an email**:

| Provider | Endpoint | Body |
|----------|------|------|
| Gmail | POST `/gmail/reply` | `{email, messageId, body, contentType}` |
| Outlook | POST `/outlook/message/reply?id={id}&email=` | `{body, contentType}` |
| IMAP | POST `/imap/reply` | `{email, uid, folder, body, contentType}` |

### 5. Search (Gmail only)

`GET /api/gmail/search?email={email}&q={keyword}`

| Parameter | Description |
|------|------|
| `q` | keyword (searches subject, body, sender) |
| `from` | sender address |
| `dateFrom` / `dateTo` | date range YYYY-MM-DD |
| `hasAttachment` | true/false |
| `isUnread` | true/false |
| `offset` / `limit` | pagination |

### 6. Attachment Download

| Provider | Method | Endpoint | Body |
|----------|------|------|------|
| Gmail | POST | `/gmail/messages/{messageId}/attachment` | `{email, attachmentId}` |
| Outlook | POST | `/outlook/attachment` | `{email, messageId, attachmentId}` |
| IMAP | POST | `/imap/attachment` | `{email, uid, folder, partId}` |

The response `result.data` is base64-encoded; decode it and save to a file.

> Gmail uses POST because the attachmentId may exceed URL length limits.

### 7. Draft Management

**Gmail**:

| Operation | Method | Endpoint |
|------|------|------|
| List drafts | GET | `/gmail/drafts?email=&limit=` |
| Get draft detail | GET | `/gmail/drafts/{draftId}?email=` |
| Create draft | POST | `/gmail/drafts` — body: `{email, to, cc, subject, body, contentType}` |
| Update draft | PUT | `/gmail/drafts/{draftId}` — same body as create |
| Delete draft | DELETE | `/gmail/drafts/{draftId}?email=` |

**Outlook**:

| Operation | Method | Endpoint |
|------|------|------|
| Create draft | POST | `/outlook/drafts` — body: `{email, toRecipients, subject, body, contentType}` |
| Update draft | PUT | `/outlook/drafts?id={draftId}&email=` — same body as create |
| Delete draft | DELETE | `/outlook/drafts?id={draftId}&email=` |
| Send draft | POST | `/outlook/drafts/send?id={draftId}&email=` |

**IMAP**:

| Operation | Method | Endpoint |
|------|------|------|
| Create draft | POST | `/imap/drafts` — body: `{email, toRecipients, subject, body, contentType}` |
| Update draft | PUT | `/imap/drafts/{uid}` — body: `{email, folder, toRecipients, subject, body, contentType}` |
| Delete draft | DELETE | `/imap/drafts/{uid}?email=&folder=` |
| Send draft | POST | `/imap/drafts/{uid}/send` — body: `{email, folder}` |

### 8. Label Management (Unified Interface)

| Operation | Method | Endpoint |
|------|------|------|
| List labels | GET | `/labels?provider=&email=` |
| Get a single label | GET | `/labels/{labelId}` |
| Create label | POST | `/labels` — body: `{name, color, provider, email, visible}` |
| Update label | PUT | `/labels/{labelId}` — body: `{name, color, order, visible}` |
| Delete label | DELETE | `/labels/{labelId}` |
| Get email's labels | GET | `/mails/{p}/{email}/labels?mailId=` |
| Add label to email | POST | `/mails/{p}/{email}/labels?mailId=` — body: `{"labelId": "..."}` |
| Bulk set labels | PUT | `/mails/{p}/{email}/labels?mailId=` — body: `{"labelIds": [...]}` |
| Remove label from email | DELETE | `/mails/{p}/{email}/labels?mailId=&labelId=` |
| Get emails under a label | GET | `/labels/{labelId}/mails?provider=&email=&limit=&offset=` |

**Gmail native labels**:
- List labels: `GET /api/gmail/labels?email=`
- Modify message labels: `POST /api/gmail/messages/{id}/labels` — body: `{email, addLabelIds, removeLabelIds}`
- Sync remote labels: `POST /api/gmail/labels/sync?email=`

### 9. Outlook Categories

Outlook uses Categories instead of Labels.

| Operation | Method | Endpoint |
|------|------|------|
| Get categories | GET | `/outlook/categories?email=` |
| Sync categories | POST | `/outlook/categories/sync?email=` |
| Create category | POST | `/outlook/categories/create?email=` — body: `{displayName, color}` |
| Update category | PUT | `/outlook/categories/update?email=&categoryId=` — body: `{displayName, color}` |
| Delete category | DELETE | `/outlook/categories/delete?email=&categoryId=` |
| Modify message categories | POST | `/outlook/message/categories?id=&email=` — body: `{addCategories, removeCategories}` |

> `color` uses Outlook preset values `preset0` ~ `preset24`.

### 10. Automation Rules

| Operation | Method | Endpoint |
|------|------|------|
| List all rules | GET | `/rules?provider=&email=` |
| Get a single rule | GET | `/rules/{ruleId}` |
| Create rule | POST | `/rules` |
| Update rule | PUT | `/rules/{ruleId}` |
| Delete rule | DELETE | `/rules/{ruleId}` |
| Enable/disable | POST | `/rules/{ruleId}/toggle` |
| Run rule on a message | POST | `/rules/execute` — body: `{provider, email, mailId}` |
| Test rule match | POST | `/rules/{ruleId}/test` — same body as above |

**Create rule body**:
```json
{
  "name": "rule name",
  "description": "description",
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

**Action types**:

| type | value | Description |
|------|-------|------|
| `add_label` | label ID | add a label |
| `remove_label` | label ID | remove a label |
| `mark_as_read` | omit | mark as read |
| `mark_as_unread` | omit | mark as unread |
| `archive` | omit | archive |
| `delete` | omit | delete |
| `auto_reply` | reply text | auto-reply with fixed content |
| `agent_handle` | Agent ID | trigger an Agent to handle the email |

> Rules are **executed automatically** when the polling engine detects a new email; no manual call is required. `auto_reply` and `agent_handle` support all three mailbox types.

### 11. Authorization Management

| Operation | Method | Endpoint |
|------|------|------|
| Gmail OAuth | POST | `/gmail/auth/initiate?loginHint={email}` — opens browser for authorization |
| Gmail status | GET | `/gmail/auth/status?email=` |
| Outlook OAuth | POST | `/outlook/auth/initiate` — opens browser for authorization |
| Outlook status | GET | `/outlook/auth/status?email=` |

### 12. Folders

| Operation | Method | Endpoint |
|------|------|------|
| IMAP folder list | GET | `/imap/folders?email=` |
| Outlook folder list | GET | `/outlook/folders?email=` |

> Gmail folders are fixed: inbox, sent, drafts, trash, spam, archive.

---

## Data Sync Mechanism

The email system uses **local cache + periodic polling**:

- **Write operations** (send, mark, delete, label): update local and remote simultaneously, no delay
- **Read operations** (query, search): return the local cache; may be delayed (default 30-second polling)
- **Remote changes** (the user operates from the official web UI): wait for the next polling cycle to sync

**Storage path**: `${DESIRECORE_ROOT}/mail/{provider}/{email}/` (index.json, messages/, sync.json)

---

## Error Handling

| Status code | Reason | Handling |
|--------|------|------|
| 400 | parameter error | check the request parameters |
| 401 | authorization expired | **handle per Rule 1**; do not try other channels |
| 404 | resource not found | sync first and retry (Rule 3) |
| 500 | internal error | tell the user to retry later |

**IMAP note**: domestic Chinese mailboxes (QQ, 163) require an "app password" instead of the login password. Use `/imap/test` to validate the configuration in advance.
