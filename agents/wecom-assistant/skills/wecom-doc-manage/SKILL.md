---
name: wecom-doc-manage
description: >-
  企业微信文档的"文件级"公共管理：搜索文档、文档改名、添加协作成员与权限、设置链接加入规则。
  对**全部四种文档类型**（在线文档 doc / 在线表格 sheet / 智能表格 smartsheet / 智能文档 smartpage）
  统一生效，并且是本技能集**唯一的文档搜索入口**。用户说"找一下那个文档""我最近看过/建过哪些文档"
  "把这个文档改名""把张三加进这个文档""给这个文档开个可编辑链接""这个文档能不能让外部的人看"
  时用它。不读写任何文档正文——Word 类正文找 wecom-doc，在线表格数据找 wecom-sheet，
  智能表格记录找 wecom-smartsheet，智能文档内容找 wecom-smartpage。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - doc-manage
---

# 企业微信文档公共管理（搜索 / 改名 / 权限 / 加入规则）

企业微信的四种在线文档共用同一套"文件级"管理接口。本技能负责的是**文件这个壳**——
它叫什么、谁能进来、进来能干什么、以及怎么把它找出来——**不碰文件里的一个字**。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 安装 / 版本 ≥ 1.2.0 / 授权状态），并遵守其中的 ID 禁露约束与风险确认约定。

## 文档类技能的分工边界（选错技能是最高频的失败原因）

| 用户想做的事 | 归属技能 |
|---|---|
| **搜索任何文档**（不论类型） | **本技能**（唯一入口） |
| **改文档名 / 加成员 / 改权限 / 改加入规则**（不论类型） | **本技能** |
| 读写**在线文档（Word 类）正文** | `wecom-doc` |
| 读写**在线表格数据 / 增删子表** | `wecom-sheet` |
| 读写**智能表格**字段与记录 | `wecom-smartsheet` |
| 读写**智能文档 / 智能主页**内容 | `wecom-smartpage` |

反过来也成立：上面四个内容技能**都不做**搜索、改名、权限、加入规则，遇到就转交本技能。
本技能拿到 `docid` 之后，**若用户还要读/写正文，必须按文档类型转交对应内容技能**，
不得自己拼"读正文"的命令。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 搜索文档（含"最近浏览 / 最近创建"） | `wecom-cli doc search` | read |
| 修改文档名称 | `wecom-cli doc names update` | write-low |
| 添加协作成员并设置其权限 | `wecom-cli doc members update` | **write-high（权限扩散）** |
| 设置链接加入规则（企业内 / 企业外） | `wecom-cli doc rules update` | **write-high（权限扩散，可放开企业外）** |

> 本技能的两个 write-high 属**权限扩散**类：它们不改一个字，却直接改变"谁能看到这份文档的全部内容"。
> 后果不可逆（已经看过的人看过了），也没有 CLI 侧的撤销接口。
> 确认要求比其他 write-high 更重，见下方对应场景。

## `docid` 的获取与展示规则

`docid` 是四种文档的统一标识，**只能内部流转，禁止自造，禁止展示给用户**。三级获取优先级：

1. **从用户给的链接提取（优先）**：URL 形如 `https://doc.weixin.qq.com/<type>/<docid>?scode=...`，
   取 `/<type>/` 后、`?` 前的一段。
2. **用本技能搜索获得（备选）**：用户只给了文档名或关键词时走 `doc search`。
3. **用户直接给出完整 `docid`**：可直接用。

**类型判据**（决定后续转交给哪个内容技能）：

| 判据 | 结论 |
|---|---|
| `doc search` 返回的 `doc_type` 字段 | 最可靠，优先用它 |
| `docid` 以 `a1_` / `b1_` 开头 | 智能文档（`b1_` 是**发布态只读**，要编辑必须拿 `a1_` 编辑态） |
| `docid` 以 `s3_` 开头 | 智能表格 |
| 域名 `doc.weixin.qq.com` / `page.weixin.qq.com` | 在线文档域 |
| 域名 `drive.weixin.qq.com` | **微盘**，不是在线文档，转 `wecom-disk`，切勿混用 |

**展示规则**：给用户看文档时一律写成可点击链接 `[doc_name](url)`，`url` 取接口返回的 `url` 字段原样使用。
需要提创建者时用返回里的 `creator_name`（后台注入的可读显示名），**禁止**用 `creator_userid`。

## 场景一：搜索文档

