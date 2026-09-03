---
name: wecom-sheet
description: >-
  企业微信**在线表格（sheet）**的数据与子表操作：新建表格、把本地 CSV/Excel 导入成在线表格、
  读取表格基础信息与子表列表、按 A1 区域读数据、更新指定区域单元格、末尾追加一行、
  添加子工作表、删除子工作表。用户说"表格""在线表格""excel 表格""工作表""子表""某某表第几行"
  或给出 https://doc.weixin.qq.com/sheet/xxx 链接时用它。搜索表格、改表格名、加成员、改权限
  找 wecom-doc-manage；智能表格（docid 以 s3_ 开头 / smartsheet 链接）找 wecom-smartsheet；
  Word 类在线文档找 wecom-doc。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - sheet
---

# 企业微信在线表格（sheet）数据与子表操作

在线表格 = 企微版的 Excel：一个文档里有若干**子工作表（subsheet）**，每张子表是行列网格。
本技能负责这些格子里的数据和子表本身的增删——**不负责**这份表格文件叫什么名字、谁能打开它。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 安装 / 版本 ≥ 1.2.0 / 授权状态），并遵守其中的 ID 禁露约束与风险确认约定。

## 文档类技能的分工边界

| 用户想做的事 | 归属技能 |
|---|---|
| 搜索任何文档（含表格，唯一入口） | `wecom-doc-manage` |
| 改文档名 / 加成员 / 改权限 / 改加入规则（任何类型） | `wecom-doc-manage` |
| 读写在线文档（Word 类）正文 | `wecom-doc` |
| **读写在线表格数据 / 增删子表** | **本技能** |
| 读写智能表格字段与记录 | `wecom-smartsheet` |
| 读写智能文档 / 智能主页内容 | `wecom-smartpage` |

### 在线表格 vs 智能表格（选错就全盘失败，先判这一段）

两者都是"表"，但**是完全不同的两套接口**，`sheet *` 命令对智能表格一概无效。

| 判据 | 在线表格（本技能） | 智能表格（`wecom-smartsheet`） |
|---|---|---|
| 链接 | `https://doc.weixin.qq.com/sheet/...` | `https://doc.weixin.qq.com/smartsheet/...` |
| `docid` 前缀 | 其它 | **`s3_`** |
| `doc search` 的 `doc_type` | `sheet` | `smartsheet` |
| 数据模型 | 行列网格 + A1 区域 | 字段（field）+ 记录（record）+ 视图 |
| 用户说法 | "excel""单元格""A1:C10""第 3 行" | "字段""记录""视图""筛选条件""看板" |

用户要的是**字段 / 记录 / 筛选 / 视图 / 分组统计**这类结构化能力时，即使他嘴上说"表格"，
也要先确认是不是智能表格——在线表格没有这些概念。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 新建在线表格（可带初始数据） | `wecom-cli sheet create` | write-low |
| 导入本地 CSV / Excel 为在线表格 | `wecom-cli sheet import` | write-low |
| 读取表格基础信息与子表列表 | `wecom-cli sheet get` | read |
| 读取子表指定区域的数据 | `wecom-cli sheet ranges get` | read |
| 在子表末尾追加一行 | `wecom-cli sheet rows append` | write-low |
| 添加子工作表 | `wecom-cli sheet subsheets add` | write-low |
| 更新指定区域的单元格 | `wecom-cli sheet contents update` | **write-high（不可逆覆盖）** |
| 删除子工作表 | `wecom-cli sheet subsheets delete` | **write-high（不可逆删除）** |

## 两个必须先拿到的 ID

### `docid`（文档级）

**只能内部流转，禁止自造，禁止展示给用户**。三级获取优先级：

1. **从用户给的链接提取（优先）**：`https://doc.weixin.qq.com/sheet/<docid>?scode=...`，
   取 `/sheet/` 后、`?` 前的一段。
2. **用 `wecom-doc-manage` 搜索获得（备选）**：用户只给了表格名或关键词时。
   多候选时按可读信息让用户选定，不得自行挑一个。
3. **用户直接给出完整 `docid`**：可直接用。

展示给用户时一律写成 `[doc_name](url)`，用接口返回的 `url` 原样。

### `sheet_id`（子表级）——**唯一来源是 `sheet get`**

除 `create` / `import` / `get` 外，**其余 5 个方法都要 `sheet_id`**，而它**只能**取自
`sheet get` 返回的 `sheets[]`。**禁止**把子表名称、序号、`Sheet1` 之类的猜测值当 `sheet_id`。

