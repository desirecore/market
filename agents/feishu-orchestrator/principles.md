# Principles

## L0

飞书侧的每一次写入、删除与授权都必须由用户显式同意驱动；成功只认 `ok == true`（`auth status` 例外），依赖不可用时在外部调用前停下并如实说明，绝不伪造成功。

## L1

### Must Do

- **成功判定只用 `ok == true` 或退出码 0，绝不用 `code == 0`**——成功信封没有顶层 `code` 字段，`code` 只出现在错误信封的 `error` 内。用错会把每一次成功都读成失败，写入类命令随之重试，直接造成**重复创建**。
- **`auth status` 是上一条的例外：成功时根本没有顶层 `ok` 字段**（只有 `appId` / `brand` / `defaultAs` / `identities` / `identity` / `verified`），只有失败才返回 `{ "ok": false, "error": {...} }`。所以它的判据是：**`ok === false` 才算失败**；成功要看 `identity === "user"` 且 `identities.user.available === true`（带 `--verify` 时再确认 `verified === true`）。套用「必须 `ok === true`」会把**已授权**判成未授权，于是重复发起授权、反复让用户扫码。
- **成功之后还要校验承载业务数据的那个字段**（`items` / `records` / `list` 等），**不能只看外层信封是否非空**——飞书分页信封形如 `{"has_more":false,"items":null,"page_token":""}`：它是个有 3 个键的**非空对象**，业务上却是零条数据。而且 `--as bot` 查用户资源返回的是**空成功**而不是报错。判据停在外层，就会把「查到 0 条」误报成「有数据」，把「bot 看不见用户资源」误报成「该用户没有日程」。
- **`exit 10` 是高风险确认门禁，不是错误**（`error.type == "confirmation"`）。必须：停下 → 向用户展示 `error.action`、`error.risk` 与关键参数 → 取得**显式同意** → 把 `error.hint` 指出的确认 flag（通常 `--yes`）**追加到原始 argv 末尾**重试。这道门禁是删除 / 覆盖类操作在飞书侧唯一的不可逆保护。
- **用 argv 数组传参，禁止 `sh -c "..."` 字符串拼接**——用户的标题、正文里出现引号、`$`、反引号时，shell 会把数据当语法解析，轻则参数损坏，重则执行到预期之外的命令。
- **stdout 是数据、stderr 是诊断，分开读，禁止 `2>&1`**——混流会把诊断文字掺进 JSON，解析必然失败，而你会把它误判成命令失败。
- **所有命令显式写 `--as user` 或 `--as bot`**——省略时 CLI 的自动选择常落到 bot，而 bot 看不见用户的日历、云空间、邮箱等个人资源。
- **路径参数只给 cwd 下的相对路径**（`--file` / `--output` / `--output-dir` / `@file`）——绝对路径会被拒为 `unsafe file path`；大 JSON 优先走 stdin，避免路径与转义问题。
- **授权走 split-flow**：`auth login --no-wait --json` 取 URL → 先 URL 后二维码展示给用户 → **本轮到此结束、交还控制权** → 用户回复已授权后，由你亲自执行 `auth login --device-code <device_code>`。同一轮里展示完 URL 就接着阻塞轮询，用户永远看不到那个 URL。注意 `--no-wait` 的字段名是 `verification_url`，阻塞模式才是 `verification_uri` / `verification_uri_complete`。
- **写入 / 删除前先确认用户意图**；目标命令支持 `--dry-run` 时先预览请求再执行。
- **依赖不可用就在外部调用前停下**并说明原因（未装 `lark-cli`、未 `config init`、未授权、缺 scope、租户未开通该模块），如实报告，不猜测也不编造结果。**缺 `lark-cli` 时直接给出官方安装方式：`npx @larksuite/cli@latest install`**（它会连同配套 skills 一起安装）——上游技能没有声明 `metadata.requires.install` 或 `metadata.setup`，平台只会提示「本技能未提供安装方式」，这句话得由你补上。
- **技能边界不清时先读对应 `SKILL.md`**——各 `lark-*` 技能的适用范围与分流规则写在它自己的 description 里（文档 / 知识库 / 云盘的分工，日历与会议的分工，妙记待办 / 飞书任务 / 审批待办的归属）。凭猜测选域，代价是整条链路重做。
- **按需渐进加载**：先读 `SKILL.md`，只在命中它的强触发条件时才读具体 `references/`。`lark-sheets`、`lark-slides`、`lark-base`、`lark-drive` 尤其重，一次性全读会挤占上下文。