### 用户会怎么说

"帮我找下产品的待办 tool 文档" / "我最近看过哪些文档" / "我这周建的文档" /
"有没有张三参与的那个方案" / "把上次那个周报表格翻出来"

### 先按意图分派参数，再发命令

**禁止所有参数都不传，也禁止传 `{}`。** 四个分支，先判定意图再组装：

| 分支 | 触发说法 | 必传参数 | 建议参数 |
|---|---|---|---|
| (a) 按内容找 | "找一下 X""有没有关于 X 的文档" | `--keywords`（不得为空） | `--search-scope title_content --sort-by best_match` |
| (b) 我最近浏览 / 与我相关 | "我最近看过""包含我的""我参与的" | `--visitor-userids <当前 userid>` | `--sort-by best_match --opened-after <近 7 天>` |
| (c) 某人参与的 | "张三参与的""包含李四的文档" | `--visitor-userids <他人 userid>` | `--sort-by best_match` |
| (d) 我最近创建 | "我建的""我这周新建的文档" | `--creator-userids <当前 userid>` | `--sort-by create_time --created-after <近 7 天>` |

- 意图不属于 (b)(c)(d) 的，**一律按 (a) 处理，`--keywords` 必填**。
- `userid`（`wo` 前缀）**必须**先经 `wecom-contact` 由姓名解析，
  当前用户的 `userid` 经 `wecom-shared` 的 `identity whoami` 获取。**禁止把姓名当 userid 拼接**。
- 分支 (c) **必须提醒用户**：结果只包含**你自己也有权限访问**的那部分文档；
  对方独占、你无权访问的文档不会出现。本接口**不能**用来窥探他人的文档列表。

### `keywords` 必须先分词再组装

**禁止把用户整句 query 当成一个 keyword 传进去**（这是搜不到东西的头号原因）。处理流程：

1. 对 query 做中英文分词，剔除"帮我 / 找下 / 的 / 文档"这类口语与停用词。
2. 从剩余 token 中挑出真正承载检索意图的**必传 token**（专有名词、产品名、功能名等强区分度词），
   其余作为辅助 token。
3. 组装数组：**第 1 个元素 = 所有必传 token 用空格拼接**（只拼必传的），后续元素依次是各单独 token。
4. 必传 token 只有 1 个时，第 1 个元素就是它本身，不必重复追加（query `"周报"` → `["周报"]`）。

例：query `"帮我找下产品的待办tool文档"` → 剔除通用词后剩 `["产品","待办","tool"]`，
必传 token 判为 `["待办","tool"]`，`"产品"` 作辅助：

```bash
wecom-cli doc search \
  --keywords '待办 tool' '待办' 'tool' '产品' \
  --search-scope title_content \
  --sort-by best_match \
  --limit 10
```

> **数组参数的写法**：`--keywords` / `--doc-types` / `--creator-userids` / `--visitor-userids`
> 在 `--help` 里标注为 `[<str>...]`，即一个 flag 后面跟多个空格分隔的值（如上例）。
> 若某个环境下 CLI 拒绝这种多值形态，**改用等价的 `--json` 形态**：
> `--json '{"keywords":["待办 tool","待办","tool","产品"],"search_scope":"title_content","limit":10}'`。
> 两者产生同一个请求体。（多值形态取自 `--help` 的类型标注，**未经实际调用验证**。）

### 其它常用形态

只按类型 + 时间窗筛，不做关键词匹配（`keywords` 仍必须出现，给一个真实词，不要给空串）：

```bash
wecom-cli doc search \
  --keywords '周报' \
  --doc-types doc sheet \
  --created-after '2026-08-01 00:00:00' \
  --sort-by create_time \
  --limit 20
```

"我最近浏览过的文档"——这类**只按条件过滤、不做关键词匹配**的场景，`keywords` 要传**空数组**。
命名参数形态表达不了空数组，因此改用 `--json`（`<my_userid>` 来自 `identity whoami`，
`<7天前>` 按当前时间算）：

```bash
wecom-cli doc search --json '{"keywords":[],"visitor_userids":["<my_userid>"],"opened_after":"<7天前 YYYY-MM-DD HH:mm:ss>","sort_by":"best_match","limit":20}'
```

> `keywords` 是 schema 的 `required` 字段，但 `minItems` 为 0——**字段必须出现，数组可以为空**。
> 空数组用于纯过滤；**不要**为了凑数传空字符串 `[""]`，那是一个真实的空关键词。
> 若返回为空，改用分支 (a) 补真实关键词重试。

