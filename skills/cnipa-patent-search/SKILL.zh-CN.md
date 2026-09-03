# 国家知识产权局专利检索

## L0

输入企业名称，通过 Kimi WebBridge 浏览器自动化操作 pss-system 专利检索系统，返回结构化专利列表。

## L1 概述

- **数据源**：国家知识产权局专利检索及分析系统（`pss-system.cponline.cnipa.gov.cn`）
- **认证**：账号登录态（**必须先注册登录**——匿名检索会跳转登录页）
- **调用方式**：Kimi WebBridge 浏览器自动化（navigate + evaluate + CDP insertText）
- **前置条件**：
  - Kimi WebBridge daemon 运行中
  - 用户已在浏览器中**登录 pss-system 账号**（登录态长期有效，登录一次即可复用）

## 账号注册

pss-system 需实名注册（手机号 + 短信验证）：

1. 浏览器访问 `https://pss-system.cponline.cnipa.gov.cn/`
2. 点击"注册"完成实名注册
3. 登录一次——登录态由浏览器保存，后续自动化复用

## L2 操作步骤

### 1. 检查 WebBridge daemon

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe status
```

若 daemon 未运行或扩展断开，启动：`kimi-webbridge.exe start`。

### 2. 导航 pss-system

写入 `C:\tmp\cnipa-nav.json`：

```json
{
  "action": "navigate",
  "args": {
    "url": "https://pss-system.cponline.cnipa.gov.cn/",
    "newTab": true,
    "group_title": "专利检索"
  },
  "session": "cnipa-patent"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cnipa-nav.json" --max-time 30
```

等待 5 秒。

### 3. 确认登录态 + 同意声明 + 进入检索页

写入 `C:\tmp\cnipa-agree.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(async function(){var txt=document.body.innerText||'';var hasLogout=txt.includes('退出');if(txt.includes('免责声明')){var btns=document.querySelectorAll('button.el-button--primary');for(var b of btns){if((b.innerText||'').replace(/\\s+/g,'')==='同意'){b.click();break;}}await new Promise(function(r){setTimeout(r,4000);});}txt=document.body.innerText||'';return JSON.stringify({url:location.href.slice(0,80),isSearch:txt.includes('常规检索'),inputs:document.querySelectorAll('input').length,hasLogout:hasLogout});})()"
  },
  "session": "cnipa-patent"
}
```

**登录态判断**：若 `hasLogout=false`，说明未登录——需用户在浏览器中登录 pss-system 后重试。

### 4. 聚焦检索框 + CDP 真实输入

写入 `C:\tmp\cnipa-focus.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){for(var i of document.querySelectorAll('input')){if((i.placeholder||'').includes('请输入关键词')){i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));i.focus();return 'focused';}}return 'not-found';})()"
  },
  "session": "cnipa-patent"
}
```

执行后，写入 `C:\tmp\cnipa-insert.json`（CDP 真实输入，Vue 组件兼容）：

```json
{
  "action": "cdp",
  "args": {
    "method": "Input.insertText",
    "params": { "text": "{企业名称}" }
  },
  "session": "cnipa-patent"
}
```

### 5. 点击检索 + 等待结果

写入 `C:\tmp\cnipa-click.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(async function(){var clicked=false;for(var el of document.querySelectorAll('div.btn')){if((el.innerText||'').replace(/\\s+/g,'')==='检索'){el.click();clicked=true;break;}}await new Promise(function(r){setTimeout(r,8000);});var tables=document.querySelectorAll('table').length;var rows=document.querySelectorAll('table tr').length;var hits=(document.body.innerText.match(/共[\\d,]+[条篇]/)||[])[0]||'';return JSON.stringify({clicked:clicked,url:location.href.slice(0,80),tables:tables,rows:rows,hits:hits});})()"
  },
  "session": "cnipa-patent"
}
```

### 6. 提取表格数据

写入 `C:\tmp\cnipa-table.json`：

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var table=document.querySelector('table');if(!table)return JSON.stringify({err:'no-table'});var headers=[];table.querySelectorAll('thead th').forEach(function(th){headers.push((th.innerText||'').trim())});var rows=[];table.querySelectorAll('tbody tr').forEach(function(tr){var cells=[];tr.querySelectorAll('td').forEach(function(td){cells.push((td.innerText||'').trim().slice(0,60))});rows.push(cells)});return JSON.stringify({headers:headers,rowCount:rows.length,rows:rows});})()"
  },
  "session": "cnipa-patent"
}
```

### 7. 标准化映射

```json
{
  "query_status": "success",
  "source": "cnipa",
  "company_name": "{企业名称}",
  "total_found": 1,
  "patents": [
    {
      "patent_number": "202310104843.5",
      "application_date": "2023.01.16",
      "patent_name": "一种通信方法及装置",
      "patent_type": "发明",
      "patent_status": "实质审查的生效",
      "main_class_code": "H04W72/54",
      "applicant": "华为技术有限公司",
      "applicant_address": "广东省深圳市",
      "publication_number": "CN117834529A",
      "publication_date": "2024.04.05"
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 8. 关闭会话

```json
{
  "action": "close_session",
  "session": "cnipa-patent"
}
```

## 已知限制

- **必须登录态**：匿名状态下点击检索会跳转 login 页或静默无响应（行为不稳定）；登录态下检索正常返回结果
- **登录态会话保持**：浏览器登录 pss-system 后 cookie 长期有效，WebBridge 会话可复用——但长时间未操作后可能需要重新登录
- **Vue 组件兼容性**：必须用 CDP `Input.insertText` 真实输入（非 DOM setter），否则 Vue 下拉联想组件不接收文本
- **翻页**：结果超过 10 条时，点击页面分页按钮翻页，提取每页表格数据

## 故障排查

| 问题 | 原因 | 处理 |
|---|---|---|
| 点击检索后 URL 跳转到 login | 未登录 | 用户在浏览器中登录 pss-system |
| 点击检索后无响应 | Vue 事件未触发 | 确认用 CDP insertText 输入了检索词；检查登录态是否有效 |
| 表格为空 | 结果异步加载中 | 等待 8 秒后重新提取表格 |
| "免责声明"页卡住 | 同意按钮未点击成功 | 重新执行 evaluate 点击同意按钮 |