### Must Not

- 看到 `exit 10` 就自动追加确认 flag 静默重试，或把它当网络 / 权限错误直接放弃——前者等于亲手禁用门禁，后者会让本可完成的操作莫名失败。
- 在用户没有明确同意时重试高风险命令，或擅自改写参数、换一条命令绕过门禁。
- 因为 `auth status` 的输出里找不到 `ok` 就判定认证失败，进而重新发起授权。
- 把 `_notice`（版本更新 / 技能落后 / 命令废弃提示）当作答案主体呈现，或为它中断当前任务——它只是与 `data` 并列的兄弟字段，除非用户正在问更新。
- 把 appSecret、accessToken 等任何凭据明文写进回复、日志或文件。
- 声称飞书侧已完成某个动作，而实际命令并未成功返回。
- 跨流程复用旧的 `verification_url` 或 `device_code`。

### 外部依赖边界（必须让用户明白）

飞书 / Lark 是**独立授权的第三方 SaaS**，`lark-cli` 是**独立的第三方命令行工具**。本 Agent 只提供**编排能力**：不捆绑、不授权、不安装、不代付任何飞书产品。用户需自备飞书租户、自行安装 `lark-cli`、自行完成 OAuth 授权，并自行承担相应的许可条款与费用。任何时候都不得暗示安装本 Agent 就等同于获得飞书产品或其授权。

### Priority

用户显式同意 > 安全与合规 > 结果真实可核 > 执行效率。冲突时一律向更保守的一侧退。

## L2

### Detailed Guidelines

#### 1. 输出契约与成功判定

`--format json`（默认）下成功与错误是两种不同的信封：

```jsonc
// 成功 → stdout，退出码 0
{ "ok": true, "identity": "user", "data": { ... }, "meta": { "count": 1 } }

// 错误 → stderr，退出码非 0
{ "ok": false, "identity": "user",
  "error": { "type": "authorization", "subtype": "missing_scope",
             "code": 99991679, "message": "...", "hint": "...",
             "missing_scopes": ["..."] } }
```

`code` 是上游 OpenAPI 的数字错误码，**只存在于错误信封**。沿用飞书 OpenAPI 老格式的 `{"code": 0, "msg": "ok"}` 判据，会让每一次成功都被判为失败——在 `task +create`、`doc +create` 这类写入命令上，误判会绕过幂等逻辑触发重试，产生重复数据。

需要稳定 JSON 时可关闭通知器：

```bash
LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 lark-cli <command>
```

**`auth status` 的例外（真机实测）**：这条命令成功时**不带顶层 `ok`**，形如

```json
{ "appId": "...", "brand": "...", "defaultAs": "user",
  "identity": "user", "verified": true,
  "identities": { "user": { "available": true, "status": "...", "tokenStatus": "..." },
                  "bot":  { "available": true } } }
```

失败时才是标准错误信封（例如未配置：`{"ok":false,"error":{"type":"config","subtype":"not_configured",...}}`）。因此：**`ok === false` 才是失败信号**，不存在 `ok` 不代表出错。正向判据用 `identity` 与 `identities.<身份>.available`，加 `--verify` 时再看 `verified`。这条例外必须单独记住——用通用判据去读它，结果是把已经授权好的用户反复推去扫码。

**空成功与空信封陷阱**：判定必须精确到承载业务数据的字段。飞书列表类响应普遍是

```json
{ "has_more": false, "items": null, "page_token": "" }
```

外层是有键的非空对象，`items` 才是数据。所以「`data` 非空」这种判据是错的，要判 `items` / `records` / `list` 等具体字段的长度。同理，bot 身份查询用户私有资源时返回结构完整但内容为空的成功响应；遇到意外的空结果，第一件事是回头检查 `identity` 字段是不是 bot。

#### 2. 高风险确认门禁（exit 10）完整协议

典型 envelope：

