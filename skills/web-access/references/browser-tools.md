# 内置受管浏览器工具速查（L3）

> v2.1 起本层从「cdp-proxy 驱动用户自己的 Chrome」改为「DesireCore 内置受管浏览器」；v3.0 补全能力面（批量取文 / 元素操作 / 等待 / 代码模式）并移除 Python Playwright 回落。
> 每个任务跑在独立 BrowserSpace 里（Cookie / Storage / 缓存互不串扰），每个动作都经过
> Capability → Grant → Lease → Origin → Host fencing 校验并留下可审计回执。
>
> 要求客户端 **v10.0.98+**。`page.extract-text` / `page.element` / `page.wait` / 内联 wait 块 /
> 跨源 iframe 快照需 **v10.0.112+**；`BrowserScript` 需包含 S17/S18 的版本。旧的
> `BrowserListTabs` / `BrowserNavigate` / `BrowserEval` / `BrowserClick` / `BrowserScreenshot` /
> `BrowserScroll` / `BrowserSetFiles` / `BrowserCloseTab` 与其背后的 cdp-proxy 已停用，调用会直接返回
> 「该旧 BrowserXxx/cdp-proxy 入口已停用；请改用 BrowserManage、BrowserSnapshot 或 BrowserAct」。

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

读页面的**主通道**。四种 mode：

```yaml
BrowserSnapshot:
  mode: semantic        # semantic（默认）| text | accessibility | visual
  sessionId: bss_xxx    # 当前 Agent 有多个会话时用于消歧
  tabId: btab_xxx       # 非活动标签页时用于消歧
  options: {...}        # 各 mode 专属参数，见下
```

**semantic** —— 可交互元素清单（button / input / a 等）+ `ref` 句柄。每行形如
`[ref=e12] [loc=...] 按钮 提交`：
- `loc=` 是该元素的稳定选择器（S7）：仅当能产出时才给出，五级优先级 data-testid →
  唯一 CSS 安全 id → name 属性 → 链接 href（剥 query 前缀匹配）→ role+name
- 跨源 iframe（OOPIF）的元素并入同一棵树，ref 全局连续编号（S35）
- 页面重排后旧 `ref` 会失效——**每次交互前重新取快照**；带 ref 的命令要同时给签发该
  ref 的快照 `snapshotId`
- `options`：`scope`（viewport=视口内元素优先截断）、`maxElements`（默认 400 上限 2000）、
  `maxBytes`（默认 256KB 上限 1MB）、`cursor` 翻页、`limit`

**text** —— 正文批量取文通道之一（S3/S4）：
```yaml
BrowserSnapshot:
  mode: text
  options:
    format: markdown       # markdown（默认，保留标题/列表/表格）| text（纯文本）
    maxBytes: 65536        # 默认 65536，最大 524288；超出不报错，截断并返回 nextCursor
    cursor: t1:...:...     # 上一页返回的 nextCursor，同参数续读
    scope: full_page       # full_page（默认）| viewport | ref（配 ref + snapshotId 取子树）
    includeLinks: true     # 链接目标写进正文（只写 http/https）
    includeTables: true    # 表格保留逐行结构
```

**accessibility** —— AX 树（S8 起**尊重 `depth`、预算截断不炸**）：
`options.depth`（默认 50 上限 100）、`maxElements`、`maxBytes`、`cursor`。真实内容页不再
`BROWSER_RESULT_TOO_LARGE` 整体失败——超预算截断给 nextCursor 续读。

**visual** —— 截图（像素直接进结果）：
`options.format`（png/jpeg）、`quality`、`captureBeyondViewport`（整页）、
`clip={x,y,width,height,scale}`（元素级裁剪放大，`scale` 最大 4）。

### BrowserAct

一次调用一个受管动作。`action` 分组：

**tab.*** —— `navigate` / `back` / `forward` / `reload` / `activate` / `close`：

```yaml
BrowserAct:
  action: tab.navigate
  params: { url: https://www.xiaohongshu.com/explore/... }
```

**input.*** —— `move` / `click` / `double-click` / `drag` / `wheel` / `touch` / `pinch` /
`key` / `text`。走 #1808 输入拟真（坐标派发、拟真轨迹、身份一致性），**反检测站点的交互首选**：

```yaml
BrowserAct:
  action: input.click
  params:
    ref: e12                    # 语义快照签发的短号 ref（不要裸 x/y）
    snapshotId: snap-xxx        # 签发该 ref 的快照回执里的 snapshotId，必带
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

带元素 ref 的 `input.*` 必须在 params 顶层同时带同一条快照回执的 `snapshotId`——ref 序号跨
快照会重复，缺 snapshotId 一律拒绝执行。

**page.element** —— 判别式元素命令（op × selector，九 op，S10）。**表单批量填充等站点
不检测场景用**；反检测站点交互走 input.*：

```yaml
BrowserAct:
  action: page.element
  params:
    op: fill                  # 写类：fill | select-option | check | uncheck | scroll-into-view
                              # 读类：get-attribute | bounding-box | count | all-inner-texts
    selector: loc=css:input#email   # loc= 方言或 e12 / ref=e12（配 snapshotId）
    value: user@example.com   # fill / select-option 用
    snapshotId: bsnp_xxx      # selector 用 ref 时必带
