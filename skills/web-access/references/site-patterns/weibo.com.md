---
domain: weibo.com
aliases: [微博, 围脖]
type: site-pattern
pinned: true
confidence: medium
learned_at: '2026-05-05'
updated_at: '2026-05-05'
---

## L0
长微博 / 视频微博 / 用户主页几乎都需登录；走 L3 CDP；移动版 m.weibo.cn 部分公开。

## 平台特征
- 桌面版（weibo.com）：未登录跳登录墙
- 移动版（m.weibo.cn）：列表与单条详情有时可匿名访问，且 DOM 简洁
- 长微博：触发"展开全文"按钮后才渲染完整内容

## 推荐流程
1. 单条公开微博 → 优先尝试 `https://m.weibo.cn/status/<id>`，WebFetch 看是否拿到正文
2. 拿不到 → BrowserNavigate（已登录态 Chrome）+ BrowserClick 点"展开" + BrowserEval 取正文
3. 用户主页时间线：必须登录，BrowserScroll 触发懒加载

## 推荐选择器
- 单条详情：`.weibo-text` / `[class*='WB_text']`
- 展开全文按钮：`a:has-text("展开全文")` 或 `.toggle-full`
- 时间戳：`a[class*='time']`
- 转发链：`.weibo-og`（被转发的原文）

## 已知陷阱
- ❌ 桌面版未登录抓取：HTML 几乎是空壳
- ❌ JS 关闭：m.weibo.cn 仍依赖 JS 渲染长内容
- ⚠️ 视频微博：流地址有 referer / token 校验，直接 yt-dlp 可能失败

## 反爬细节
- 桌面 weibo.com 严格检查 cookies 中的 SUB / SUBP；过期立即跳转登录
- 短时间高频访问会触发"小黑屋"——账号被禁登录

## 历史更新
- 2026-05-05：初版基线