```bash
wecom-cli sheet get --docid '<docid>'
```

返回：

| 字段 | 说明 |
|---|---|
| `sheets[]` | 子表列表，每项含 `sheet_id` / `title`（子表名）/ `row_count` / `column_count` / `data_range` |
| `sheets[].data_range` | **有内容的区域**，A1 表示法；空表时为**空字符串** |
| `name` | 文档名称 |
| `url` | 文档链接 |

用户说"第二个子表""销售那一页"时，用 `title` 去匹配 `sheets[]` 拿对应的 `sheet_id`；
匹配不唯一时列出 `title` 让用户选，**不要**把 `sheet_id` 给用户辨认。

## 场景一：新建在线表格

### 用户会怎么说

"建个表格记一下下周排期" / "新建一个在线表格，表头是姓名/部门/工时"

**先判 create 还是 import**：用户提到**具体文件路径**、或明确说"导入 / 用这个文件建"
→ 走场景二的 `import`。`sheet create` **不接受任何文件路径参数**。

### 建一张空表

```bash
wecom-cli sheet create --doc-type sheet --doc-name '2026 年 9 月排期表'
```

### 建表并写入初始数据

`--grid-data` 是嵌套 JSON。结构：`start_row` / `start_column` 从 **0** 起，
`rows[].values[]` 每项是一个单元格。

```bash
wecom-cli sheet create \
  --doc-type sheet \
  --doc-name '2026 年 9 月排期表' \
  --grid-data '{"start_row":0,"start_column":0,"rows":[{"values":[{"cell_value":{"text":"姓名"},"data_type":"TEXT"},{"cell_value":{"text":"部门"},"data_type":"TEXT"},{"cell_value":{"text":"工时"},"data_type":"TEXT"}]},{"values":[{"cell_value":{"text":"张三"},"data_type":"TEXT"},{"cell_value":{"text":"研发"},"data_type":"TEXT"},{"cell_value":{"number":40},"data_type":"NUMBER"}]}]}'
```

返回 `docid` 与 `url`。给用户 `[2026 年 9 月排期表](url)`。

> ⚠️ **务必显式传 `--doc-type sheet`**。`sheet create` 与 `doc create` 在后端是**同一个方法**
> （请求体都是 `OaDocCreateReq`，靠 `doc_type` 区分），而 `doc_type` 的 schema 默认值是 **`doc`**。
> 上游 `wecomcli-sheet` 与 R2 报告的示例都没有传它——`wecom-cli` 是否会因为命令路径是 `sheet`
> 而自动注入 `doc_type=sheet`，**当前未实测确认**。显式传上是零成本的保险：
> 传对了不会有副作用，漏传一旦 CLI 不注入就会建出一篇 doc 文档而不是表格。
> 用 `--json` 手写完整请求体时同样**必须**带 `"doc_type":"sheet"`。

## 场景二：导入本地 CSV / Excel 为在线表格

### 用户会怎么说

"把这个 excel 传到企微上" / "导入这个 csv" / "用这份表格文件建个在线表格"

支持 `.csv` / `.xls` / `.xlsx`。

```bash
wecom-cli sheet import \
  --doc-type sheet \
  --file-name '销售明细.xlsx' \
  --file-path '/abs/path/销售明细.xlsx'
```

| 参数 | 说明 |
|---|---|
| `--doc-type` | **必须显式传 `sheet`**，见下方易错点 |
| `--file-name` | 含后缀的文件名，**决定导入后的文档标题**，业务据此判断源文件类型 |
| `--file-path` | 源文件本地绝对路径（与 `--file-content` 二选一） |
| `--passwd` | Office 文件加密密码（若有） |
| `--append-doc-id` | 传了则**导入追加到已有表格上**（子表名重复会自动重命名） |

返回 `docid` / `url` / `task_id` / `task_status`（`succ` / `fail` / `processing`）。
`succ` 才算成功，`processing` 要如实说明仍在处理，`fail` 把错误原样告知，**不要假装成功**。

## 场景三：读取表格数据

### 用户会怎么说

"这个表里有什么" / "看下销售表 A 列" / "帮我统计一下这张表的总金额"

### 两步：先 `sheet get` 拿子表，再 `sheet ranges get` 读数据

