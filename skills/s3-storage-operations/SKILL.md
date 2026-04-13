---
name: 对象存储操作
description: 操作 S3 兼容对象存储（上传、下载、列举、删除），通过 DesireCore HTTP API 调用。Use when 用户要求上传/下载/分享文件、需要生成下载链接、或工作流产出文件需要持久化存储与分发。
version: 2.0.1
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: false
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
  short_desc: 通过 DesireCore HTTP API 操作 S3 兼容对象存储，支持上传、下载、列举、删除与分享链接
  category: data
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# s3-storage-operations 技能

## L0：一句话摘要

让 Agent 通过 DesireCore HTTP API 操作 S3 兼容对象存储，实现文件上传/下载/列举/删除并生成可分享的下载链接。

## L1：概述与使用场景

### 能力描述

s3-storage-operations 是一个**工具技能（Tool-Skill）**，通过 DesireCore Agent Service 的 HTTP API 与用户预配置的 S3 兼容对象存储（AWS S3、七牛云 Kodo、MinIO 等）交互。

**架构变更（v2.0）**：S3 操作已从内置工具迁移为 HTTP REST API 端点，可通过 curl 从任意环境调用。Claude Code 的 Global Skill（`desirecore-s3-storage`）包含完整的 curl 调用指南。

核心原则：用户的 S3 连接已在 **资源 → 对象存储** 中预配置。API 自动解析连接——Agent 无需关心连接细节，专注于操作本身。

### 使用场景

- 用户要求「上传文件」、「放到存储里」、「保存到 S3」
- 用户要求「给我个下载链接」、「分享这个文件」、「从 S3 下载」
- 用户要求「看看存储里有什么」、「列出桶里的文件」
- 用户要求「从 S3 删除」、「清理临时文件」
- 工作流产出文件（报告、导出、图片）需要通过 URL 分享
- Agent 需要读取存储在 S3 中的数据进行处理

## L2：详细规范

### 端口发现

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
```

### API 端点

| 端点                  | 方法   | 说明                            |
| --------------------- | ------ | ------------------------------- |
| `/api/s3/connections` | GET    | 列出可用连接摘要                |
| `/api/s3/upload`      | POST   | 上传文件（multipart/form-data） |
| `/api/s3/download`    | GET    | 生成下载链接或下载文件          |
| `/api/s3/list`        | GET    | 列出对象                        |
| `/api/s3/objects`     | DELETE | 删除对象                        |

### 快速参考

```bash
PORT=$(cat ~/.desirecore/agent-service.port)

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

### 连接解析机制

所有 API 端点均接受可选 `connection_id` 参数。未指定时，系统按以下优先级自动解析：

```
指定 ID  →  isDefault=true  →  第一个 status="connected"  →  第一个连接
```

### 错误处理

所有错误返回统一格式：

```json
{ "success": false, "error": "描述信息", "code": "ERROR_CODE" }
```

错误代码：`NO_CONNECTION` | `NOT_FOUND` | `UPLOAD_FAILED` | `DOWNLOAD_FAILED` | `DELETE_FAILED` | `LIST_FAILED` | `INVALID_REQUEST`

### 安全红线

| 规则                 | 说明                                                  |
| -------------------- | ----------------------------------------------------- |
| **禁止上传敏感文件** | `.env`、凭证文件、私钥等绝不上传                      |
| **删除前必须确认**   | 调用删除 API 前应与用户确认意图                       |
| **不假设连接存在**   | API 返回 `NO_CONNECTION` 时，引导用户在界面中添加连接 |

### 集成点

- **S3 Routes** — `lib/agent-service/routes/s3-routes.ts`: HTTP API 实现
- **S3 Client** — `lib/agent-service/s3-client.ts`: AWS V4 签名，CRUD 操作
- **Connection Resolver** — `lib/agent-service/s3-connection-resolver.ts`: 自动选择连接
- **Global Skill Sync** — `lib/agent-service/global-skill-sync.ts`: 启动时写入 Global Skill
- **Port Discovery** — `~/.desirecore/agent-service.port`: 端口发现文件
