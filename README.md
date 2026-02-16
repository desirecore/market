# DesireCore Market

DesireCore 官方市场仓库，存放经过官方验证的 Agent 和 Skill 定义。

## 目录结构

```
.
├── manifest.json      # 仓库元数据
├── categories.json    # 分类配置
├── README.md          # 本文件
├── agents/            # Agent 定义目录
│   ├── task-master/
│   │   └── agent.json
│   ├── code-reviewer/
│   │   └── agent.json
│   ├── business-analyst/
│   │   └── agent.json
│   ├── writing-coach/
│   │   └── agent.json
│   ├── translator/
│   │   └── agent.json
│   └── data-analyst/
│       └── agent.json
└── skills/            # Skill 定义目录
    ├── web-search/
    │   └── skill.json
    ├── file-manager/
    │   └── skill.json
    ├── calendar-sync/
    │   └── skill.json
    ├── doc-parser/
    │   └── skill.json
    └── email-client/
        └── skill.json
```

## Agent 清单

| ID | 名称 | 分类 | 定位 |
|----|------|------|------|
| task-master | 任务管家 | 效率 | 智能任务规划与追踪专家 |
| code-reviewer | 代码审查官 | 开发 | 资深代码审查与质量把控 |
| business-analyst | 商业洞察师 | 商业 | 数据驱动的商业分析顾问 |
| writing-coach | 写作教练 | 创意 | 从构思到润色的写作伙伴 |
| translator | 译界通 | 沟通 | 跨文化沟通与专业翻译 |
| data-analyst | 数据洞察师 | 数据 | 数据科学与业务洞察专家 |

## Skill 清单

| ID | 名称 | 分类 | 风险等级 | 功能概述 |
|----|------|------|----------|----------|
| web-search | 网络搜索 | 效率 | 中 | 智能搜索与信息聚合 |
| file-manager | 文件管家 | 开发 | 高 | 本地文件系统管理 |
| calendar-sync | 日历同步 | 商业 | 中 | 日历服务连接与调度 |
| doc-parser | 文档解析器 | 数据 | 低 | 50+ 格式文档解析 |
| email-client | 邮件助理 | 沟通 | 高 | 智能邮件管理与起草 |

## 数据格式

### Agent 定义 (agents/{id}/agent.json)

```json
{
  "id": "string",
  "name": "string",
  "avatar": { "t": "string", "bg": "string" },
  "shortDesc": "string",
  "fullDesc": "string",
  "category": "productivity|development|business|creative|communication|data",
  "tags": ["string"],
  "version": "semver",
  "latestVersion": "semver",
  "updatedAt": "YYYY-MM-DD",
  "maintainer": { "name": "string", "verified": boolean },
  "downloads": number,
  "rating": number,
  "ratingCount": number,
  "installStatus": "not_installed",
  "persona": {
    "role": "string",
    "traits": ["string"],
    "tools": ["string"]
  }
}
```

### Skill 定义 (skills/{id}/skill.json)

```json
{
  "id": "string",
  "name": "string",
  "icon": "lucide-icon-name",
  "shortDesc": "string",
  "fullDesc": "string",
  "category": "productivity|development|business|creative|communication|data",
  "tags": ["string"],
  "version": "semver",
  "latestVersion": "semver",
  "updatedAt": "YYYY-MM-DD",
  "maintainer": { "name": "string", "verified": boolean },
  "downloads": number,
  "rating": number,
  "ratingCount": number,
  "installStatus": "not_installed",
  "riskLevel": "low|medium|high",
  "requires": {
    "tools": ["string"],
    "connections": ["string"]
  },
  "compatibleAgents": ["string"]
}
```

## 设计令牌

头像背景色使用 DesireCore 设计系统：

- **Green (#34C759)**: 效率、商业类
- **Blue (#007AFF)**: 开发、沟通类
- **Purple (#AF52DE)**: 创意、数据类

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