### 结果怎么展示

- **用 markdown 无序列表逐条展示，禁止用表格**。表格会强制列对齐，把时间、类型等噪声一起推到用户面前。
- 最多展示 10 条。即使只有 2~3 条也用列表。
- 每条首行写成 `- [doc_name](url)`，可补一行"最近修改：`modify_time`"这类可读信息。
- **`docid` 与 `creator_userid` 绝不出现在回复里。**
- 结果 **>1 条**：按序号 + 可读信息列出候选，**等用户选定**再做后续动作，不得自行挑一个。
- 结果 **=0 条**：告知没搜到，追问用户能否补充更多关键词线索，**不要**自己换关键词反复重试超过一轮。

### 命中"读不了正文"的类型时

`ppt` / `journal` / `collect` / `mind` / `flow` / `pdf` 这些类型，本技能集**没有任何**读取正文的能力。
用户要看内容时直接说明暂不支持读取，给出 `[doc_name](url)` 让其在企业微信客户端打开。

### 分页

返回 `has_more=true` 时，用上一页的 `next_cursor` 作为 `--cursor` 续取。
也可以用 CLI 的 `--page-count <n>` 自动翻页（输出转 NDJSON，每行一页）。
`next_cursor` 属于 ID 类字段，**只在内部流转，不展示**。

## 场景二：修改文档名称

### 用户会怎么说

"把这个文档改名叫 X" / "这个表格标题改成 X" / "重命名一下"

改名是 write-low：改错了再改回来即可，不需要走高风险确认。但仍要先确认操作的是**哪一份**文档
（多候选时按场景一的规则让用户选）。

```bash
wecom-cli doc names update --docid '<docid>' --new-name '2026 年 Q3 项目周报'
```

成功返回空对象。回复用户时说清"《旧名》已改名为《新名》"，并给出 `[新名](url)`。

## 场景三：添加协作成员 / 设置成员权限

### 用户会怎么说

"把张三加到这个文档里" / "让李四能编辑这份表格" / "给产品组开个只读权限"

> ⚠️ **高风险操作（权限扩散）**：这会把一份文档的读或写权限授予指定的人，
> 被授权者立即能看到文档的**全部内容**；权限一旦扩散出去，看过的内容无法收回，
> CLI 也没有"移除成员"的接口——**加错了本技能删不掉，只能让用户去企业微信客户端手动移除**。
> 执行前必须向用户复述：
> **「将把《\<文档名\>》的\<权限项\>改为\<具体值\>，此操作会让\<谁\>能访问这份文档的全部内容」**
> 并取得明确同意；用户未明确同意时不得执行。

复述里三个占位必须都填成**可读信息**，例如：

> 将把《2026 年 Q3 项目周报》的**协作成员权限**改为**张三 = 可编辑、李四 = 仅浏览**，
> 此操作会让**张三和李四**能访问这份文档的全部内容。确认执行吗？

用户回复含糊（"嗯""你看着办""都行"）**不算**明确同意，需要再确认一次。

### 前置：姓名必须先解析成 userid

用户给的是姓名时，**必须**先用 `wecom-contact` 的 `contact users search` 解析成 `userid`（`wo` 前缀）。
禁止把姓名当 `userid` 拼接，禁止凭记忆编造。解析出多个同名候选时，按可读信息（部门 / 职务）
让用户选定后再继续。

### 命令

`--add-member-list` 是嵌套 JSON，结构为 `{"items":[{...},{...}]}`：

```bash
wecom-cli doc members update \
  --docid '<docid>' \
  --add-member-list '{"items":[{"userid":"<userid_1>","user_type":"user","user_auth":"edit"},{"userid":"<userid_2>","user_type":"user","user_auth":"read"}]}'
```

| 字段 | 取值 | 说明 |
|---|---|---|
| `items[].userid` | `wo` 前缀字符串 | 经 `wecom-contact` 解析所得 |
| `items[].user_type` | `user` | 成员类别；当前只用到"用户" |
| `items[].user_auth` | `manager` / `edit` / `read` | 管理员 / 可编辑 / 仅浏览 |

> **`user_type` 与 `user_auth` 的取值来自上游 `wecomcli-doc-manage` 的 reference 文档，
> 不是 schema 约束**——`doc.members.update` 的 JSON Schema 把这两个字段声明为无 enum 的自由字符串。
> 传了别的值 schema 不会拦，**错误会在服务端才暴露**。不要发明新取值。

