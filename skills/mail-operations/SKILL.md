---
license: "MIT"
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
version: 1.1.0
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
  updated_at: '2026-10-05'
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
      source_hash: sha256:ec3be525ab586e62
      translated_by: human
      translated_at: '2026-10-05'
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
  required_client_version: 10.0.178
---

# mail-operations Skill

## L0: One-line Summary

Send and receive email, search, manage labels, and run automation rules via a local REST API; supports Gmail / Outlook / IMAP.

## L1: Overview and Use Cases

### Capability

mail-operations is a **Procedural Skill** that operates email systems through DesireCore's local REST API (called via the built-in `MailOperations` tool). It supports three mailbox types—Gmail (OAuth2), Outlook (MSAL), and IMAP/SMTP (QQ, 163, Yahoo, etc.)—covering send/receive, search, label management, attachment download, draft management, and automation rules.

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

- **How to call**: use the built-in `MailOperations` tool. Its parameters are `path` (a relative path starting with `/api/`, with query parameters appended directly to it), `method` (default `GET`), `body` (a JSON object), and `save_to` (only for attachment downloads, see section 6). The tool locates the local Mail Service and attaches the access credential automatically; the Agent neither needs nor can supply a token.
- **Path form**: the endpoints below omit the `/api` prefix; add it when calling. For example, `/imap/messages?email=me%40example.com&limit=20` becomes `path: "/api/imap/messages?email=me%40example.com&limit=20"`. The only exception is the health check `/ping` (no `/api`).
- **Do not connect to the port directly**: do not `curl` `https://127.0.0.1:62000`. The port is allocated dynamically starting at 62000 (when several DesireCore instances run, 62000 may belong to another instance), and in strict capability mode direct requests without the credential always return 401.
- **Parameter location**: GET / DELETE parameters always go in the query string; for POST / PUT follow the tables below. The `email` of endpoints such as `messages/fetch`, mark as read/unread, Outlook single-message operations, and IMAP draft send must be in the query string; putting it in the body returns 400 `Missing email parameter`. For `/sync`, both `provider` and `email` must be in the query string: `provider` in the body returns 400 `Invalid provider`, and `email` alone in the body raises no parameter error but the sync does not take effect.
- **Content-Type**: `application/json` (set automatically by the tool when `body` is passed)
- **Response format**: success `{"code": 1, "msg": "Success", "result": ...}`, failure `{"code": 0, "msg": "error message"}`; some errors also carry a stable error code field `error` (e.g. `smtp_unverified`)

---

## Mandatory Behavior Rules

The following rules have the highest priority and must be obeyed on every operation.

### Rule 1: Operate Only Through the MailOperations Tool

All email operations **must and may only** be done through the built-in `MailOperations` tool, which calls the local Mail Service. **Never** call an external email client or browser, and do not connect to the local port with `curl` / `HttpRequest` (except for the large-attachment streaming-to-disk method explicitly given in a `MailOperations` error message).

If a call returns **401**, distinguish the cause by `msg`:
1. Gmail / Outlook returns `Not authorized` or `Authorization expired`: tell the user the account's authorization has expired and guide them to re-authorize on the DesireCore Emails page. To start it on their behalf, call Gmail `POST /api/gmail/auth/initiate?loginHint={email}` or Outlook `POST /api/outlook/auth/initiate` and give the returned `result.authUrl` to the user to open in a browser (the service does not open a browser by itself)
2. IMAP returns `Account not configured`: the account is missing or its configuration is corrupted; this is not an expired authorization, and the user needs to add the account again (first `/imap/test`, then `/imap/accounts`)
3. The response carries `error: "unauthorized"` (missing or invalid Mail Service capability): the request did not go through `MailOperations`; retry with that tool

### Rule 2: Confirm the Account Before Operating

Before performing any operation, **you must first call `GET /api/accounts`** to obtain the account list:
- Match the user's specified account by email address or domain ("QQ mailbox" → IMAP `qq.com`)
- Only one account exists and the user says "my mailbox" → use it directly
- No matching account found → tell the user and prompt them to add one

