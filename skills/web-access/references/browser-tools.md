# 内置受管浏览器工具速查（L3-fast）

> v2.1 起，本层从「cdp-proxy 驱动用户自己的 Chrome」改为「DesireCore 内置受管浏览器」。
> 每个任务跑在独立 BrowserSpace 里（Cookie / Storage / 缓存互不串扰），每个动作都经过
> Capability → Grant → Lease → Origin → Host fencing 校验并留下可审计回执。
>
> 要求客户端 **v10.0.98+**。旧的 `BrowserListTabs` / `BrowserNavigate` / `BrowserEval` /
> `BrowserClick` / `BrowserScreenshot` / `BrowserScroll` / `BrowserSetFiles` /
> `BrowserCloseTab` 与其背后的 cdp-proxy 已停用，调用会直接返回
> 「该旧 BrowserXxx/cdp-proxy 入口已停用；请改用 BrowserManage、BrowserSnapshot 或 BrowserAct」。

## 何时用内置浏览器 vs Python Playwright

| 场景 | 推荐 |
|------|------|
| 到达并操作登录态站点（小红书 / B站 / 微博 / 飞书 / 知乎） | **内置浏览器**（登录态优先走 L3-fallback CDP；仅在已授予 `browser.import.*` 时才用 BrowserImport 导入 Cookie） |
| 抽取登录态站点的长正文 | Python Playwright（内置浏览器没有批量取文通道，见下） |
| 简单点击 / 滚动 / 截图 | **内置浏览器** |
| 多个任务要互不串扰地并行 | **内置浏览器**（一任务一 Space） |
| 需要复杂等待逻辑（wait_for_selector + race condition） | Python Playwright（cdp-browser.md） |
| 需要在浏览器内运行长时间脚本（>30 s） | Python Playwright（内置浏览器单条命令 30 s deadline） |
| 需要对元素做放大裁剪截图 | Python Playwright（内置浏览器只有整页截图） |

## 前置条件

1. 客户端 v10.0.98+，`~/.desirecore/config/browser.json` 里 `electron-embedded` 或
   `standalone-managed` Provider 处于 `enabled`（默认即开启）
2. 无需用户手工启动调试 Chrome，也无需 Python / Playwright

## 工具一览

每个工具默认 `hidden: true`，**只有 web-access 技能被激活后才暴露给 LLM**。

### BrowserManage

Space / Session / Tab 的生命周期。

```yaml
BrowserManage:
  action: create_space          # list_spaces | create_space | start_session | join_session
                                # | leave_session | list_sessions | list_tabs | create_tab
                                # | freeze_session | resume_session | close_session
  name: xhs-note                # create_space 用
  persistence: ephemeral        # ephemeral=查完即弃，不落 Profile；persistent=保留登录态
  providerPreference: [electron-embedded]
```

```yaml
BrowserManage:
  action: start_session
  spaceId: bsp_xxx
  capabilities:                 # 只申请你真正要用的，最小权限
    - browser.observe.tabs
    - browser.observe.snapshot
    - browser.observe.screenshot
    - browser.navigate.create-tab
    - browser.navigate.url
    - browser.navigate.activate-tab
    - browser.input.pointer.click
    - browser.input.pointer.wheel   # 要滚动加载就必须带上，漏了 input.wheel 会被策略拒绝
    - browser.input.keyboard
```

**显式传 `capabilities` 就是在做减法**：不传时按 `agentDefault` 全量签发租约，传了就只签这一份
列表。所以别照抄示例——把你这次真正要用的动作对应的能力都列全。

`create_space` 会触发一次用户确认。任务收尾用 `close_session` 释放。

### BrowserSnapshot

读页面的**主通道**。返回可交互元素及其 `ref` 句柄、`rect`、`disabled` 状态。

```yaml
BrowserSnapshot:
  mode: semantic        # semantic（默认）| accessibility | visual
  sessionId: bss_xxx    # 当前 Agent 有多个会话时用于消歧
  tabId: btab_xxx
```