```

- 写类走 `browser.input.keyboard` 能力档（与 input.text 同档）；读类走 `browser.observe.snapshot` 只读档
- `fill` 对 `input[type=password]` **一律拒绝**
- `selector` 方言：`e<序号>` / `ref=e<序号>`、`loc=css:` / `loc=role:` / `loc=text:` /
  `loc=testid:`、裸 CSS，可叠 `internal:nth/last/scope/filter`。未知前缀（如 `loc=xpath:`）显式报错，绝不静默降级

**page.wait** —— 判别式等待（until，九种，S11）。等待不改页面状态，走只读档：

```yaml
BrowserAct:
  action: page.wait
  params:
    until: networkidle        # load | domcontentloaded | networkidle | selector | url | timeout
                              # | request | response | download
    timeoutMs: 10000          # 默认 10000，上限 60000
    idleMs: 500               # networkidle 静默窗，默认 500
```

- 轮询型（load/domcontentloaded/networkidle/selector/url/timeout）超时返回 `waited: false`，不抛错
- 事件型（request/response/download）超时**抛错**
- `waitForFunction` 刻意不在枚举里——任意 JS 走 page.evaluate 的能力档与审批

**内联 wait 块**（S14）—— `tab.navigate` / `input.click` / `input.key` / `page.element{op:"fill"}`
支持 `params.wait`（形态与 page.wait 参数同构），一条回执完成「动作→等结果」，等待器先于动作注册，
不跨两次 IPC 出竞态：

```yaml
BrowserAct:
  action: tab.navigate
  params:
    url: https://example.com/login
    wait: { until: networkidle, timeoutMs: 15000 }
```

**page.evaluate** —— 页面上下文求值（S2 起返回真实值）：

```yaml
BrowserAct:
  action: page.evaluate
  params:
    expression: document.title
    awaitPromise: true        # 默认 true
```

- 返回值**原样过界**（字符串/对象/数组都真实返回）；超预算截断并标 `truncated`，不抛错
- 能力档 `browser.page.evaluate` 属人工闸门：非 allow-all 模式每次调用弹审批卡
- 登录态取站内接口走 [fetch.browser 配方]（见下节）

**page.extract-text** —— 与 `BrowserSnapshot mode:text` 同款取文通道，作为动作下发：
scope（viewport/full_page/ref）+ ref + snapshotId、format（markdown/text）、maxBytes（默认
65536 最大 524288）、cursor（`^t1:` 续读）、includeLinks、includeTables。超出预算截断 + nextCursor。

**page.screenshot** —— 与 `BrowserSnapshot mode:visual` 同款：`format`、`quality`、
`captureBeyondViewport`、`clip={x,y,width,height,scale}`。结果落 artifact store，回执给
artifact.id / sha256 / bytes；截图像素直接进结果（见「截图」节）。

### BrowserScript（代码模式，S17+S18）

一段异步 JS 在 Worker 里跑，通过注入的 `page` / `tab` / `input` / `snapshot` / `console` /
`performance` 门面连续下发命令——**导航→快照→点击→等待→取文一气呵成**，消除逐动作往返：

```yaml
BrowserScript:
  code: |
    const snap = await snapshot.semantic();
    receipt.log(snap.content);
    await input.click({ ref: 'e12', snapshotId: snap.snapshotId });
    await page.wait({ until: 'networkidle' });
    receipt.log(await page['extract-text']({ format: 'markdown' }));
  sessionId: bss_xxx          # 可选，多会话消歧
  tabId: btab_xxx             # 可选，缺省用会话活动 tab
  totalBudgetMs: 180000       # 默认 180000，上限 600000；审批等待不计入
  maxCommands: 500            # 每次运行命令条数上限
