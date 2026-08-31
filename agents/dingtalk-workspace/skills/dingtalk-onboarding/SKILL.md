---
name: dingtalk-onboarding
description: 钉钉能力接入与健康自检。Use when 首次使用钉钉能力、报「dws 未找到 / 未登录 / 权限不足 / 权益未开通」、需要授权或换组织、或钉钉命令报错需要定位是环境问题还是业务问题。负责安装检测、授权引导、doctor 解读、多组织 profile 切换。**不做任何钉钉业务操作**——业务命令走 dingtalk-* 官方技能。
metadata:
  category: onboarding
  requires:
    bins:
      - dws
    tools:
      - Bash
---

# 钉钉接入与自检

本技能只管**能不能用**，不管**做什么**。任何钉钉业务操作都交给官方 `dingtalk-*` 技能。

## 为什么需要这个技能

钉钉官方 CLI `dws` 自带一套 Agent 技能分发机制，会把 14 个产品技能装到它认识的 80+ 个 Agent 框架目录里（`~/.claude/skills/`、`~/.cursor/skills/`、`~/.agents/skills/` 等）。

**但它的目标枚举里没有 DesireCore。** `dws skill install <id> <target>` 和 `dws skill setup --target` 的 target 都是固定枚举，`--source` 只能改源不能改目标。所以 DesireCore 用户拿不到官方的自动分发，必须走 DesireCore 自己的市场条目。

这就是本技能存在的理由。

## 自检顺序

首次执行钉钉操作前按顺序确认。后续轮次可复用结论，**除非出错**。

### 第 1 步：装了吗

```bash
command -v dws
```

无输出 = 未安装。**立刻停止**，告诉用户：

```
钉钉能力需要先安装官方 CLI：

    npm i -g dingtalk-workspace-cli

装完我再继续。
```

**不要**假装执行了钉钉操作，**不要**用 curl 或其它方式绕过。

### 第 2 步：授权了吗

```bash
dws auth status --format json
```

`authenticated: false` = 未授权。**立刻停止**，引导授权：

```bash
dws auth login            # 本机有浏览器：OAuth 回环，自动完成
dws auth login --device   # 无浏览器 / SSH / 容器：出设备码
```

⚠️ **钉钉不支持账号密码登录，也不支持手机验证码、纯应用凭证。** 只有 OAuth 回环、设备流、`--token`、自有应用 OAuth 四种。用户给你账号密码时要说明这一点。

设备流会打印授权链接和一个形如 `XXXX-XXXX` 的码，**原样转给用户**，不要改写。码 15 分钟过期，过期后 dws 会自动重新出码。

授权成功后 token 自动刷新（access token 约 2 小时，refresh token 约 30 天），之后无需再打扰用户。

### 第 3 步：出错时才跑 doctor

```bash
dws doctor
```

四项：登录状态 / 钥匙串 / 网络连通性 / 版本更新。

**这是排障工具，不是心跳。** 不要每轮都跑。

## 错误分诊

拿到错误先判断是**环境问题**还是**业务问题**——这决定了要不要打扰用户。

| 特征 | 类型 | 处理 |
|---|---|---|
| `command not found` | 环境 | 回第 1 步 |
| `authenticated: false` / `resolve access token` 失败 | 环境 | 回第 2 步 |
| `category: validation` + `缺少必填参数 X` | **参数问题，不是权限** | 补上参数重试，不要打扰用户 |
| `category: validation` + `unknown flag` / `blocked_flag` | **参数问题** | 查 `--help` 用正确的 flag。注意有些 flag 被显式屏蔽了自动归一化 |
| `category: api` + `server_error_code` 带 `RightsDenied` / `权益` | **权益未开通**（要买/要开通，不是配权限） | 停止，说明缺哪项权益，指向钉钉管理后台 |
| `category: api` + 权限点相关 | **权限不足** | 停止，说明缺哪个权限点 |
| `subtype: missing_collection` | **不是错误也不是空** | 响应结构未知，dws 拒绝把它当空结果。换个入口交叉确认，**不要报告「没有数据」** |
| 网络超时 / `doctor` 网络项失败 | 环境 | 停止说明；**不要重试写操作**——可能已生效 |

