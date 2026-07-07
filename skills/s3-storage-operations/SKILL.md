---
name: s3-storage-operations
description: 操作 S3 兼容对象存储（上传、下载、列举、删除），通过 DesireCore HTTP API 调用。Use when 用户要求上传/下载/分享文件、需要生成下载链接、或工作流产出文件需要持久化存储与分发。
version: 2.0.4
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - storage
  - s3
  - upload
  - download
  - sharing
metadata:
  author: desirecore
  version: '2.0.1'
  updated_at: '2026-03-13'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 对象存储操作
      short_desc: 通过 DesireCore HTTP API 操作 S3 兼容对象存储，支持上传、下载、列举、删除与分享链接
      description: >-
        操作 S3 兼容对象存储（上传、下载、列举、删除），通过 DesireCore HTTP API 调用。Use when 用户要求上传/下载/分享文件、需要生成下载链接、或工作流产出文件需要持久化存储与分发。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:6ea8e1375f12de72
      translated_by: human
    en-US:
      name: Object Storage Operations
      short_desc: Operate S3-compatible object storage via DesireCore HTTP API — upload, download, list, delete, and share links
      description: >-
        Operate S3-compatible object storage (upload, download, list, delete) via the DesireCore HTTP API. Use when the user requests file upload/download/sharing, needs a download link, or when workflow outputs need persistent storage and distribution.
      body: ./SKILL.md
      source_hash: sha256:0182951808f5f831
      translated_by: human
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="s3so-a" x1="4" y1="3" x2="20"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#5AC8FA"/><stop
    offset="1" stop-color="#AF52DE"/></linearGradient></defs><ellipse cx="11"
    cy="5" rx="7" ry="2.75" fill="url(#s3so-a)" fill-opacity="0.14"
    stroke="url(#s3so-a)" stroke-width="1.5"/><path d="M4 5v5.5c0 1.52 3.13
    2.75 7 2.75s7-1.23 7-2.75V5" fill="url(#s3so-a)" fill-opacity="0.08"
    stroke="url(#s3so-a)" stroke-width="1.5"/><path d="M4 10.5V16c0 1.52 3.13
    2.75 7 2.75s7-1.23 7-2.75v-5.5" fill="url(#s3so-a)" fill-opacity="0.08"
    stroke="url(#s3so-a)" stroke-width="1.5"/><rect x="15.5" y="8.5" width="5"
    height="5" rx="1.4" fill="#34C759" fill-opacity="0.15" stroke="#34C759"
    stroke-width="1.4"/><path d="M18 7v10" stroke="#34C759" stroke-width="1.8"
    stroke-linecap="round"/><path d="M16.5 8.5 18 7l1.5 1.5" stroke="#34C759"
    stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path
    d="M16.5 15.5 18 17l1.5-1.5" stroke="#34C759" stroke-width="1.8"
    stroke-linecap="round" stroke-linejoin="round"/></svg>
  category: data
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# s3-storage-operations Skill

## L0: One-line Summary

Lets the Agent operate S3-compatible object storage through the DesireCore HTTP API — uploading, downloading, listing, and deleting files, and generating shareable download links.

## L1: Overview and Use Cases

### Capability Description

s3-storage-operations is a **Tool-Skill** that interacts with the user's pre-configured S3-compatible object storage (AWS S3, Qiniu Kodo, MinIO, etc.) via the DesireCore Agent Service HTTP API.

**Architecture change (v2.0)**: S3 operations have been migrated from a built-in tool to HTTP REST API endpoints, callable via curl from any environment. Claude Code's Global Skill (`desirecore-s3-storage`) contains the full curl invocation guide.

Core principle: the user's S3 connection is pre-configured under **Resources → Object Storage**. The API resolves the connection automatically — the Agent does not need to worry about connection details and can focus on the operation itself.

### Use Cases

- The user asks to "upload a file", "put it in storage", or "save to S3"
- The user asks for "a download link", "share this file", or "download from S3"
- The user asks to "see what's in storage" or "list files in the bucket"
- The user asks to "delete from S3" or "clean up temp files"
- A workflow produces files (reports, exports, images) that need to be shared via URL
- The Agent needs to read data stored in S3 for further processing

## L2: Detailed Specification

### Port Discovery

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
```

### API Endpoints

| Endpoint              | Method | Description                     |
| --------------------- | ------ | ------------------------------- |
| `/api/s3/connections` | GET    | List available connection summaries |
| `/api/s3/upload`      | POST   | Upload a file (multipart/form-data) |
| `/api/s3/download`    | GET    | Generate a download link or download a file |
| `/api/s3/list`        | GET    | List objects                    |
| `/api/s3/objects`     | DELETE | Delete an object                |

### Quick Reference

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)

# 列出连接
curl -k "https://127.0.0.1:${PORT}/api/s3/connections"

# 上传
curl -k -X POST "https://127.0.0.1:${PORT}/api/s3/upload" \
  -F "file=@local-file.pdf" -F "key=remote/path.pdf"

# 获取下载链接
curl -k "https://127.0.0.1:${PORT}/api/s3/download?key=remote/path.pdf"

# 列出对象
curl -k "https://127.0.0.1:${PORT}/api/s3/list?prefix=remote/"

# 删除
curl -k -X DELETE "https://127.0.0.1:${PORT}/api/s3/objects" \
  -H "Content-Type: application/json" -d '{"key":"remote/path.pdf"}'
```

### Connection Resolution

All API endpoints accept an optional `connection_id` parameter. When unspecified, the system resolves it automatically with the following priority:

```
Specified ID  →  isDefault=true  →  first status="connected"  →  first connection
```

### Error Handling

All errors return a unified format:

```json
{ "success": false, "error": "描述信息", "code": "ERROR_CODE" }
```

Error codes: `NO_CONNECTION` | `NOT_FOUND` | `UPLOAD_FAILED` | `DOWNLOAD_FAILED` | `DELETE_FAILED` | `LIST_FAILED` | `INVALID_REQUEST`

### Security Red Lines

| Rule                      | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| **No uploading sensitive files** | Never upload `.env`, credential files, private keys, etc. |
| **Confirm before deletion** | Always confirm intent with the user before calling the delete API |
| **Do not assume a connection exists** | When the API returns `NO_CONNECTION`, guide the user to add a connection in the UI |

### Integration Points

- **S3 Routes** — `lib/agent-service/routes/s3-routes.ts`: HTTP API implementation
- **S3 Client** — `lib/agent-service/s3-client.ts`: AWS V4 signing, CRUD operations
- **Connection Resolver** — `lib/agent-service/s3-connection-resolver.ts`: automatic connection selection
- **Global Skill Sync** — `lib/agent-service/global-skill-sync.ts`: writes the Global Skill on startup
- **Port Discovery** — `${DESIRECORE_ROOT}/agent-service.port`: port discovery file
