# AgentFS 背景知识（共享）

> 此文件由 create-agent、update-agent 等元技能共享引用。
> 以下信息仅供 Agent 内部理解，**不要向用户展示**。

## AgentFS v2 仓库结构

每个 Agent 的仓库遵循 AgentFS v2 扁平结构：

```
<agent_id>/
├── agent.json        # 元数据与运行时配置
├── persona.md        # 人格定义（L0/L1/L2）
├── principles.md     # 行为原则（L0/L1/L2）
├── memory/           # 记忆目录
├── skills/           # 技能目录
├── tools/            # 工具目录
└── heartbeat/        # 心跳配置
```

## 关键文件说明

| 文件 | 验证 API | 常见问题 |
|------|---------|---------|
| `agent.json` | `GET /api/agents/:id` 返回完整配置 | engine 字段缺失导致无法启动 |
| `persona.md` | `GET /api/agents/:id/persona` 返回结构化数据 | L0 为空则 Agent 无身份摘要 |
| `principles.md` | `GET /api/agents/:id/principles` 返回结构化数据 | must_not 为空则无安全红线 |
| `memory/` | 目录存在即可 | `_policy.json` 缺失会使用默认策略 |

## 受保护路径

详见 `_protected-paths.yaml`。核心规则：

- `persona.md` L0 section — **block**（核心身份，不可自动修改）
- `principles.md` "绝不做" section — **block**（安全红线，需人类显式修改）
- `agent.json` access_control / privacy — **owner_only**（需 owner 确认）
- `tools/` permissions / credentials — **owner_only / block**（敏感操作）