### 一个真实样本

```
server_error_code: SearchRightsDenied
message: 当前用户暂无消息搜索权益，无法执行本次搜索。请提示用户开通消息搜索权益后重试。
```

这是**权益**问题：`chat` 域里一切依赖消息检索的能力（搜聊天记录、@我汇总、拉历史消息）不可用，但发消息、群管理、机器人、会话分组等非检索能力**仍然可用**。

正确处理：告诉用户「消息搜索需要开通权益」，并说明哪些 chat 能力仍可用。**不要**换个命令硬试，**不要**把整个 chat 域报成不可用。

## 多组织

```bash
dws profile list --format json
```

单组织时无需关心。多组织时：

- **禁止默认取第一个**，也禁止取「最近登录」或「最近使用」
- 没有 `isOrgCurrent=true` 时必须**问用户**
- **解析目标、读取上下文、最终执行必须使用同一个 profile**——跨 profile 混用会拿到错的 userId 和错的文档

一次性指定用 `--profile <corpId>:<userId>`（推荐用 `profile list` 返回的完整形式）。

## 安装官方产品技能

钉钉的 14 个产品技能：`dingtalk-aisearch` / `aitable` / `calendar` / `chat` / `contact` / `doc` / `drive` / `event` / `mail` / `minutes` / `misc` / `shared` / `todo` / `wiki`。

### 当前唯一可用的安装路径

装完 `dws` 后，技能已经在本机了——postinstall 会把它们解包到 `~/.dws/skills/multi/`。从那里拷进 DesireCore 的全局技能目录即可：

```bash
# 目标目录随运行时根变化，不要写死 ~/.desirecore
DC_ROOT="${DESIRECORE_TEST_ROOT:-${DESIRECORE_HOME:-$HOME/.desirecore}}"
mkdir -p "$DC_ROOT/skills"
for s in ~/.dws/skills/multi/dingtalk-*; do
  cp -R "$s" "$DC_ROOT/skills/"
done
```

拷完让用户重启 DesireCore 或等下一轮技能发现（每轮 query 重新发现）。

**必须同时告诉用户这个代价**：这样装的技能**没有 provenance 记录**（`skills.lock` 里没有 `providerId` / `contentDigest`），所以：
- DesireCore 的市场同步会把它们当作孤儿条目——**既不会自动更新，也不会自动卸载**
- `dws upgrade` 升级二进制后，`~/.dws/skills/multi/` 里的技能会更新，但 **DesireCore 里的副本不会跟着变**，需要重新拷一次

所以每次 `dws upgrade` 之后，提醒用户重跑一遍上面的拷贝。

### 为什么不能走市场安装

市场里有 `dingtalk-cli` 条目，但**它现在装不了**：钉钉官方仓库 `open-dingtalk/dingtalk-workspace-cli` 未公开（HTTP 404），市场客户端按 git 源拉取会失败。该条目的作用是**让用户在市场里发现钉钉能力并看到安装说明**，不是实际分发通道。

如果用户在市场点了安装并报错，这是预期行为，按上面的手工路径引导即可，**不要说市场坏了**。

### 为什么不能用 `dws skill setup`

`dws skill setup --target` 和 `dws skill install <id> <target>` 的 target 是**固定枚举**（80+ 个 Agent 框架），**里面没有 DesireCore**；`--source` 只能改源不能改目标。所以官方的自动分发对 DesireCore 用户不生效。

⚠️ 注意 `dws` 的 postinstall 会**自动**往它认识的框架目录写技能（`~/.claude/skills/`、`~/.cursor/skills/`、`~/.agents/skills/` 等）。如果用户同时用别的 AI 编程工具，装 dws 会顺带修改那些目录——这是上游行为，值得提前告知。

## 边界

本技能**不做**：任何钉钉业务操作、命令目录说明、产品能力介绍。

那些属于官方 `dingtalk-*` 技能。用 `dws schema --compact` 做能力发现，用官方技能的 description 做产品路由。
