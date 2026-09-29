# 离线队列 API

离线队列目前只能通过下列接口手动登记和处理：写操作失败时**不会**自动入队，网络恢复后也**不会**自动处理。`POST /offline/process` 执行时，`mark_as_read`、`mark_as_unread`、`delete`、`add_label`、`remove_label` 只修改本地缓存，不同步到邮件服务器；`send_email`、`archive`、`move_to_folder` 尚未实现。这些未实现的类型、以及缺少 `params.labelId` 的加/去标签操作，处理时什么都不做却照样出队并计入 `processed`——`processed` 的计数不代表操作真的执行了。不要把离线队列当作发信或同步远程的手段。

下表端点与主文档一样省略 `/api` 前缀，经 `MailOperations` 调用时需补上（`/ping` 除外）。

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取队列状态 | GET | `/offline/status` |
| 获取队列操作 | GET | `/offline/queue` |
| 添加操作到队列 | POST | `/offline/queue` — body: `{type, provider, email, mailId, params}`，`type` ∈ `mark_as_read, mark_as_unread, delete, move_to_folder, add_label, remove_label, send_email, archive` |
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
