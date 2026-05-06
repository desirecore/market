---
domain: bilibili.com
aliases: [B站, 哔哩哔哩, 小破站]
type: site-pattern
pinned: true
confidence: medium
learned_at: '2026-05-05'
updated_at: '2026-05-05'
---

## L0
公开主页可 WebFetch；视频详情 / 评论 / 长简介 / 收藏夹建议 L3 CDP。

## 平台特征
- 视频页：基础信息（标题、UP 主、播放数）公开 SSR；完整描述 / 弹幕 / 评论需 JS 渲染或登录
- 列表页（首页 / 分区）：大部分公开，可走 WebFetch + Jina
- API：`api.bilibili.com/x/...` 部分接口公开，可 curl 直接拉数据

## 推荐流程
- 仅取标题/UP 主/播放数 → WebFetch 即可
- 取完整简介 / 评论 → BrowserNavigate + BrowserEval
- 批量数据 → 优先尝试 `api.bilibili.com` 公开接口（有专门的 wbi 签名机制）

## 推荐选择器
- 视频标题：`h1.video-title` 或 `[class*='video-title']`
- UP 主：`a.up-name` / `.up-detail-top a`
- 视频简介：`.video-desc` / `[class*='desc-info']`
- 评论：`.reply-item .content`
- 弹幕：通过 `api.bilibili.com/x/v1/dm/list.so` 拉 XML

## 已知陷阱
- ❌ headless 抓详情：部分元素只在 viewport 内才渲染（懒加载）
- ❌ 用户主页评论：必须登录
- ⚠️ 直接 fetch `api.bilibili.com` 高频接口（如 `wbi/...`）需要 wbi 签名，否则返回 -403

## 反爬细节
- 视频 BV 号 ↔ AV 号：可通过本地工具或 `api.bilibili.com/x/web-interface/view?bvid=...` 互转
- 弹幕 `oid`（cid）需先从视频元数据接口拿到

## 历史更新
- 2026-05-05：初版基线，待实际验证调整