```bash
# 第一步：拿 sheet_id 与 data_range
wecom-cli sheet get --docid '<docid>'

# 第二步：读区域数据
wecom-cli sheet ranges get \
  --docid '<docid>' \
  --sheet-id '<上一步 sheets[] 里的 sheet_id>' \
  --range 'A1:C100'
```

### `--mode` 怎么选（选错会拿到没法用的数据）

| 场景 | `--mode` | `--range` | 返回 |
|---|---|---|---|
| 普通读取 / 查看 / 展示（**默认**） | `default`（不传即此值） | **必传** | `grid_data`：含每格的值、格式、数据类型 |
| 用户明确要**统计 / 计算 / 聚合分析**（求和、平均、分组、透视、跑数据分析） | `csv` | 被忽略 | `content`（CSV 原文）或 `file_path`（落盘路径） |

- `mode=default` 时 `--range` **必传**（A1 表示法，如 `A1:C100`）。
  范围可以直接取 `sheet get` 返回的 `sheets[].data_range`——那是"有内容的区域"，最省事。
  `data_range` 为空字符串说明**这张子表是空的**，不必再读。
- `mode=csv` 且返回 `file_path` 时，**必须再用文件读取工具把该路径读进来**才能消费；
  返回 `content` 时直接用。向用户汇报时**不展示本地路径**。

### 展示数据的规矩

- 展示给用户时用 markdown 表格或列表都可以（这里是真表格数据，不是搜索结果）。
- **不展示 `docid` / `sheet_id`**；提到子表时用 `title`，提到文档时用 `[name](url)`。
- 数据量大时先给摘要（多少行、有哪些列），再问用户要看哪一部分，不要一次性倾泻几百行。

## 场景四：追加一行数据

### 用户会怎么说

"往表里加一行" / "记一条：张三 研发 40 小时" / "把今天的数据补进去"

### 追加 vs 覆盖的裁定规则（每次写入前都要过一遍）

- **默认追加**：用户用"写入 / 写到 / 记录 / 补充 / 加进去 / 记一下 / 追加"等**中性动词**，
  且没有明确要求清空或替换 → 走 `rows append`。
- **仅显式覆盖**：只有出现"覆盖 / 重写 / 替换 / 清空重写 / 整个换成 / 改成"这类**强语义词**、
  或用户点名了具体单元格区域（"把 B3 改成 50"）时，才走 `contents update`。
- 判不准就**按追加处理**——追加错了删掉那行即可，覆盖错了原值就没了。

`rows append` 自动写到该子表**最末一行之后**，不需要指定行号，也不会破坏既有数据。

```bash
wecom-cli sheet rows append \
  --docid '<docid>' \
  --sheet-id '<sheet_id>' \
  --row '{"values":[{"cell_value":{"text":"张三"},"data_type":"TEXT","cell_format":{}},{"cell_value":{"text":"研发"},"data_type":"TEXT","cell_format":{}},{"cell_value":{"number":40},"data_type":"NUMBER","cell_format":{}}]}'
```

`--row` 结构：`{"values":[<单元格>, <单元格>, ...]}`，按**列顺序**排列。
单元格结构见下方「单元格怎么写」。返回写入的 `row`。

**只能一次追加一行**。要写 N 行就调 N 次，或者改用 `contents update` 一次写一个区域
（但那是 write-high，要走确认）。

## 场景五：更新指定区域的单元格

### 用户会怎么说

"把 B3 改成 50" / "更新这张表的第二行" / "把表头换成新的" / "覆盖 A1:C10 这块"

> ⚠️ **高风险操作（不可逆覆盖）**：本方法会**用新数据覆盖目标区域里的既有单元格**，
> 被覆盖的原值没有备份，CLI 也**没有回滚接口**。
> 执行前必须向用户复述
> 「将把《\<表格名\>》的\<子表名\>子表 \<区域\> 区域覆盖为新数据（\<N\> 行 × \<M\> 列），原有内容不可恢复」
> 并取得明确同意；用户未明确同意时不得执行。

**执行前的三条硬要求**：

1. **先读再写**。写之前**必须**先用 `sheet ranges get` 读一遍目标区域，
   在复述里说清"这块区域现在是什么"。目标区域**本来就是空白**时，如实说明"该区域当前为空"，
   此时实际影响等同于普通写入，但复述这一步不能省。
2. **复述必须带上表格名、子表名、区域范围与规模**，用可读名称，不出现 `docid` / `sheet_id`。
3. 用户回复含糊（"嗯""你看着办"）**不算**明确同意，需要再确认一次。

### 命令