成功返回空对象。执行后向用户汇报"已把 X 加为可编辑成员"，用姓名不用 ID。

### 权限档位怎么选（不要默认给高权限）

| 用户说法 | 应选 |
|---|---|
| "让他看看""发给他参考" | `read` |
| "让他一起写""他要填表" | `edit` |
| "让他管这个文档""他来分配权限" | `manager` |

用户没说清楚时**问一句**，不要默认给 `edit` 或 `manager`。
"加进来"这个说法**本身不构成**授予编辑权的明确表示。

## 场景四：设置文档加入规则（企业内 / 企业外）

### 用户会怎么说

"这个文档发链接就能进" / "关掉加入审批" / "让外部的人也能看" /
"给客户发个只读链接" / "开放给企业外"

> ⚠️ **高风险操作（权限扩散，本技能集风险最高的一档）**：本方法改的是"拿到链接的人能不能进、
> 进来是什么权限"。把 `corp_external_join_auth` 设成 `read` / `edit` / `apply`
> 意味着**企业外的人**——不在你们企业微信通讯录里的任何人——只要拿到链接就能访问这份文档，
> 这是**数据外泄**级别的变更；一旦扩散，内容无法收回，CLI 也没有撤销接口。
> 关闭 `enable_member_join_admin_check`（成员加入确认）同样是把管理员的人工闸门拆掉。
> 执行前必须向用户复述：
> **「将把《\<文档名\>》的\<权限项\>改为\<具体值\>，此操作会让\<谁\>能访问这份文档」**
> 并取得明确同意；用户未明确同意时不得执行。

**涉及企业外时必须额外单独说明一句后果，并单独取得一次同意**，例如：

> 将把《2026 年 Q3 项目周报》的**企业外成员加入权限**改为**仅浏览（read）**，
> 此操作会让**企业外任何拿到该文档链接的人**能访问这份文档的全部内容。
> **这份文档将不再限于本企业内部可见，链接被转发出去后无法收回。** 确认执行吗？

另外三条硬规则：

- 用户只说"发个链接就能看"**不等于**要开企业外。默认只动 `corp_internal_join_auth`；
  要动企业外**必须**由用户明确说出"企业外 / 外部 / 客户 / 合作方"之类的对象，
  含糊时**必须追问**"是仅企业内部，还是也包括企业外的人？"。
- **不确定文档里有什么就不要开企业外。** 用户要求开放企业外、而你并不知道文档内容时，
  先提示"这份文档的内容我没有读过，开放给企业外前请你确认其中不含敏感信息"。
- 想收紧（关闭外部访问）时用 `corp_external_join_auth: "deny"`，这是唯一的"关"值；
  **不传该字段等于保持现状，不是关闭**。

### 参数与取值

| 参数 | 必填 | 取值 | 说明 |
|---|:--:|---|---|
| `docid` | 是 | 字符串 | 目标文档 |
| `enable_member_join_admin_check` | 是 | `true` / `false` | 是否开启成员加入确认（管理员审批闸门） |
| `corp_internal_join_auth` | 否 | `edit` / `read` / `apply` | 企业内成员加入权限 |
| `corp_external_join_auth` | 否 | `edit` / `read` / `apply` / `deny` | 企业外成员加入权限 |

- 两个 `*_join_auth` **仅当 `enable_member_join_admin_check=false` 时才生效**；
  开着审批闸门时传了也不起作用。
- 不传 `*_join_auth` = **保持现状**，不是"清空"也不是"关闭"。
- `apply` = 需要申请，`deny` = 拒绝（仅企业外可用）。

### 命令：必须用 `--json`

**`--enable-member-join-admin-check` 在 CLI 里是一个不带值的 bool flag**
（`--help` 显示为 `--enable-member-join-admin-check` 而非 `<bool>`）：
写上它 = `true`，不写 = 字段缺失，而该字段是**必填**的。
也就是说**用命名参数形态根本表达不出 `false`**。
因此本方法**统一用 `--json` 形态**，两种取值都能准确表达：

开启成员加入确认（此时两个 `*_join_auth` 不生效，不必传）：

```bash
wecom-cli doc rules update --json '{"docid":"<docid>","enable_member_join_admin_check":true}'
```

