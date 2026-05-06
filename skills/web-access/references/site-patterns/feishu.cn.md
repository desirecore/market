---
domain: feishu.cn
aliases: [飞书, Lark, lark.com]
type: site-pattern
pinned: true
confidence: high
learned_at: '2026-05-05'
updated_at: '2026-05-05'
---

## L0
**强登录、强权限**站点；必须 L3 CDP 复用用户登录态；优先用飞书 OpenAPI。

## 平台特征
- 文档 / 多维表格 / 知识库：完全 SPA，未登录无法访问
- 权限模型严格：用户即使登录，也可能因企业空间隔离打不开他人文档
- OpenAPI 完整：`open.feishu.cn/open-apis/...`，企业可申请 access_token 获取大多数数据
- 国际版 `lark.com` 与国内版 `feishu.cn` 有不同的鉴权域

## 推荐流程
1. 公开文档（companion 页面/官方文档站点 `feishu.cn/hc/...`）→ WebFetch / Jina
2. 用户文档 → BrowserNavigate（已登录 Chrome）+ BrowserEval 抓正文
3. 长期程序化访问 → 申请 OpenAPI access_token，走 HTTP，避免 CDP

## 推荐选择器
- 文档标题：`.title-input` / `header [class*='title']`
- 富文本正文：`.lark-editor-render` / `[contenteditable] .ace-line`
- 评论：`.lark-comment` / `[class*='comment']`

## 已知陷阱
- ❌ 直接 WebFetch 用户文档 URL：返回登录占位 HTML
- ❌ 跨企业空间访问：即使登录也是 403，DOM 提示"无权限"
- ⚠️ Lark vs 飞书：URL 结构相似但 cookie 域不同，不能复用同一登录态

## 反爬细节
- session 强绑定 IP + 设备指纹，跨设备复用 cookie 会失效
- 自动化操作（高频 click/scroll）可能触发企业管理员告警

## 历史更新
- 2026-05-05：初版基线
