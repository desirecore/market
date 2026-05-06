---
domain: zhihu.com
aliases: [知乎]
type: site-pattern
pinned: true
confidence: medium
learned_at: '2026-05-05'
updated_at: '2026-05-05'
---

## L0
专栏文章公开可 WebFetch；问答详情、评论、回答列表建议 L3 CDP。

## 平台特征
- 文章 `zhuanlan.zhihu.com/p/<id>`：通常完全公开，WebFetch 即可
- 问答 `zhihu.com/question/<qid>`：未登录可看部分回答；完整内容、评论、点赞数需登录
- 移动 web `m.zhihu.com`：约束更松，对匿名相对友好

## 推荐流程
1. 专栏文章 → WebFetch / Jina Reader 优先
2. 问答详情 → BrowserNavigate + BrowserEval；批量回答用 `[...document.querySelectorAll('.AnswerItem')].map(...)`
3. 评论 → 必须登录，BrowserClick 展开，BrowserScroll 加载更多

## 推荐选择器
- 文章标题：`h1.Post-Title` / `h1[class*='Title']`
- 文章正文：`div.Post-RichText` / `[class*='RichText']`
- 回答列表：`.AnswerItem` / `[class*='AnswerItem']`
- 单条回答：`.RichContent-inner`
- 评论：`.CommentItemV2 .CommentRichText`

## 已知陷阱
- ❌ 直接 WebFetch 问答详情：只看到登录引导
- ⚠️ 长回答有"展开"按钮，触发前 DOM 不完整
- ⚠️ 知乎付费内容（盐选）即使登录也需会员

## 反爬细节
- d_c0、z_c0 等 cookie 决定登录态
- 风控：异常 UA / 短时高频 → 触发滑动验证码

## 历史更新
- 2026-05-05：初版基线
