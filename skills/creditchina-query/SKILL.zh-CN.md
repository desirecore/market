# 信用中国查询

## L0

输入企业名称，通过 Kimi WebBridge 浏览器自动化 + ddddocr 本地 OCR 自动过图形验证码，返回企业信用信息。

## L1 概述

- **数据源**：信用中国（`creditchina.gov.cn`，国家发改委指导）
- **认证**：图形验证码（ddddocr 本地 OCR 自动识别，~100ms）
- **调用方式**：Kimi WebBridge + CDP 截图 + ddddocr Python OCR
- **前置条件**：
  - Kimi WebBridge daemon 运行中
  - Python 已安装 `ddddocr`（`pip install ddddocr`）
  - Python 已安装 `Pillow`（`pip install pillow`）

## L2 操作步骤

### 1. 导航搜索页

写入 `C:\tmp\cc-nav.json`：

```json
{
  "action": "navigate",
  "args": {
    "url": "https://www.creditchina.gov.cn/xinyongxinxi/?keyword={企业名称URL编码}&scenesVal=default&tableName=credit_xyzx_tyshxydm",
    "newTab": true,
    "group_title": "信用中国查询"
  },
  "session": "creditchina-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cc-nav.json" --max-time 30
```

等待 6 秒。

### 2. 确认验证码弹层

写入 `C:\tmp\cc-check.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var v=document.getElementById('vcode');var i=document.getElementById('vcodeimg');return JSON.stringify({vcode:v?v.getBoundingClientRect().width>0:false,vimg:i?i.getBoundingClientRect().width>0:false});})()"
  },
  "session": "creditchina-query"
}
```

若 `vcode=true` 且 `vimg=true`，验证码弹层已出现，继续下一步。

### 3. 获取验证码图坐标

写入 `C:\tmp\cc-coord.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var img=document.getElementById('vcodeimg');if(!img)return 'no-img';var r=img.getBoundingClientRect();return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),dpr:window.devicePixelRatio});})()"
  },
  "session": "creditchina-query"
}
```

记录返回的 `x` / `y` / `w` / `h`。

### 4. CDP 截图验证码区域

> **注意**：WebBridge 的 screenshot 工具对此页面存在间歇性失败（HTTP 000/400），**必须用 CDP `Page.captureScreenshot` 的 clip 参数**。

写入 `C:\tmp\cc-shot.json`（替换 `{x}` / `{y}` / `{w}` / `{h}` 为上一步返回值）：

```json
{
  "action": "cdp",
  "args": {
    "method": "Page.captureScreenshot",
    "params": {
      "format": "png",
      "clip": { "x": {x}, "y": {y}, "width": {w}, "height": {h}, "scale": 1 }
    }
  },
  "session": "creditchina-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cc-shot.json" --max-time 40 -o "C:/tmp/cc-cdp-resp.json"
```

解码 base64 并保存为图片：

```python
import json, base64
d = json.load(open(r'C:\tmp\cc-cdp-resp.json', encoding='utf-8'))
b64 = d.get('data', {}).get('data', '')
open(r'C:\tmp\cc-captcha.png', 'wb').write(base64.b64decode(b64))
```

### 5. ddddocr 识别（~100ms）

```python
import ddddocr, sys, time
sys.stdout.reconfigure(encoding='utf-8')
ocr = ddddocr.DdddOcr(show_ad=False)
t0 = time.time()
with open(r'C:\tmp\cc-captcha.png', 'rb') as f:
    code = ocr.classification(f.read())
print(f'验证码: {code} ({(time.time()-t0)*1000:.0f}ms)')
open(r'C:\tmp\cc-code.txt', 'w').write(code)
```

### 6. 填入验证码 + 点击验证