提示：
- `semantic` 只列 button / input / a 等可交互元素，**不含图片和正文文本节点**
- 元素 `name` 往往是 placeholder（如「请输入」），无标签时只能靠 `rect.y` 排序定位
- 页面重排后旧 `ref` 会失效——**每次交互前重新取快照**
- `accessibility` 能拿到 StaticText 正文，但**只在很简单的页面上可用**：实测
  example.com 正常返回，维基百科条目一律 `BROWSER_RESULT_TOO_LARGE`（回执上限 2 MB），
  且 schema 里的 `depth` 参数目前被宿主忽略（硬编码 depth=50），调小也没用
- 因此**取真实页面正文仍要靠 L2 Jina Reader（公开页）或 L3-fallback Playwright（登录态）**

### BrowserAct

一次调用一个受管动作。完整 `action` 见工具 schema，常用的：

```yaml
BrowserAct:
  action: tab.navigate
  params: { url: https://www.xiaohongshu.com/explore/... }
```

```yaml
BrowserAct:
  action: input.click
  params: { ref: bref_xxx }     # 用快照 ref；坐标会因页面重排失效
```

```yaml
BrowserAct:
  action: input.text
  params: { text: 搜索关键词 }
```

```yaml
BrowserAct:
  action: input.wheel
  params: { deltaX: 0, deltaY: 720, x: 640, y: 400 }
```

```yaml
BrowserAct:
  action: tab.activate          # 截图前必须先做这一步
  params: { bounds: { x: 0, y: 0, width: 1280, height: 900 } }
```

```yaml
BrowserAct:
  action: page.screenshot
  params: { format: png }       # 结果落 artifact store，回执给 artifact.id / sha256 / bytes
```

### BrowserImport（**需人工审批 + 额外授权**）

把用户浏览器里的登录态 Cookie 导入当前 Space。

> **前置条件（先看这里，别直接试）**：`browser.import.discover` /
> `browser.import.cookies.inspect` / `browser.import.cookies` 三个能力**不在 `agentDefault` 里**，
> 而 `BrowserManage(create_space)` 建的 Agent grant 就是按 `agentDefault` 签的。也就是说
> **仅靠 create_space / start_session 走不通 BrowserImport**，必须由 Host/用户侧另行授予 import
> 能力（`agentElevated` 或 Workbench 路径）。没有这层授权就别在这条路上耗——**直接回落
> L3-fallback（Python Playwright 连用户已登录的 Chrome）**，那是当前更稳的登录态复用方式。

动作枚举只有这 6 个：`discover` | `create_plan` | `dry_run` | `apply` | `rollback` | `list_plans`
（**没有 `plan`**）。完整流程是 `discover → create_plan → dry_run → apply`：

```yaml
BrowserImport:
  action: discover              # 列出可导入的来源，返回不透明 sourceProfileId
```

```yaml
BrowserImport:
  action: create_plan           # 域名授权、来源、冲突策略都在这一步定死
  sourceKind: chromium-profile  # chromium-profile | firefox-profile | safari-profile
                                # | browser-extension | cookie-file
  sourceProfileId: <discover 返回的 ID>
  domains: [xiaohongshu.com]    # 必须逐域显式授权
  conflictStrategy: newer-wins  # keep-target | replace-target | newer-wins | fail-on-conflict
```

```yaml
BrowserImport:
  action: dry_run               # 先看命中多少条，再决定要不要真的写入
  planId: bimp_xxx              # create_plan 返回的 ID，前缀是 bimp_
```

```yaml
BrowserImport:
  action: apply                 # 只认 planId；域名/策略在 create_plan 时已固化
  planId: bimp_xxx
```

写坏了用 `action: rollback` + 同一个 `planId` 回退；`list_plans` 查当前 Space 的历史 plan。

解密与过滤全在 Host 侧完成，**Cookie 值不会进入 Agent 上下文或审计日志**。

### BrowserShare

