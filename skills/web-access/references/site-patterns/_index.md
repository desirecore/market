# 站点经验基线索引

本目录是 web-access 技能内置的"全局基线 site-pattern"——所有 Agent 默认能读到，但**写入时请用 `SitePatternWrite(scope='agent')`** 落到 Agent 共享层（`agents/<id>/memory/site-patterns/`），不要直接修改本目录。

读取顺序（最先命中即返回）：

1. **用户私有**：`users/<userId>/agents/<agentId>/memory/site-patterns/<domain>.md`
2. **Agent 共享**：`agents/<agentId>/memory/site-patterns/<domain>.md`（受 Git 管理，可发布）
3. **全局基线**：本目录（只读，跟随 web-access 技能版本发布）

## 已知站点

| Domain | 别名 | 推荐路径 |
|--------|------|---------|
| `xiaohongshu.com` | 小红书 / 红薯 / xhs | L3 CDP（强制登录） |
| `bilibili.com` | B站 / 哔哩哔哩 | L3 CDP（视频描述、评论需登录） |
| `weibo.com` | 微博 | L3 CDP（长微博需登录） |
| `zhihu.com` | 知乎 | L3 CDP（长文 + 评论需登录） |
| `feishu.cn` | 飞书 / Lark | L3 CDP（必须登录） |

后续 Agent 自学积累的新站点会落在 `agents/<id>/memory/site-patterns/`，对所有 Agent 用户可见。
