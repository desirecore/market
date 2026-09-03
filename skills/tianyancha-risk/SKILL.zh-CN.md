# 天眼查企业风险查询

## L0

输入企业名称，调用天眼查风险信息 API，返回结构化风险画像（自身/周边/历史/预警四类）。

## L1 概述

- **数据源**：天眼查开放平台 `risk/riskInfo/2.0`
- **认证**：Token（`Authorization` Header，**不带 `Bearer` 前缀**）
- **调用方式**：HTTP GET（curl / HttpRequest 工具）
- **前置条件**：Token 有效（需在天眼查开放平台开通对应接口权限）

## 凭证获取

本技能需要天眼查开放平台 Token：

1. 访问 [天眼查开放平台](https://open.tianyancha.com/) 注册企业账号
2. 购买/开通接口套餐（风险信息接口 `risk/riskInfo/2.0` 按套餐分级授权）
3. 将 Token 配置为环境变量 `TIANYANCHA_TOKEN`，或替换下文命令中的 `{TIANYANCHA_TOKEN}` 占位符

## L2 操作步骤

### 1. 构造请求

```bash
curl -s --max-time 30 --ssl-no-revoke \
  "https://open.api.tianyancha.com/services/open/risk/riskInfo/2.0?keyword={企业名称URL编码}" \
  -H "Authorization: ${TIANYANCHA_TOKEN}"
```

**参数说明**：

| 参数 | 值 | 说明 |
|---|---|---|
| keyword | 企业名称（URL 编码） | 如"华为技术有限公司" |
| Authorization | `{TIANYANCHA_TOKEN}` | **Header 传 Token，不带 `Bearer` 前缀**（带前缀返回 300009） |

### 2. 判断响应

- `error_code == 0` 且 `reason == "ok"`：成功，提取 `result.riskList[]`
- `error_code == 300009`：账号信息有误——Token 错误或加了 Bearer 前缀
- `error_code == 300005`：无权限访问此 API——当前 Token 未授权该接口
- `error_code == 300008`：缺少必要参数——检查 keyword

### 3. 响应结构解析

`result` 包含两个字段：

- `riskLevel`：整体风险等级
- `riskList[]`：四类风险（每类含 name / count / type / list[]）

四类风险：

| 类型 | type | 含义 |
|---|---|---|
| 自身风险 | 1 | 该企业自身的司法/经营风险（开庭公告/裁判文书/立案信息/法院公告/司法拍卖等） |
| 周边风险 | 2 | 关联方（股东/高管/投资企业）的风险 |
| 历史风险 | 3 | 已了结的历史风险（历史立案/历史开庭/被执行人_历史等） |
| 预警提醒 | 0 | 工商变更提醒（投资人变更/主要人员变更/注册资本变更/法定代表人变更/破产案件等） |

每类下 `list[]` 为子项，每子项含 `title`（如"开庭公告"）/ `total`（条数）/ `tag`（警示/高风险/提示信息）/ `list[]`（前几条明细，含 id / title / desc / riskCount）。

### 4. 标准化映射

```json
{
  "query_status": "success",
  "source": "tianyancha",
  "company_name": "{企业名称}",
  "risk_level": "{result.riskLevel}",
  "summary": {
    "self_risk_count": 3127,
    "related_risk_count": 1505,
    "history_risk_count": 9113,
    "warning_count": 815
  },
  "self_risks": [
    { "risk_type": "开庭公告", "count": 1501, "level": "警示", "title": "该公司起诉他人或公司的开庭公告", "detail_count": 1096 }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 5. 尽调要点提炼

输出报告时按以下优先级提炼：

1. **高风险条目**（tag=高风险）：如"被执行人"、"清算信息"、"失信被执行人"——直接列为重大风险项
2. **警示条目大额计数**（total > 100）：如开庭公告 1501 条——列为司法活跃度指标
3. **预警变更**：近期投资人/法定代表人/注册资本变更——列为经营动态

## 已知限制

- **Token 分级授权**：接口按套餐授权，未授权接口返回 300005——购买全维度套餐后可扩展工商/股权/知产等接口
- **QPS 限流**：天眼查 API 按套餐有 QPS 限制，连续调用注意间隔（建议 ≥1 秒）
- **响应体量大**：大企业响应可达 98KB+，解析时注意内存与上下文压缩（只提取汇总+前 N 条明细）

## 故障排查

| 错误码 | 含义 | 处理 |
|---|---|---|
| 0 | 成功 | — |
| 300005 | 无权限访问此 API | 当前 Token 未授权该接口；确认调用的接口在授权范围内 |
| 300008 | 缺少必要参数 | 检查 keyword 参数 |
| 300009 | 账号信息有误 | Token 错误 / 加了 Bearer 前缀 / Token 过期——去掉前缀重试，仍失败则更新 Token |
