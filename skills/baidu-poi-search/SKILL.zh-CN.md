# 百度地图 POI 搜索

## L0

输入企业名称，调用百度地图地点检索 API，返回标准化 POI 数据（名称/地址/经纬度/省市）。

## L1 概述

- **数据源**：百度地图开放平台地点检索 API v2
- **认证**：AK（个人开发者免费配额）
- **调用方式**：HTTP GET（curl / HttpRequest 工具）
- **前置条件**：无浏览器依赖、无额外依赖——纯 REST API

## 凭证获取

本技能需要百度地图 AK（访问令牌）：

1. 访问 [百度地图开放平台](https://lbsyun.baidu.com/) 注册开发者账号
2. 控制台 → 应用管理 → 创建应用（启用"地点检索"服务，AK 类型选"浏览器白名单"并将白名单留空 `0.0.0.0/0`）
3. 将 AK 配置为环境变量 `BAIDU_MAP_AK`，或替换下文命令中的 `{BAIDU_MAP_AK}` 占位符

> 若本机 DesireCore 服务目录已注册百度地图服务（端点 `https://api.map.baidu.com`），优先通过服务目录调用，凭证由服务配置统一管理。

## L2 操作步骤

### 1. 构造请求

```bash
curl -s --max-time 15 --ssl-no-revoke \
  "https://api.map.baidu.com/place/v2/search?query={企业名称URL编码}&region={城市或全国}&output=json&page_size=20&ak=${BAIDU_MAP_AK}"
```

**参数说明**：

| 参数 | 值 | 说明 |
|---|---|---|
| query | 企业名称（URL 编码） | 如"华为技术有限公司"→ `%E5%8D%8E%E4%B8%BA%E6%8A%80%E6%9C%AF%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8` |
| region | 城市名或"全国" | 限定检索范围；不确定时用"全国" |
| output | json | 固定 |
| page_size | 20 | 每页条数（最大 20） |
| ak | `{BAIDU_MAP_AK}` | 百度地图 AK（个人开发者免费申请） |

### 2. 判断响应

- `status == 0`：成功，提取 `results[]`
- `status != 0`：失败，查看 `message`（如 101=AK参数不存在，200=AK被禁用，302=配额超限）

### 3. 标准化映射

对 `results[]` 中每条记录映射为：

```json
{
  "source": "baidu-poi",
  "company_name": "{用户输入的企业名称}",
  "poi_name": "{result.name}",
  "address": "{result.address}",
  "latitude": "{result.location.lat}",
  "longitude": "{result.location.lng}",
  "province": "{result.province}",
  "city": "{result.city}"
}
```

### 4. 同名词过滤（尽调场景）

POI 结果可能包含同名词干扰（如"南岗华为公司"不是"华为技术有限公司"）。过滤建议：

- 精确匹配：`result.name` 与企业全名一致 → 标记 `match=exact`
- 包含匹配：`result.name` 包含企业全名或其简称 → 标记 `match=partial`
- 其他 → 标记 `match=related`，尽调报告单独归类

### 5. 输出格式

```json
{
  "query_status": "success",
  "source": "baidu-poi",
  "total": 5,
  "results": [
    { "poi_name": "华为技术有限公司", "address": "广东省深圳市龙岗区...", "latitude": "22.656137", "longitude": "114.066131", "match": "exact" }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

## 已知限制

- 免费配额：个人开发者有 QPS（约 3 次/秒）与日量上限（地点检索约 100 次/日，以控制台额度管理为准）
- POI ≠ 工商注册地址：返回的是地图标注地址，可能与工商注册地址不同（尽调时注意区分）
- 同名词：知名企业简称（如"华为"）会命中大量非目标 POI，建议输入企业全名

## 故障排查

| 错误码 | 含义 | 处理 |
|---|---|---|
| 0 | 成功 | — |
| 101 | AK 参数不存在 | 检查 ak 参数是否正确传递 |
| 200 | AK 被禁用 | 到百度地图开放平台控制台检查应用状态 |
| 201 | AK 校验失败 / SN 校验失败 | 本方案使用白名单 0.0.0.0/0 类型 AK，无需 SN |
| 302 | 配额超限 | 查看控制台额度管理，等待次日或升级配额 |
| 240 | API 服务无效 | AK 未勾选"地点检索"服务——到控制台修改应用勾选 |