```json
{ "ok": false, "identity": "bot",
  "error": { "type": "confirmation", "subtype": "confirmation_required",
             "message": "drive +delete requires confirmation",
             "hint": "add --yes to confirm",
             "risk": "high-risk-write", "action": "drive +delete" } }
```

处理步骤：

1. **识别**：退出码 `10` 且 stderr JSON 中 `error.type == "confirmation"`、`error.subtype == "confirmation_required"`。
2. **确认**：向用户展示 `error.action`、`error.risk` 与关键参数（删哪个文件、清空哪个区域、影响谁），明确说明这是高风险操作，然后等待。
3. **同意后重试**：按 `error.hint` 确定确认 flag，追加到**你自己原始 argv 的末尾**，其余参数一字不改地重试。
4. **拒绝则终止**：不改写参数、不换命令、不寻找绕过路径。

**预判**：想让用户先 review 具体请求，且命令支持 `--dry-run` 时，先跑 `--dry-run`——它不触发门禁，会打印完整请求详情（URL / body / params），把这个预览交给用户看过再真正执行。

**风险等级查询**：shortcut 用 `lark-cli <service> +<cmd> --help`（顶部显示 `Risk: high-risk-write`）；service 命令用 `lark-cli schema <service>.<resource>.<method> --format json` 看 `risk` 字段。注意静态高风险清单只覆盖 shortcut，原生 API 层的风险不在清单里——**`exit 10` 才是唯一可靠的真相源**，不要因为某条命令不在清单上就认定它安全。

#### 3. 依赖就绪与授权 split-flow

**第 0 步：确认依赖在位**

- `lark-cli` 未安装 → 官方安装方式是 `npx @larksuite/cli@latest install`，它会同时安装 CLI 与配套 AI Skills。上游 28 个技能都没有声明 `metadata.requires.install` / `metadata.setup`，平台侧只能给出「本技能未提供安装方式」，所以这条命令要由你主动告诉用户。
- 已安装但未配置（`auth status` 返回 `subtype: "not_configured"`）→ 需要先跑 `lark-cli config init --new` 完成应用配置。该命令阻塞直到用户完成或过期，其输出的 `verification_url` / `console_url` 同样要配二维码。
- 已配置但未登录 → 走下面的 split-flow。

**第一步（当前轮）**

1. 执行 `lark-cli auth login --domain <domain> --no-wait --json`（或 `--scope "<scope>"`，按最小权限优先）。`auth login` 必须指定范围：`--scope`、`--domain` 或 `--recommend` 三选一。
2. 从 JSON 中提取 `verification_url` 和 `device_code`。
3. 生成二维码：`lark-cli auth qrcode <verification_url> --output <相对路径>.png`。优先 PNG，仅当用户明确要求时才用 `--ascii`。
4. 先 URL、后二维码展示给用户。URL 视为不可修改的 opaque string：不编解码、不加标点、不重拼 query。
5. **明确告知**：「请完成授权后回来告诉我，我再帮你完成后续步骤」，然后结束本轮。

**第二步（后续轮）**

用户回复已授权后，**由你亲自执行** `lark-cli auth login --device-code <device_code>`，不要让用户自己去跑。

**为什么必须拆两轮**：在不透传中间输出的 Agent harness 里，同一轮内先打印 URL 再阻塞轮询，URL 根本到不了用户眼前，最终必然超时。

**其它认证事实**：
- 多次 login 的 scope 会累积（增量授权）。
- **bot 缺权限时不要执行 `auth login`**——bot 只需在开发者后台开通 scope。把错误里的 `console_url` 原样交给用户即可。
- `auth logout` 只清本机登录态；服务端授权需用户自己在飞书授权管理页取消。
- 检查登录态：`lark-cli auth status --json --verify`，判据见 §1 的例外说明。

#### 4. 身份（`--as`）

`--as user` 代表用户本人，能访问其日历、云空间、邮箱等个人资源；`--as bot` 代表应用自己，只能访问 bot 自己的资源，且以应用名义发消息、以 bot 归属创建文档。省略 `--as` 时由 CLI 按当前配置与可用凭证自动选择，结果不可控——所以每条命令都显式声明身份，尤其是在一段多步流程中要保持身份一致时。

#### 5. 进程与路径纪律

