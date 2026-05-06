---
domain: xiaohongshu.com
aliases: [小红书, 红薯, xhs, RED]
type: site-pattern
pinned: true
confidence: high
learned_at: '2026-05-05'
updated_at: '2026-05-05'
---

## L0
强登录站点，必须走 L3 CDP；笔记详情 `.note-content`，列表卡片 `.note-card`；URL 必带 `xsec_token`。

## 平台特征
- 强制登录：未登录会跳转登录墙，DOM 中没有正文
- 富 SPA：路由全靠 JS，WebFetch 拿到的 HTML 几乎是空壳
- 反爬严格：短时间多次请求会触发风控（验证码 / 限流）
- xsec_token：详情页 URL 包含 `xsec_token=...`，**通过站内交互生成**——直接拼 URL 容易失败

## 推荐流程
1. 通过 BrowserListTabs 找到已登录的 xhs tab；如无，BrowserNavigate 打开
2. BrowserEval 注入选择器抓取标题与正文
3. 列表页用 `[...document.querySelectorAll('.note-card a')].map(a => a.href)` 收集详情页链接
4. 单条笔记结尾调用 `BrowserCloseTab` 释放 tab，避免 tab 池溢出

## 推荐选择器
- 笔记标题：`#detail-title` 或 `h1[class*="title"]`
- 笔记正文：`#detail-desc` 或 `.note-content`
- 评论区：`.comments-container .comment-item`
- 列表卡：`.note-card`，链接 `.note-card a.cover`

## 已知陷阱
- ❌ 直接 WebFetch 笔记 URL：返回登录墙 HTML，解析无效
- ❌ Headless 模式访问：丢失登录态，触发风控
- ❌ 高频抓取：>30 req/min 易触发验证码

## 反爬细节
- xsec_token 由前端生成，与会话/路由绑定，不能跨 tab 复用太久
- User-Agent 检查较弱，但 navigator.webdriver 必须为 false（cdp-proxy 已默认绕过）
- click 操作建议优先用 `mode='real-mouse'`（CDP 真实鼠标事件），避免被 .click() 检测

## 速率限制
- 自评：单 IP 每分钟 ≤ 30 个详情页请求；超过会出验证码
- 风控触发后：等 5-10 分钟自然解除；同账号短期内反复触发可能短封

## 历史更新
- 2026-05-05：初版基线（基于公开经验整理，待 Agent 实际验证升级 confidence）