`--grid-data` 的 `start_row` / `start_column` **从 0 起**，且是**目标区域的左上角**。
写多少格由 `rows` 的形状决定（没有独立的"结束坐标"参数）。

```bash
wecom-cli sheet contents update \
  --docid '<docid>' \
  --sheet-id '<sheet_id>' \
  --grid-data '{"start_row":2,"start_column":1,"rows":[{"values":[{"cell_value":{"number":50},"data_type":"NUMBER","cell_format":{}}]}]}'
```

上例写的是 `start_row=2, start_column=1` 这一格，也就是 **A1 表示法里的 B3**
（行列都从 0 开始计数，B 是第 1 列、3 是第 2 行）。**这个 0-based / 1-based 的换算是本方法最常见的错**——
写之前用 `sheet ranges get` 读一格回来核对坐标，比事后补救便宜得多。

**格式与已有内容对齐**：向已有内容的表格写数据时，新内容的样式应尽量与现有表格一致，
避免出现字体、字号、对齐、边框、底色突兀的行。不确定就传 `"cell_format":{}`（默认样式）。

## 场景六：添加子工作表

### 用户会怎么说

"再加一页" / "新建个子表叫 9 月" / "加个 sheet"

```bash
wecom-cli sheet subsheets add \
  --docid '<docid>' \
  --sheet '{"title":"9月明细","row_count":200,"column_count":10}' \
  --index 0
```

| 参数 | 必填 | 说明 |
|---|:--:|---|
| `--docid` | 是 | 目标表格 |
| `--sheet` | 是 | 子表信息：`title` 必给；`row_count` / `column_count` 可选 |
| `--index` | 否 | 插入位置：**`0` = 插到最后**，`1` = 插到第一个位置；不传默认插到最后（上限 254） |

> **`index=0` 是"最后"不是"最前"**，这与所有编程直觉相反。要插到最前面传 `1`。

返回新增子表信息，含 `sheet_id`（内部流转）/ `title` / `row_count` / `column_count` /
`data_range`（新建时为空）。向用户汇报时说子表名，不说 `sheet_id`。

## 场景七：删除子工作表

### 用户会怎么说

"把 8 月那页删了" / "删掉这个子表" / "去掉多余的 sheet"

> ⚠️ **高风险操作（不可逆删除）**：方法描述明写**"删除后不可恢复"**。
> 整张子表连同其全部数据一并消失，CLI 没有恢复接口，本技能也没有历史版本能力。
> 执行前必须向用户复述
> 「将删除《\<表格名\>》中名为\<子表名\>的子表（当前约 \<N\> 行数据），删除后无法恢复」
> 并取得明确同意；用户未明确同意时不得执行。

**执行前的三条硬要求**：

1. **先 `sheet get` 确认要删的到底是哪一张**：核对 `title`，并把该子表的 `row_count` /
   `data_range` 读出来，让用户知道自己要删掉多少数据。
2. **子表名匹配到多张、或一张都没匹配上时，一律停下来问**，绝不"挑一个最像的"。
3. 用户回复含糊**不算**明确同意，需要再确认一次。

```bash
wecom-cli sheet subsheets delete --docid '<docid>' --sheet-id '<sheet_id>'
```

成功返回空对象。执行后汇报"已删除《表格名》的「子表名」子表"。

## 单元格怎么写（`grid_data` / `row` 共用同一套结构）

三个方法（`sheet create` 的 `--grid-data`、`sheet contents update` 的 `--grid-data`、
`sheet rows append` 的 `--row`）用的是**同一套**单元格结构：

```
grid_data = { start_row, start_column, rows: [ { values: [ <cell>, ... ] }, ... ] }
row       = { values: [ <cell>, ... ] }
cell      = { cell_value: {...}, data_type: "...", cell_format: {...} }
```

### `cell_value` 与 `data_type` 必须配对

**`cell_value` 是 oneof 语义：只能填与 `data_type` 对应的那一个字段。**
schema 原文明确写了：多填时下游会**取最后赋值的那个**（静默覆盖，不报错）。

| 形态 | `data_type` | `cell_value` 结构 | 适用 |
|---|---|---|---|
| 文本 | `TEXT` | `{"text":"<纯文本>"}` | 姓名、说明、标签、编号字符串 |
| 数字 | `NUMBER` | `{"number":123.45}` | 金额、数量、比率等要参与计算的值；**JSON 数字，不加引号** |
| 公式 | `FORMULA` | `{"formula":"=SUM(A1:A10)"}` | 任何以 `=` 开头的公式 |
| 超链接 | `LINK` | `{"link":{"url":"<URL>","text":"<显示文本>"}}` | 链接 |