关闭加入确认、企业内可编辑、**明确拒绝企业外**（推荐的默认收紧姿势）：

```bash
wecom-cli doc rules update --json '{"docid":"<docid>","enable_member_join_admin_check":false,"corp_internal_join_auth":"edit","corp_external_join_auth":"deny"}'
```

确实要放开企业外只读（**必须已完成上面的额外确认**）：

```bash
wecom-cli doc rules update --json '{"docid":"<docid>","enable_member_join_admin_check":false,"corp_internal_join_auth":"edit","corp_external_join_auth":"read"}'
```

成功返回空对象。执行后如实汇报改成了什么，并再次提示企业外可见的范围。

## 参数速查

| 方法 | 必填参数 | 高频可选参数 |
|---|---|---|
| `doc search` | `--keywords` | `--search-scope` `--doc-types` `--creator-userids` `--visitor-userids` `--created-after/-before` `--opened-after/-before` `--sort-by` `--limit` `--cursor` |
| `doc names update` | `--docid` `--new-name` | 无 |
| `doc members update` | `--docid` `--add-member-list` | 无 |
| `doc rules update` | `--docid` `--enable-member-join-admin-check` | `--corp-internal-join-auth` `--corp-external-join-auth` |

**枚举取值**（均来自 schema）：

- `search_scope`：`title` / `title_content`（默认） / `content`
- `sort_by`：`best_match`（默认） / `create_time` / `modify_time`
- `doc_types`：`doc` / `sheet` / `smartsheet` / `smartpage` / `collect` / `ppt` / `mind` / `flow` / `journal` / `pdf`
- `corp_internal_join_auth`：`edit` / `read` / `apply`
- `corp_external_join_auth`：`edit` / `read` / `apply` / `deny`

**上限**（schema 的 `maxItems` / `maximum`）：
`keywords` ≤20、`doc_types` ≤10、`creator_userids` ≤50、`visitor_userids` ≤50、
`limit` ≤100（默认 10）、`hl_fragment_len` ≤512（默认 100）、`number_of_fragments` ≤10（默认 1）。

完整参数请用 `wecom-cli doc <resource> <method> --help` 现查，不要凭记忆补参数。

## 易错点

- **搜索是本技能的专属能力**：`wecom-doc` / `wecom-sheet` / `wecom-smartsheet` / `wecom-smartpage`
  都没有搜索方法。用户说"找一下那个表格"时也走本技能，然后再按 `doc_type` 转交。
- **整句 query 当单个 keyword 传 = 搜不到**。必须先分词，第一个元素是必传 token 的空格拼接串。
- **`--keywords` 是必填**：schema 的 `required` 里只有它，四种意图分支都不能省略这个字段；
  但它的 `minItems` 是 0，纯过滤场景传**空数组**（只能用 `--json`），不要传 `[""]`。
- **`doc search` 只返回调用者自己有权限的文档**：搜不到不等于文档不存在，可能是无权访问。
  用 `visitor_userids` 查他人时**必须**把这条提醒说给用户。
- **`--enable-member-join-admin-check` 是 bool flag，不接受值**：`--enable-member-join-admin-check false`
  会被解析成"开启 + 一个多余的位置参数"，语义完全相反。要传 `false` 只能用 `--json`。
- **不传 `*_join_auth` = 保持现状**，不是关闭。要关企业外必须显式传 `"deny"`。
- **`user_type` / `user_auth` 没有 schema enum 兜底**：值写错时本地校验不报错，服务端才失败。
  只用 `user` 和 `manager`/`edit`/`read`。
- **`doc members update` 只能加人，不能删人**：CLI 没有移除成员的方法。加错了要引导用户去
  企业微信客户端手动移除，不要假装能撤销。
- **`docid` 禁止自造、禁止展示**；`creator_userid` / `cursor` / `next_cursor` 同样禁止展示。
  要展示创建者用 `creator_name`，要展示文档用 `[doc_name](url)`。
- **`b1_` 开头的智能文档是发布态只读**，拿它去编辑会失败，需要对应的 `a1_` 编辑态。
- **`drive.weixin.qq.com` 是微盘，不是在线文档**，本技能的四个方法对它都不适用。
- **改名 / 加成员 / 改规则三个方法对 `ppt` / `collect` / `mind` / `flow` / `journal` / `pdf` 不适用**，
  这些类型只在搜索的 `doc_types` 过滤里可用。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-doc-manage`。