把 Space / Session 委派给另一个 Agent，`shareMode` 可选 `snapshot`（只读副本）、
`copy-on-write`（写时复制）、`live-shared`（实时共享）、`handoff`（移交控制权）。

## 已知边界（照做，别试探）

| 边界 | 说明 |
|------|------|
| **截图前必须 `tab.activate`** | 标签页默认停在 `(-10000,-10000,1x1)`，没有合成表面。直接截图会卡满 30 s deadline，**并把标签页宿主打掉**，之后全部报 `BROWSER_TAB_HOST_NOT_FOUND` |
| **同时只有一个可见标签页** | `tab.activate` 绑定主窗口、全局互斥。多 Space 可以并发导航/快照/输入，但截图必须逐个 activate 串行 |
| **`page.evaluate` 基本不可用** | 每次调用需人工审批；返回的字符串/对象被替换为 `[REDACTED:browser-runtime-value]`（只有 number/boolean/null 穿透）；反调试站点会把它挂起几十秒。读页面用 `BrowserSnapshot` |
| **`cdp.raw` 需人工审批** | `browser.raw_cdp.*` 属于永远人工闸门的能力，无人值守流程用不了（元素级裁剪截图因此不可用） |
| **没有批量取文通道** | `semantic` 不含正文，`accessibility` 在真实页面上超限，`page.evaluate` 被审批+脱敏。要正文请回落 Jina / Playwright |
| **单条命令 30 s deadline** | 超时即判 `browser.host.gone`，会话作废 |
| **用户真实鼠标会抢控制权** | 鼠标划过可见标签页会触发 `trusted-user-input` 并递增 control epoch，可能打断 Agent 的租约 |
| **artifact 不要走 `/save`** | 该接口会弹系统「另存为」对话框等人点。artifact 文件在 `${DESIRECORE_ROOT}/browser/artifacts/<bart_id>/`，直接读即可，默认保留 24 小时 |

## SitePatternRead / SitePatternWrite

参见 SKILL.md 的"站点经验积累"章节。任务结束如果发现新陷阱、新选择器，调用：

```yaml
SitePatternWrite:
  domain: xiaohongshu.com
  scope: agent           # agent=共享（受 Git 管理，可发布）；user=私有
  mode: merge            # 默认 merge 追加；replace 覆盖
  content: |
    ## 已知陷阱
    - 2026-08: ...
```

含 cookie/token/手机号/邮箱时会自动降级 scope='user'。

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `该旧 BrowserXxx/cdp-proxy 入口已停用` | 还在调 v2.0 的旧工具 | 改用 BrowserManage / BrowserSnapshot / BrowserAct |
| `BROWSER_TAB_HOST_NOT_FOUND` | 标签页宿主已销毁（多因上一条命令超时） | 重建 Session；检查是否漏了 `tab.activate` |
| `BROWSER_COMMAND_DEADLINE_EXCEEDED` | 单条命令超 30 s | 截图先 activate；避免 `page.evaluate` |
| `BROWSER_TOOL_SESSION_FORBIDDEN` | 会话已关闭/崩溃，或不属于当前 Agent | 重新 `list_sessions`，必要时重建 |
| `BROWSER_TOOL_SESSION_AMBIGUOUS` | 当前 Agent 有多个会话且未传 sessionId | 显式传 `sessionId` |
| `BROWSER_HUMAN_APPROVAL_REQUIRED` | 触到人工闸门能力（evaluate / raw_cdp / 上传下载 / Cookie 导入等） | 向用户说明用途并等待审批，或换用无需审批的路径 |
| `BROWSER_RESULT_TOO_LARGE` | 回执超过 2 MB（`accessibility` 快照最常见） | 改用 `semantic` 快照 + 截图；取正文回落 Jina / Playwright |

## 调用链路

```
Agent → BrowserManage/Snapshot/Act → browser-use service（Capability/Grant/Lease/Policy 校验）
      → BrowserHost（electron-embedded 或 standalone-managed）→ Chromium
                                    ↑ 每步产出带 digest 的回执，写入审计事件流
```