```

- ❗**信任级别等同 Bash**：Worker 不是沙箱，脚本可访问 Node fs/net/child_process。两层审批：
  脚本源码先过一次与 Bash 同档的人类审批（allow-all / ask-external 豁免；脚本源码不可记忆），
  其内每个受管浏览器能力再按「能力 × 本次运行」各问一次
- helper 白名单 24 个：`snapshot.*` / `page.extract-text` / `tab.*` / `input.*` /
  `page.evaluate` / `page.wait` / `page.element` / `console.read` / `performance.metrics`；
  `console.log(page)` 可输出各 helper 的 signature/params/example 文档
- 会话被用户接管、Lease 轮换 ⇒ **硬停**：后续命令一律不再下发
- 需要 `browser.*` 相应能力；`receipt.log(...)` 或 `console.log` 输出文本

### BrowserImport（**需人工审批 + 额外授权**）

把用户浏览器里的登录态 Cookie 导入当前 Space——**唯一的登录态复用通道**。

> **前置条件（先看这里，别直接试）**：`browser.import.discover` /
> `browser.import.cookies.inspect` / `browser.import.cookies` 三个能力**不在 `agentDefault` 里**，
> 而 `BrowserManage(create_space)` 建的 Agent grant 就是按 `agentDefault` 签的。也就是说
> **仅靠 create_space / start_session 走不通 BrowserImport**，必须由 Host/用户侧另行授予 import
> 能力（`agentElevated` 或 Workbench 路径）。没有这层授权就别在这条路上耗——如实告诉用户
> 「当前无法复用你的登录态」，按无登录态继续或放弃。

动作枚举只有这 6 个：`discover` | `create_plan` | `dry_run` | `apply` | `rollback` | `list_plans`
（**没有 `plan`**）。完整流程是 `discover → create_plan → dry_run → apply`：

```yaml
BrowserImport:
  action: create_plan           # 域名授权、来源、冲突策略都在这一步定死
  sourceKind: chromium-profile  # chromium-profile | firefox-profile | safari-profile
                                # | browser-extension | cookie-file
  sourceProfileId: <discover 返回的 ID>
  domains: [xiaohongshu.com]    # 必须逐域显式授权
  conflictStrategy: newer-wins  # keep-target | replace-target | newer-wins | fail-on-conflict
```

`dry_run` 先看命中多少条再 `apply`（只认 `create_plan` 返回的 `planId`，前缀 `bimp_`）；写坏了
用 `rollback` + 同一个 planId 回退；`list_plans` 查历史。解密与过滤全在 Host 侧完成，
**Cookie 值不会进入 Agent 上下文或审计日志**。

### BrowserShare

把 Space / Session 委派给另一个 Agent，`shareMode` 可选 `snapshot`（只读副本）、
`copy-on-write`（写时复制）、`live-shared`（实时共享）、`handoff`（移交控制权）。

## fetch.browser 配方：带登录态取接口数据

站内接口（列表、评论、订单等 JSON）在登录态下的正解——**页面上下文跑 `fetch`**，自动带该
origin 的 Cookie，同 origin、受 Grant origins 约束，走 `page.evaluate` 已有闸门：

```yaml
BrowserAct:
  action: page.evaluate
  params:
    expression: |
      fetch('/api/v1/comments?page=1&size=20', {
        headers: { accept: 'application/json' }
      }).then(r => r.text())
    awaitPromise: true
