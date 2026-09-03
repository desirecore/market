# 中国政府采购网招标公告查询

## L0

输入企业名称（建议用简称而非全名，如"华为"而非"华为技术有限公司"），通过 Kimi WebBridge 浏览器自动化搜索政府采购网，返回结构化招标公告列表。

## L1 概述

- **数据源**：中国政府采购网搜索系统（`search.ccgp.gov.cn`）
- **认证**：无（公开搜索）
- **调用方式**：Kimi WebBridge 浏览器自动化（navigate + evaluate）
- **前置条件**：Kimi WebBridge daemon 运行中（`127.0.0.1:10086`）+ 浏览器扩展已连接
- **核心优势**：浏览器会话天然规避 curl 直连的 IP 限流

## L2 操作步骤

### 1. 检查 WebBridge daemon

```bash
curl -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  -d '{"action":"list_tabs","session":"ccgp-query"}' --max-time 10
```

若连接失败，启动 daemon：

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe start
```

### 2. 导航搜索结果页

**Windows 方式**（JSON 写入临时文件避免编码问题）：

写入 `C:\tmp\ccgp-nav.json`：

```json
{
  "action": "navigate",
  "args": {
    "url": "https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&pinMu=0&bidType=0&dbselect=bidx&kw={企业简称URL编码}",
    "newTab": true,
    "group_title": "政府采购网查询"
  },
  "session": "ccgp-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\ccgp-nav.json" --max-time 30
```

等待 5 秒后继续。

### 3. 提取公告列表

写入 `C:\tmp\ccgp-extract.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var txt=document.body.innerText||'';var total=(txt.match(/共找到\\s*(\\d+)\\s*条/)||[])[1]||'?';var items=[];document.querySelectorAll('a').forEach(function(a){var t=(a.innerText||'').replace(/\\s+/g,' ').trim();if(t.includes('{企业名称关键字}')&&t.length>10){var li=a.closest('li')||a.closest('div');var date='';if(li){var m=(li.innerText||'').match(/\\d{4}[-:]\\d{2}[-:]\\d{2}/);if(m)date=m[0];}items.push({title:t.slice(0,80),href:(a.href||'').slice(0,100),date:date});}});return JSON.stringify({total:total,count:items.length,items:items.slice(0,10)});})()"
  },
  "session": "ccgp-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\ccgp-extract.json" --max-time 40
```

### 4. 深度提取详情页（可选）

对列表中每条公告，导航到详情页并提取结构化字段：

```json
{
  "action": "navigate",
  "args": { "url": "{公告详情URL}" },
  "session": "ccgp-query"
}
```

等待 5 秒后提取：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var txt=document.body.innerText||'';var lines=txt.split('\\n').map(function(s){return s.trim();}).filter(function(s){return s.length>0;});var fields={};for(var i=0;i<lines.length-1;i++){var l=lines[i];var n=lines[i+1];if(/采购人|采购代理|项目名称|项目编号|采购方式|中标|金额|供应商|地址|联系人|电话|公告日期|品目|更正/.test(l)&&n.length<200){fields[l]=n;}}return JSON.stringify({title:document.title,url:location.href.slice(0,80),fields:fields});})()"
  },
  "session": "ccgp-query"
}
```

### 5. 标准化映射

```json
{
  "query_status": "success",
  "source": "ccgp",
  "company_name": "{企业名称}",
  "total_found": 2,
  "announcements": [
    {
      "event_type": "招投标公告",
      "event_title": "乌兰察布职业学院物业服务（华为校区）采购更正公告（第一次）",
      "event_date": "2026-08-25",
      "source_url": "http://www.ccgp.gov.cn/cggg/dfgg/gzgg/...",
      "project_number": "WSZC-G-F-260032",
      "purchaser": "乌兰察布职业学院",
      "agency": "乌兰察布市公共资源交易中心",
      "contact": "栗春雨 0474-8305228",
      "correction": "投标截止时间 2026-09-02 → 2026-09-10"
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 6. 翻页（可选）

若 `total` > 10，修改 URL 中 `page_index=2` 重复步骤 2-3。保持 ≥5 秒间隔。

### 7. 关闭会话

```json
{
  "action": "close_session",
  "session": "ccgp-query"
}
```

## 已知限制

- **默认时间范围仅近一周**：搜索结果可能为 0——需在 URL 中加 `start_time` 和 `end_time` 参数放宽（如 `start_time=2026:01:01&end_time=2026:08:31`），或点击页面"近半年"筛选
- **标题检索模式**：搜索匹配公告标题中的关键词，非供应商维度——企业全名命中率低，建议用简称（如"华为"而非"华为技术有限公司"）
- **礼貌间隔**：浏览器会话虽规避了 curl 限流，但仍应保持 ≥5 秒/次的间隔，不要高频翻页
- **HTML 结构依赖**：页面改版可能导致选择器失效——若提取为空，改用 `document.body.innerText` 全文读取

## 故障排查

| 问题 | 原因 | 处理 |
|---|---|---|
| navigate 失败 | daemon 未运行 / 扩展断开 | `kimi-webbridge.exe start` 重启 daemon |
| "频繁访问" | IP 限流 | 浏览器会话一般不触发；若触发等 60 秒重试 |
| 提取列表为空 | 搜索结果为 0 / 选择器失效 | 检查 keyword 是否正确；改用 `evaluate` 读 `body.innerText` |
| 详情页字段为空 | 页面异步加载未完成 | 等 5 秒后重试提取 |