### Rule 3: Auto-Sync When the Query Is Empty

When a query returns an empty list or cannot find the specified data:
1. Call `POST /{provider}/messages/fetch?email={email}` to sync remote data (`email` goes in the query string)
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
| Message detail | path param `/{id}` | query param `?id={id}` | path param `/{uid}` (the list's `imap:<uid>` or a bare numeric UID) + `?folder=` |
| Search (local cache) | supported | supported | supported |
| Remote fetch paging | `pageToken` (no `offset`) | `skip` / `offset` | `offset` |
| Drafts | supported (incl. list/detail) | supported (create/update/delete/send) | supported (create/update/delete/send) |
| Attachment download | supported | supported | supported |
| Labels/categories | native labels | Categories | local labels only |
| Sending prerequisite | authorized | authorized | SMTP verified (`smtpStatus: verified`) |
| Auto-rules | supported | supported | supported |

---

## Core Operations

In the following, `{p}` denotes the provider (`gmail`, `outlook`, `imap`); `{email}` must be URL-encoded (`@` → `%40`, `+` → `%2B`).

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
| Test IMAP connection | POST | `/imap/test` — body: `{email, password, imap?: {host, port, secure}, smtp?: {host, port, secure}}`; `imap` / `smtp` may be omitted when the domain has a preset. **A failed connection still returns HTTP 200**; check `result.imap.success` and `result.smtp.success` |
| Add IMAP account | POST | `/imap/accounts` — same body as above, optionally plus `displayName` and `allowUnverifiedSmtp`; success returns 201 with `{email, smtpStatus, smtp}`. If the SMTP test fails it returns 400 by default (`error: smtp_verification_failed`); pass `allowUnverifiedSmtp: true` only when the user agrees to a receive-only account |
| Re-verify SMTP | POST | `/imap/accounts/verify-smtp` — body: `{email}`; a failed verification also returns 200, so check `result.smtp.success` and `result.smtpStatus`: on success `smtpStatus` returns to `verified`; on failure the user needs to update the authorization code and verify again |

### 2. Message List and Sync

| Operation | Method | Endpoint | Parameters |
|------|------|------|------|
| Query local cache | GET | `/{p}/messages` | query string: `email, offset, limit, folder`; returns `{messages, total, offset, limit}` |
| Remote sync | POST | `/{p}/messages/fetch?email=` | `email` must be in the query string; body (or query string): `folder`, `limit` (1–1000, default 20); paging: IMAP `offset`, Outlook `skip` / `offset`, Gmail `pageToken` (Gmail returns 400 for `offset`); returns `messages` plus paging info `pagination` |
| Manually trigger sync | POST | `/sync?provider=&email=` | parameters in the query string; **gmail / outlook only** — IMAP returns 400, use `messages/fetch` instead |

**IMAP remote sync is slow**: every message is downloaded and parsed in full (about 0.65 messages/second measured), so keep each batch's `limit` at 100 or less and page through older mail with `offset` (how many of the newest messages to skip).

**folder values**:
- Local cache list and search: `inbox, sent, drafts, trash, spam, archive, other`, case-insensitive; server names (e.g. `INBOX`, `Sent Messages`) are accepted too. IMAP custom folders are all stored locally as `other`.
- Remote sync: generic names (`inbox`, `sent`, ...) are mapped automatically to the actual IMAP folder, the Outlook folder, or the Gmail label; for IMAP you may also pass a `path` returned by `GET /imap/folders`. Gmail has no label for `archive`, so it fetches without filtering.
- **IMAP single-message operations** (detail on a cache miss, mark as read/unread, delete, mark as junk / not junk, reply, attachment download) pass `folder` verbatim to the IMAP server, so it must be a real `path` returned by `GET /imap/folders` (e.g. `INBOX`, `Sent Messages`); it defaults to `INBOX` when omitted. The `folder` field of a list item is a normalized value (e.g. `sent`) and cannot be used as an IMAP folder name directly.

**Response format** (message list item):
```json
{
  "id": "messageID (imap:<uid> for IMAP)", "provider": "gmail",
  "subject": "subject",
  "from": {"name": "...", "address": "..."},
  "toRecipients": [{"name": "...", "address": "..."}],
  "receivedDateTime": "ISO8601", "sentDateTime": "ISO8601",
  "bodyPreview": "snippet",
  "isRead": true, "hasAttachments": false,
  "folder": "inbox", "labelIds": ["INBOX"]
}
```

`labelIds` appears only on Gmail messages and `categories` only on Outlook messages.

### 3. Single Message Operations

| Operation | Gmail | Outlook | IMAP |
|------|-------|---------|------|
| Get detail | GET `/{id}?email=` | GET `/message?id={id}&email=` | GET `/{uid}?email=&folder=` |
| Mark as read | POST `/{id}/read?email=` | POST `/message/read?id={id}&email=` | POST `/{uid}/read?email=&folder=` |
| Mark as unread | POST `/{id}/unread?email=` | POST `/message/unread?id={id}&email=` | POST `/{uid}/unread?email=&folder=` |
| Delete | DELETE `/{id}?email=` | DELETE `/message?id={id}&email=` | DELETE `/{uid}?email=&folder=` |
| Mark as junk | POST `/{id}/spam?email=` | POST `/message/spam?id={id}&email=` | POST `/{uid}/spam?email=&folder=` |
| Not junk | POST `/{id}/not-spam?email=` | POST `/message/not-spam?id={id}&email=` | POST `/{uid}/not-spam?email=&folder=` |

> All paths are prefixed with `/api/{provider}/messages` (Gmail/IMAP) or `/api/outlook/` (Outlook's special routing). For IMAP, `{uid}` may be the list's `id` (`imap:<uid>`) as is; see section 2 for `folder`, which may be omitted for INBOX.

**Mark as junk / Not junk**: moves the message into the junk folder, or out of it back to the inbox. The server and the local cache change together, and the response is `result: {id, folder}`.
- Gmail swaps the `SPAM` / `INBOX` labels and keeps the `id`; Outlook and IMAP assign a new `id` after the move, so use the returned `id` for any later operation on this message. When the IMAP server lacks UIDPLUS the `id` is `null`; run `messages/fetch` on the destination folder before using the message again.
- If the IMAP account has no junk folder on the server, the call returns 409 `imap_spam_folder_not_found`. Tell the user as is; do not retry and do not substitute another folder.
- A message already in the destination folder returns success without moving. A message moved back to the inbox does not trigger mail rules or a new-mail notification.
- Not junk handles one message at a time; do not move a batch back to the inbox together. Mark as junk may be called once per message.
- Requires client 10.0.178 or later; older clients return 404, in which case ask the user to upgrade the client.

**Extra fields in message detail**: `body: {content, contentType}`, `ccRecipients`, `attachments: [{id, filename, contentType, size}]`. For IMAP, an attachment's `id` is its index within the message as a string (`"0"`, `"1"`, ...).

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

Each `attachments` item is `{filename, content (base64), contentType}`. Gmail requires at least one non-empty recipient. When an IMAP account's `smtpStatus` is `unverified` (receive-only), send, reply, and draft send all return 409 (`error: smtp_unverified`); guide the user to re-verify SMTP first.

**Reply to an email**:

| Provider | Endpoint | Body |
|----------|------|------|
| Gmail | POST `/gmail/reply` | `{email, messageId, body, contentType}` |
| Outlook | POST `/outlook/message/reply?id={id}&email=` | `{body, contentType}` |
| IMAP | POST `/imap/reply` | `{email, uid, folder, body, contentType}` (`uid` may be `imap:<uid>`; `folder` defaults to `INBOX`) |

### 5. Search (All Three Providers)

`GET /api/{p}/search?email={email}&q={keyword}` (`{p}` is `gmail`, `outlook`, or `imap`)

Search reads only the **local cache** and never contacts the mail server; if nothing is found, sync remotely per Rule 3 and search again.

| Parameter | Description |
|------|------|
| `q` | keyword, **matches the subject only** (case-insensitive) |
| `from` | sender address (substring match) |
| `dateFrom` / `dateTo` | date range YYYY-MM-DD (local time zone, both days inclusive) |
| `hasAttachment` | `true` returns only messages with attachments (`false` does not filter) |
| `isUnread` | `true` returns only unread messages (`false` does not filter) |
| `folder` | folder filter, same values as the local cache list |
| `offset` / `limit` | pagination, `limit` at most 200 |

Parameter names must match exactly; unknown parameters (e.g. `query`, `hasAttachments`) return 400. Returns `{messages, total, offset, limit}`.

To run a full-text search on the Gmail server by body or sender, use the `query` parameter of `POST /gmail/messages/fetch?email=` instead: it is passed straight to the Gmail API, supports Gmail search syntax (such as `from:` and `has:attachment`), and the results are also written to the local cache. Outlook and IMAP have no equivalent remote search parameter. If an older client returns 404 for `/outlook/search` or `/imap/search`, page through `GET /{p}/messages` and filter the results yourself.

### 6. Attachment Download

| Provider | Method | Endpoint | Body |
|----------|------|------|------|
| Gmail | POST | `/gmail/messages/{messageId}/attachment` | `{email, attachmentId}` |
| Outlook | POST | `/outlook/attachment` | `{email, messageId, attachmentId}` |
| IMAP | POST | `/imap/attachment` | `{email, messageId, attachmentId, folder?}` |

- `attachmentId` comes from `attachments[].id` in the message detail; call the detail endpoint first to get the attachment list.
- IMAP: use the list's `id` (e.g. `imap:12345`) as `messageId`; `attachmentId` is the attachment index as a string (the first attachment is `"0"`); `folder` is the real folder path on the server and may be omitted for INBOX.
- **Always pass `save_to` to `MailOperations` when downloading an attachment** (the target file path): the tool decodes the base64 in process and writes the file, returning only the absolute path, byte count, and SHA-256; without `save_to` the tool refuses to return the attachment response. The target path must be inside a writable working directory.
- The endpoint's raw response is `result: {data: <base64>, size}`; the tool refuses to parse responses larger than about 32 MB — in that case follow the streaming-to-disk method given in the tool's error message, or ask the user to export the attachment manually from the Emails page.

Example (IMAP):

```json
{
  "path": "/api/imap/attachment",
  "method": "POST",
  "body": {"email": "me@example.com", "messageId": "imap:12345", "attachmentId": "0"},
  "save_to": "./attachments/report.pdf"
}
```

> Gmail uses POST because the attachmentId may exceed URL length limits.

### 7. Draft Management

**Gmail**:

| Operation | Method | Endpoint |
|------|------|------|
| List drafts | GET | `/gmail/drafts?email=&limit=` |
| Get draft detail | GET | `/gmail/drafts/{draftId}?email=` |
| Create draft | POST | `/gmail/drafts` — body: `{email, to, cc, subject, body, contentType}` (`to` / `cc` are comma-separated address strings) |
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
| Create draft | POST | `/imap/drafts` — body: `{email, to, cc, subject, body, contentType}` (`to` / `cc` are comma-separated address strings, not a `toRecipients` array); returns `{uid, id}` |
| Update draft | PUT | `/imap/drafts/{uid}` — same body as create; it deletes the old draft and creates a new one, returning a **new** `{uid, id}` — use the new uid to send or delete afterwards (the old uid gets 404 `Draft not found`). If the server does not support UIDPLUS the returned uid is 0; re-read the draft list before the next operation |
| Delete draft | DELETE | `/imap/drafts/{uid}?email=` |
| Send draft | POST | `/imap/drafts/{uid}/send?email=` — `email` in the query string, no body needed |

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
| Get emails under a label | GET | `/labels/{labelId}/mails?provider=&email=&limit=&offset=` — returns `mailIds` (no message content) |

The unified label interface changes only DesireCore's local data and does not sync to the mail server. To change labels on the server, use the Gmail native labels below or the Outlook categories in section 9.

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

The regex operator is `matches_regex` (`regex` is treated as an unknown operator and never matches); `is_true` / `is_false` are only for `has_attachment`.

**Action types**:

| type | value | Description |
|------|-------|------|
| `add_label` | label ID | add a local label |
| `remove_label` | label ID | remove a local label |
| `mark_as_read` | omit | mark as read in the local cache only |
| `mark_as_unread` | omit | mark as unread in the local cache only |
| `delete` | omit | delete from the local cache only; the message on the server is untouched |
| `auto_reply` | reply text | auto-reply with fixed content |
| `agent_handle` | Agent ID | trigger an Agent to handle the email |

> Rules are **executed automatically** when the polling engine detects a new email; no manual call is required (for IMAP only new INBOX mail is covered). `auto_reply` and `agent_handle` support all three mailbox types; `agent_handle` binds the Agent Service connection that is current when the rule is created or updated. `archive`, `move_to_folder`, `forward_to`, and `star` can be saved but currently do nothing when executed; do not promise these effects to the user.

### 11. Authorization Management

| Operation | Method | Endpoint |
|------|------|------|
| Gmail OAuth | POST | `/gmail/auth/initiate?loginHint={email}` — returns `result.authUrl` for the user to open in a browser to authorize |
| Gmail status | GET | `/gmail/auth/status?email=` |
| Outlook OAuth | POST | `/outlook/auth/initiate` — returns `result.authUrl` for the user to open in a browser to authorize |
| Outlook status | GET | `/outlook/auth/status?email=` |

### 12. Folders

| Operation | Method | Endpoint |
|------|------|------|
| IMAP folder list | GET | `/imap/folders?email=` — returns `[{name, path, specialUse, flags}]`; use `path` as the `folder` of IMAP single-message operations |
| Outlook folder list | GET | `/outlook/folders?email=` |

> Gmail folders are fixed: inbox, sent, drafts, trash, spam, archive.

---

## Data Sync Mechanism

The email system uses **local cache + periodic polling**:

- **Write operations** (send, mark, delete, Gmail native labels, Outlook categories): the provider endpoints update local and remote simultaneously, no delay; the unified label interface (section 8) and the mark, delete, and label actions of auto-rules change local data only
- **Read operations** (query, search): return the local cache; may be delayed (default 30-second polling)
- **Remote changes** (the user operates from the official web UI): Gmail / Outlook wait for the next polling cycle to sync; IMAP polling only pulls new INBOX mail, other folders require an explicit `messages/fetch`, and read or delete changes made on the server to already-cached messages are not written back locally

**Storage path**: `${DESIRECORE_ROOT}/mail/{provider}/{email}/` (meta.json, index.json, messages/)

---

## Error Handling

| Status code | Reason | Handling |
|--------|------|------|
| 400 | parameter error (including a parameter in the wrong place, e.g. a query-string parameter put in the body) | check parameter names and locations against `msg` |
| 401 | Gmail/Outlook authorization expired, IMAP account not configured, or missing Mail Service capability | **handle per Rule 1**; do not try other channels |
| 404 | resource not found | sync first and retry (Rule 3) |
| 409 | IMAP account SMTP not verified (`error: smtp_unverified`) | guide the user to re-verify SMTP (`POST /imap/accounts/verify-smtp`) |
| 500 | internal error (common IMAP cause: `folder` is not a folder that exists on the server) | check `folder` first; if it still fails, tell the user to retry later |

**IMAP note**: domestic Chinese mailboxes (QQ, 163) require an "app password" instead of the login password. Use `/imap/test` to validate the configuration in advance and check `result.imap.success` and `result.smtp.success` in the response.