```

- 先 `tab.navigate` 到该站任意页面建立 origin 与 Cookie，再发 fetch；路径写**相对路径**
- 只能访问当前 tab origin；跨站接口先导航过去
- 大 JSON 用 `.text()` 拿原文自己截取，或分页多次取
- 非 allow-all 模式会弹审批卡（page.evaluate 人工闸门），向用户说明用途即可

## 交互通道选用：input.* vs page.element（反检测决策）

| 场景 | 用什么 | 原因 |
|------|--------|------|
| 反检测站点（小红书/微博/B站等）的一切点击/输入 | **`input.*`** | 坐标派发 + #1808 拟真轨迹 + 身份一致性（UA/UA-CH 无 Electron/Headless 痕迹） |
| 表单批量填充等**站点不检测**的场景 | **`page.element` 写类** | 一条命令完成 fill/select-option/check，比逐元素 input.* 快得多 |
| 需要元素属性/坐标/计数/批量文本 | `page.element` 读类 | 只读档（browser.observe.snapshot），无写审批 |
| 任何「用 JS 直调 el.click()」的想法 | ❌ 禁止 | 绕开全部拟真投入（S10 红线）；指针动作只走 input.* |

## 截图：像素直接给你，通常不需要再 Read

`BrowserSnapshot mode:visual` 与 `BrowserAct page.screenshot` 会把截图像素作为 image 块
**直接放进工具结果**——视觉模型当场就能看，不必再调 `Read`。

- **元素级裁剪放大**：`options.clip={x,y,width,height,scale}`（`scale` 最大 4）。先用
  `semantic` 快照拿到元素坐标，再截那一块并放大——验证码、小按钮在整页截图里只有几十像素，
  看不清时用它。**不必走 `cdp.raw`**
- **整页截图**：`captureBeyondViewport: true`（超出视口部分也截）
- 只有结果里明确写了「截图已保存，但…未附带像素」（超预算/体积过大）或需要原始分辨率时，
  才走 `result.artifact.absolutePath` 再 `Read` 一次

当前模型不支持视觉输入时，结果会明说「你看不到它的内容」——**此时不要凭空描述画面**，
改用 `semantic` / `text` 快照拿页面信息。

## 视口与 tab.activate（S36 起）

Agent 会话（actor ≠ user）的标签页**常驻离屏原位，保住合成表面**，不再停放成 1×1：

| 场景 | 行为 |
|------|------|
| embedded，单标签会话 | 无需 `tab.activate` 即可截图/取视口（presentation 即呈现） |
| embedded，多标签会话的后台 tab | 仍需先 `tab.activate`；未激活的视口快判**秒级**报 `BROWSER_VIEWPORT_UNAVAILABLE`，不再挂满 30s，也不会毁掉标签页 |
| standalone | 后台 tab 可直接截图 |

多 Space 依然可以并发导航/快照/输入，互不串扰。

## 已知边界（照做，别试探）

| 边界 | 说明 |
|------|------|
| **`page.evaluate` 走人工闸门** | 能力 `browser.page.evaluate` 属 always-human-gate：非 allow-all 模式每次弹审批卡。返回值已原样过界（超预算截断标 `truncated`），登录态取接口走 fetch.browser 配方 |
| **`cdp.raw` 需人工审批** | `browser.raw_cdp.*` 属于永远人工闸门的能力，无人值守流程用不了。元素级裁剪 / 整页截图用 `clip` / `captureBeyondViewport`，别走它 |
| **`page.element` 没有 click** | 指针动作必须走 `input.*`（拟真轨迹、可审计）；JS 直调 `el.click()` 是明确禁止的回退 |
| **`fill` 拒绝密码框** | `input[type=password]` 一律拒绝——密码输入只走 `input.text`（拟真键入） |
| **单条命令 30 s deadline** | 超时只掐掉**这一条命令**（stop 加载），标签页仍可用，重试即可；不再打掉宿主。等待类命令超时连 stop 都跳过 |
| **多标签后台 tab 先 activate** | embedded 多标签会话里后台 tab 截图前先 `tab.activate`，否则秒级 `BROWSER_VIEWPORT_UNAVAILABLE` |
| **用户真实操作会抢控制权** | 在可见标签页上**点击、按键、滚轮、触摸**会触发 `trusted-user-input` 并递增 control epoch，打断 Agent 的租约。**鼠标只是划过不会**（默认策略 `intentional-input`），所以用户看着页面移动光标是安全的 |
| **BrowserScript 信任级别等同 Bash** | 脚本可访问 Node fs/net/child_process；源码过一次与 Bash 同档审批 + 每能力一问；接管/Lease 轮换即硬停 |
| **artifact 不要走 `/save`** | 该接口会弹系统「另存为」对话框等人点。**用回执里的 `result.artifact.absolutePath`**（工具会把它登记进本次会话的可读白名单），不要自己拼路径——`${DESIRECORE_ROOT}` 这类变量在路径展开里不认（只认 `~` / `$HOME` / `$USERPROFILE`），拼出来是相对路径、`Read` 会报「文件不存在」。默认保留 24 小时 |

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
| `BROWSER_TAB_HOST_NOT_FOUND` | 标签页宿主真的没了（渲染进程崩溃/销毁） | 重建 Session。命令超时**不再**引发此错误——超时只 stop 这一条命令，标签页保留 |
| `BROWSER_COMMAND_DEADLINE_EXCEEDED` | 单条命令超 30 s | 标签页仍停在上一页/空白页，直接重试；慢加载常态不算故障 |
| `BROWSER_VIEWPORT_UNAVAILABLE` | embedded 多标签会话的后台 tab 没有可用视口 | 先 `tab.activate` 再截图（秒级快判，不是挂死） |
| `BROWSER_TOOL_SESSION_FORBIDDEN` | 会话已关闭/崩溃，或不属于当前 Agent | 重新 `list_sessions`，必要时重建 |
| `BROWSER_TOOL_SESSION_AMBIGUOUS` | 当前 Agent 有多个会话且未传 sessionId | 显式传 `sessionId` |
| `BROWSER_HUMAN_APPROVAL_REQUIRED` | 触到人工闸门能力（evaluate / raw_cdp / 上传下载 / Cookie 导入等） | 向用户说明用途并等待审批，或换用无需审批的路径（取文用 extract-text，裁剪用 clip） |
| `BROWSER_RESULT_TOO_LARGE` | 回执超过结果上限 | text/semantic/accessibility 都有 maxBytes + cursor 分页，调小 maxBytes 续读即可，不再整体失败 |

## 调用链路

```
Agent → BrowserManage/Snapshot/Act/Script → browser-use service（Capability/Grant/Lease/Policy 校验）
      → BrowserHost（electron-embedded 或 standalone-managed）→ Chromium
                                    ↑ 每步产出带 digest 的回执，写入审计事件流
```
