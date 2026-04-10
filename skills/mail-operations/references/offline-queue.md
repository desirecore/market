# 离线队列 API

当网络不可用时，写操作会进入离线队列，恢复网络后自动处理。

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取队列状态 | GET | `/offline/status` |
| 获取队列操作 | GET | `/offline/queue` |
| 添加操作到队列 | POST | `/offline/queue` — body: `{type, provider, email, mailId, params}` |
| 移除单个操作 | DELETE | `/offline/queue/{operationId}` |
| 清空队列 | DELETE | `/offline/queue` |
| 清除失败操作 | DELETE | `/offline/failed` |
| 手动处理队列 | POST | `/offline/process` |

## 同步状态

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取同步状态 | GET | `/sync-status?provider=&email=` — 返回 idle/syncing/error |
| 获取轮询引擎状态 | GET | `/polling/status` — 所有账户轮询状态 |
| 健康检查 | GET | `/ping`（注意：路径不含 `/api` 前缀） |
