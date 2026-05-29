# BrowserXxx 工具速查（L3-fast）

> 适配自 [eze-is/web-access](https://github.com/eze-is/web-access) 的 `references/cdp-api.md`（MIT，作者 一泽 Eze）。
> DesireCore 把 cdp-proxy 内嵌为子进程，并通过这组 BuiltinTool 调用——比直接 curl 更安全（不暴露端口给 prompt 注入）、比 Python heredoc 更轻（无 Python/Playwright 依赖）。

## 何时用 BrowserXxx vs Python Playwright

| 场景 | 推荐 |
|------|------|
| 抓取登录态站点（小红书 / B站 / 微博 / 飞书 / 知乎） | **BrowserXxx**（fast，零 Python） |
| 简单点击 / 滚动 / 截图 / 上传文件 | **BrowserXxx** |
| 需要复杂等待逻辑（page.wait_for_selector + race condition） | Python Playwright（cdp-browser.md） |
| 需要在浏览器内运行长时间脚本（>30 s） | Python Playwright |

## 前置条件

1. 用户已启动调试模式 Chrome（端口 9222；见 SKILL.md 的 Prerequisites 部分）
2. cdp-proxy 子进程会在首次工具调用时由 agent-service lazy spawn

## 工具一览

每个工具默认 `hidden: true`，**只有 web-access 技能被激活后才暴露给 LLM**。

### BrowserListTabs

列出已打开 tab。返回每行 `[targetId] title — url`。

```yaml
BrowserListTabs:
  # 无参数
```

### BrowserNavigate

打开 URL；省略 `target` 时新开 tab。

```yaml
BrowserNavigate:
  url: https://www.xiaohongshu.com/explore/...
  target: <可选 targetId>
```

### BrowserEval

在指定 tab 内执行 JS（`returnByValue: true` + `awaitPromise: true`）。

```yaml
BrowserEval:
  target: <targetId>
  expression: |
    (() => {
      const t = document.querySelector('h1.video-title')?.textContent || ''
      const d = document.querySelector('.video-desc')?.textContent || ''
      return JSON.stringify({ title: t.trim(), desc: d.trim() })
    })()
```

提示：
- DOM 节点不能直接返回，要提取属性
- 大量数据用 `JSON.stringify()` 包裹返回字符串
- 风险等级 medium：是任意 JS 入口，不要执行不可信代码

### BrowserClick

```yaml
BrowserClick:
  target: <targetId>
  selector: button.submit
  mode: real-mouse   # 默认 js；登录态站点反爬严格时建议 real-mouse
```

`mode: real-mouse` 走 CDP `Input.dispatchMouseEvent` 派发真实鼠标事件——能触发文件对话框、绕过部分反自动化检测。

### BrowserScreenshot

```yaml
BrowserScreenshot:
  target: <targetId>
  filename: 自定义文件名.png  # 可选；写入 ${DESIRECORE_ROOT}/screenshots/
```

### BrowserScroll

```yaml
BrowserScroll:
  target: <targetId>
  direction: bottom    # 或 top；与 y 二选一
  # y: 3000           # 按像素滚动
```

### BrowserSetFiles（**需用户确认**）

为 input[type=file] 设置本地文件，绕过文件对话框。涉及上传，必须经 user confirmation。

```yaml
BrowserSetFiles:
  target: <targetId>
  selector: input[type=file]
  files:
    - /Users/me/Pictures/photo.png
```

### BrowserCloseTab

```yaml
BrowserCloseTab:
  target: <targetId>
```

任务收尾建议清理你创建的临时 tab，避免 cdp-proxy 的 tab 池堆积（15 min 后会自动 GC，但显式关更整洁）。

## SitePatternRead / SitePatternWrite

参见 SKILL.md 的"站点经验积累"章节。任务结束如果发现新陷阱、新选择器，调用：

```yaml
SitePatternWrite:
  domain: xiaohongshu.com
  scope: agent           # agent=共享（受 Git 管理，可发布）；user=私有
  mode: merge            # 默认 merge 追加；replace 覆盖
  content: |
    ## 已知陷阱
    - 2026-05: ...
```

含 cookie/token/手机号/邮箱时会自动降级 scope='user'。

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `Chrome 未开启远程调试端口` | 用户没启动调试 Chrome | 引导用户跑 SKILL.md 中的启动命令 |
| `attach 失败` | targetId 无效或 tab 已关闭 | 重新 `BrowserListTabs` |
| `CDP 命令超时` | 页面长时间未响应 | 检查页面状态，必要时 `BrowserCloseTab` 后重开 |
| `CDP proxy 请求被中止或超时` | 代理子进程异常或网络故障 | 等待 ProxyController 自动重启（最多 3 次） |

## 调用链路

```
Agent → BrowserXxx 工具 → proxy-client → cdp-proxy 子进程 → Chrome (DevTools Protocol)
                          ↑ 首次调用 lazy spawn 子进程
```