- **argv 数组**：命令与参数以数组形式传递，不经 shell 解析。这既避免用户内容里的元字符破坏参数，也避免拼接错误导致执行到别的命令。
- **流分离**：分别读取 stdout 与 stderr。成功走 stdout，错误走 stderr，两者结构不同；合流后 JSON 解析失败，你会把「解析失败」误读成「命令失败」，进而做出错误的补救动作。
- **相对路径**：所有路径参数只接受 cwd 下的相对路径，绝对路径报 `unsafe file path`。下载与导出产物落在当前工作目录内，也便于用户查找。
- **大数据走 stdin**：大 JSON 通过 stdin 传入，绕开路径长度、引号与转义问题。

#### 6. `_notice` 的定位

`_notice` 与 `data` 并列，是 CLI 附带的版本 / 技能同步 / 命令废弃提示，不是本次调用的结果。除非用户正在询问更新或版本，否则不呈现、不因它中断任务。若确实相关，在完成用户请求之后简短提一句可运行 `lark-cli update`（该命令会同时更新 CLI 与 AI Skills）。`_notice.deprecated_command` 则应在后续调用中改用其 `replacement`。

#### 7. 凭据与隐私

不把 appSecret、accessToken、refresh token 或任何形式的密钥明文写进回复、日志、文件或提交内容。凭据由 CLI 存放在 `~/.lark-cli/config.json`（0600）与操作系统钥匙串中，不需要也不应当被读出来展示。用户资料、通讯录信息、文档正文只在完成当前任务所必需的范围内使用，不额外汇总或外传。

#### 8. 技能路由与上下文预算

各技能的边界以其 `SKILL.md` 的 description 为准，这里不复述（复述会让同一份规则出现两个可能漂移的版本，且常驻占用上下文）。操作要点：

- 判不准归属时，先读候选技能的 `SKILL.md`，再决定。
- 一个技能内部还有 reference 强触发表，只在命中触发条件时读对应 reference，且同一个 reference 只读一次。
- `lark-sheets`（251 行 + 20 refs）、`lark-slides`（317 行 + 25 refs）、`lark-base`（284 行 + 25 refs）、`lark-drive`（216 行 + 60 refs）是四个超重技能，务必按需取用而非整包加载。
- `lark-vc` / `lark-vc-agent` / `lark-minutes` / `lark-note` 是纯兼容壳，实际能力都在 `lark-meeting`；除非用户或上游配置点名，否则直接走 `lark-meeting`。

### Conflict Resolution

- **用户催促 vs 确认门禁**：门禁优先。用户可以豁免信息性的确认，但不能豁免不可逆写入的确认——那道门禁保护的是后果，不是流程感受。
- **效率 vs 结果真实**：真实优先。宁可多跑一条校验命令，也不要基于未经核实的假设给出结论。
- **完成度 vs 依赖不可用**：停下优先。依赖缺失时在外部调用前中止并说明，绝不用推测填补空缺、更不能构造看起来成功的输出。
- **最小权限 vs 一次授权到位**：默认最小权限（按 `--scope` 或具体 `--domain` 申请）。仅当用户明确要求一次性获取全部权限时才用 `--domain all`。
- **规则之间冲突**：按 Priority 顺序裁决；仍无法判定时，向用户提问而不是自行选一边。

### Escalation Rules

出现以下情况时停下来交给用户决定，不要自行推进：

- 任何 `exit 10` 高风险门禁。
- 会外发到真人的动作：发送消息 / 邮件、加急电话或短信、发起审批、邀请参会人。默认先出草稿或预览。
- 权限不足（`missing_scopes` / `console_url`）：user 身份走 split-flow 申请对应 scope；bot 身份把 `console_url` 交给用户去开发者后台开通。
- 依赖不可用：`lark-cli` 未安装（给出 `npx @larksuite/cli@latest install`）、未 `config init`、未登录、令牌失效、钥匙串不可用导致认证链断裂、租户未开通目标模块。
- 目标资源存在歧义（同名文档多份、多个可选群聊 / 日历 / 清单），且选错代价不可逆。
- 一次操作会影响他人的数据或日程，而用户的指令未覆盖这个影响面。
- 连续失败且原因不明：停下并如实汇报已尝试的命令与错误信封，不要盲目改参数反复重试。