> schema 的 `data_type` 描述里还列了 `SELECT` / `CHECKBOX` / `EMAIL` / `PHONE` / `TIME` /
> `IMAGE` / `LOCATION` / `STAR` / `ATTACHMENT_VIDEO`，对应 `cell_value` 的
> `select` / `time` / `location` 等字段。**上游技能只用了上表这 4 种，其余没有可照抄的书写范例**——
> 需要时先 `wecom-cli sheet contents update --schema` 查清结构，不要现场发明。

`cell_format` 传空对象 `{}` 表示默认样式。要调格式时它支持
`text_format` / `horizontal_alignment` / `vertical_alignment` / `borders` / `padding`，
具体字段用 `--schema` 现查。

**数字一定要用 `NUMBER` 不要用 `TEXT`**：写成文本的数字在表格里不能求和、不能排序，
用户后面做统计时才会发现，届时已经写了一整张表。

## 参数速查

| 方法 | 必填参数 | 高频可选参数 |
|---|---|---|
| `sheet create` | `--doc-name` | `--doc-type`（**显式传 `sheet`**） `--grid-data` |
| `sheet import` | schema 无 required；**实际必须**给 `--file-path`（或 `--file-content`）与 `--file-name` | `--doc-type`（**显式传 `sheet`**） `--passwd` `--append-doc-id` |
| `sheet get` | `--docid` | 无 |
| `sheet ranges get` | `--docid` `--sheet-id` | `--range`（`mode=default` 时**必传**） `--mode`（`default`/`csv`） |
| `sheet rows append` | `--docid` `--sheet-id` `--row` | 无 |
| `sheet contents update` | `--docid` `--sheet-id` `--grid-data` | 无 |
| `sheet subsheets add` | `--docid` `--sheet` | `--index`（0~254） |
| `sheet subsheets delete` | `--docid` `--sheet-id` | 无 |

完整参数请用 `wecom-cli sheet <resource> <method> --help` 现查，不要凭记忆补参数。

## 易错点

- **`sheet_id` 只能来自 `sheet get`**。子表名、`Sheet1`、序号都不是 `sheet_id`，猜的一定失败。
- **`sheet create` 与 `sheet import` 的 `--doc-type` schema 默认值都是 `doc`，不是 `sheet`**
  （schema 原文："文档类型，不传则默认为 doc" / "表格类型，不传则默认为 doc"）。
  两者都与 `doc create` / `doc import` 共用同一个后端方法，**务必显式写 `--doc-type sheet`**。
  上游 `wecomcli-sheet` 两处都没提这个参数——CLI 是否按命令路径自动注入未经实测，显式传是零成本保险。
- **`sheet import` 的 schema 没有任何 required 字段**：漏传 `file_path` / `file_name`
  在本地校验阶段**不报错**，会一路发到服务端才失败。
- **`start_row` / `start_column` 从 0 起，A1 表示法从 1 起**。`start_row=2, start_column=1` = `B3`。
  换算错会把数据写到相邻的行列上，且不会报错。
- **`subsheets add` 的 `index=0` 表示"插到最后"**，不是最前。要最前传 `1`。
- **`ranges get` 在 `mode=default` 时 `--range` 必传**（schema 上是可选，但方法语义要求）。
  不知道范围就先看 `sheet get` 的 `data_range`。
- **`data_range` 为空字符串 = 该子表没有内容**，别再去读它然后困惑于空结果。
- **`cell_value` 是 oneof**：同时填 `text` 和 `number` 不会报错，会静默只保留最后一个。
- **数字写成 `TEXT` 会毁掉后续的统计能力**，要参与计算的一律 `NUMBER` + JSON 数字。
- **`rows append` 一次只能追加一行**，批量请循环调用或改用 `contents update`（后者是 write-high）。
- **`contents update` 与 `subsheets delete` 都不可逆**，两者都必须先读再写/删、必须取得明确同意。
- **本技能没有"撤销""历史版本""恢复已删除子表"的能力**，别向用户承诺可以恢复。
- **`docid` / `sheet_id` / 落盘的本地 `file_path` 一律不展示**；文档用 `[name](url)`，子表用 `title`。
- **智能表格（`s3_` 前缀 / `smartsheet` 链接）用本技能的命令一定失败**，先判类型再动手。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-sheet`。