写入 `C:\tmp\cc-submit.json`（替换 `{code}` 为识别结果）：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var inp=document.getElementById('vcode');if(!inp)return 'no-input';var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(inp,'{code}');inp.dispatchEvent(new Event('input',{bubbles:true}));inp.dispatchEvent(new Event('change',{bubbles:true}));for(var el of document.querySelectorAll('button, a, input[type=button]')){if((el.innerText||el.value||'').trim()==='验证'){el.click();break;}}return 'submitted';})()"
  },
  "session": "creditchina-query"
}
```

等待 5 秒。

### 7. 检查验证结果

写入 `C:\tmp\cc-result.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var t=document.body.innerText||'';if(t.includes('验证码错误'))return '验证码错误';if(t.includes('失效'))return '验证码已失效';return JSON.stringify({hasResult:t.includes('共')||t.includes('条'),textSample:t.slice(0,500)});})()"
  },
  "session": "creditchina-query"
}
```

**三种结果**：

- `"验证码错误"` / `"验证码已失效"` → 返回步骤 3 重试（点"换一张"刷新验证码）
- `hasResult=true` 且返回搜索数据 → 成功，继续步骤 8
- `textSample` 含"很抱歉，没有找到您搜索的数据" → 验证码已通过，但搜索词无匹配（非技术错误）——建议换企业全名或简称重试

### 8. 读取搜索结果

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){return document.body.innerText.slice(0,1500);})()"
  },
  "session": "creditchina-query"
}
```

### 9. 标准化映射

```json
{
  "query_status": "success",
  "source": "creditchina",
  "company_name": "{企业名称}",
  "captcha_solved": true,
  "search_result": "有结果 | 无匹配",
  "credit_info": [
    {
      "event_type": "行政处罚 | 行政许可 | 失信被执行 | 守信激励",
      "event_title": "...",
      "event_date": "...",
      "source_url": "...",
      "summary": "..."
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 10. 关闭会话

```json
{
  "action": "close_session",
  "session": "creditchina-query"
}
```

## 重试策略

验证码识别失败（错误/失效）时自动重试，最多 3 轮：

1. 点击"换一张"刷新验证码：`evaluate` 点击文本含"换一张"的元素
2. 等 2 秒（新图加载）
3. 重复步骤 3-6（重新截图→识别→提交）

3 轮失败后：报告用户，请人工在浏览器中手动过一次验证码，然后智能体接管继续（验证通过后浏览器记住验证态，后续查询免验证码）。

## 已知限制

- **验证码时效极短**：从截图到提交需 <15 秒——**必须用 ddddocr 本地识别（~100ms），禁用云端 OCR（10~30 秒往返必超时）**
- **CDP 截图替代 screenshot**：WebBridge screenshot 工具对此页面间歇性失败（HTTP 000/400），必须用 CDP `Page.captureScreenshot` 的 clip 参数
- **验证态缓存**：一次验证通过后，浏览器记住验证态——后续搜索（导航到新 keyword URL）不再需要验证码，直接返回结果
- **CORS 限制**：不能通过 `fetch+FileReader` 或 `canvas.toDataURL` 取图（跨子域 tainted）——只能用 CDP 截图
- **搜索词建议**：精确企业全名可能"没有找到您搜索的数据"（信用库只收录有信用记录的主体）——先试全名，无结果再试简称

## 故障排查

| 问题 | 原因 | 处理 |
|---|---|---|
| 412（直连被 WAF 拦截） | 未用浏览器 | 必须通过 WebBridge 浏览器访问 |
| 验证码弹层未出现 | keyword 参数未触发 | 检查 URL 中的 keyword 参数 |
| CDP 截图返回空 | 坐标错误 / 页面滚动 | 重新获取 vcodeimg 的 getBoundingClientRect |
| ddddocr 识别为空 | 图片损坏 / 识别失败 | 刷新验证码重试；确认 CDP 截图 bytes > 3000 |
| 验证码错误/失效 | 识别错 / 超时 | 点"换一张"重试（最多 3 轮）；仍失败转人工 |
| "没有找到您搜索的数据" | 企业无信用记录 / 词不匹配 | 换简称重试；确认企业有信用记录 |
