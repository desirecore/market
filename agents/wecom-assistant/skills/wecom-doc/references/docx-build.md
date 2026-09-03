# 生成 `.docx`：`scripts/build_docx.py` 使用规范

新建企微 doc 文档的第一步。**模型只需写一份 JSONL 描述文件，不需要写 Python 脚本**——
分发器 `build_docx.py` 会把每条命令派发到对应函数，生成带完整排版的 `.docx`。

## 整体工作流

| 步骤 | 做什么 | 产物 |
|---|---|---|
| 1 | 用文件写入工具输出一个 `*.jsonl` | `<工作目录>/项目周报.jsonl` |
| 2 | `python3 scripts/build_docx.py <*.jsonl>` | `<可写根>/docx/项目周报.docx` |
| 3 | `wecom-cli doc import --doc-type doc --file-name '项目周报.docx' --file-path '<Step 2 路径>'` | 企微在线文档 |

## ⚠️ 运行前置：两个环境变量 + 一个 Python 依赖

`build_docx.py` 自带沙箱式的路径白名单，**两个环境变量都必须显式设置，否则脚本直接失败**：

| 环境变量 | 作用 | 格式 |
|---|---|---|
| `WECOMAGENT_READABLE_DIRS` | 允许**读取** JSONL 的目录白名单 | JSON 数组：`[{"path":"/abs/dir","label":"任意标签"}]` |
| `WECOMAGENT_WRITABLE_DIRS` | 允许**写出** `.docx` 的目录白名单 | 同上 |

- 两个变量都**不设置就用不了**（`_parse_roots` 会抛 `环境变量 ... 未设置或为空`）。
  上游是在企微自己的 Agent 宿主里跑的，那边由宿主注入；**在 DesireCore 里没有人注入，必须自己带上**。
- **输出路径不是你指定的**：脚本取 `WECOMAGENT_WRITABLE_DIRS` 的**第一个** root，
  在其下拼出 `<root>/docx/<jsonl 文件名主干>.docx`。目录不存在会自动创建。
  同名文件已存在时追加 `_<毫秒时间戳>_<pid>` 后缀，**不会覆盖**已有文件。
- 路径里**不允许出现 `.` 或 `..` 片段**，必须给完全展开的绝对路径。
- Python 依赖：**`python-docx`**（`import docx`）。缺了会在 import 阶段就崩。
- 读入 / 写出都有 **30 MiB** 硬上限。

完整调用形态：

```bash
WORKDIR='<工作目录绝对路径>'
WECOMAGENT_READABLE_DIRS="[{\"path\":\"$WORKDIR\",\"label\":\"work\"}]" \
WECOMAGENT_WRITABLE_DIRS="[{\"path\":\"$WORKDIR\",\"label\":\"work\"}]" \
python3 scripts/build_docx.py "$WORKDIR/项目周报.jsonl"
```

成功时 stdout 打印一行：`Successfully built <绝对路径>`。**把这个路径抓出来喂给 `doc import`。**

### 排错表（脚本的错误信息很笼统，靠这张表反查）

| 现象 | 真实原因 |
|---|---|
| `Error: failed to pick output path`（退出码 2） | `WECOMAGENT_WRITABLE_DIRS` 没设 / 不是合法 JSON 数组 / 元素缺 `path` |
| `Error: 路径不在允许范围内`（退出码 2） | JSONL 路径不在 `WECOMAGENT_READABLE_DIRS` 的任一 root 之内，或路径里含 `./` `../` |
| `Error: 类型错误，无法执行: ...`（退出码 2） | JSONL 的 `action` 名写错、`params` 字段名/类型不对、或取值越界 |
| `ModuleNotFoundError: No module named 'docx'` | 缺 `python-docx` 依赖 |
| `Error: 执行失败，请检查输入文件格式或稍后重试`（退出码 2） | JSONL 不是每行一个合法 JSON（常见：有空行、或 JSON 跨了多行） |

排错失败时**如实告诉用户生成 `.docx` 失败**，不要伪造一个 `.docx` 路径去 import。
纯文本内容也可以退回到"写 `.txt` 直接 import"的轻量路径。

## JSONL 书写规范

### 格式硬要求

- 文件后缀 `.jsonl`。
- 每行一个 JSON 对象，结构固定：`{"action": "<函数名>", "params": {<入参对象>}}`。
- **每个 JSON 对象必须压缩到单行**（表格这种嵌套结构也一样）。
- **整个文件不得出现空行**，行与行直接相连。
- 文件名主干只能是 `[A-Za-z0-9_.-]{1,128}`；不满足时脚本会把输出名回退成 `document.docx`
  （**中文文件名会触发这个回退**，想让产物名可控就用 ASCII 命名 JSONL）。

### 4 个 action

| action | 用途 |
|---|---|
| `add_heading` | **所有标题**：封面主标题（`level: 0`）+ 章节标题（`level: 1~4`） |
| `add_paragraph` | 段落：纯文本 / 列表样式 / Subtitle / 多 run 混排格式 |
| `add_table` | 固定布局表格 |
| `add_page_break` | 分页（无参数，传 `{}`） |

> **硬性规则**：任何"标题"性质的文本一律用 `add_heading`，
> **禁止**写成 `add_paragraph` + `style: "Title"`。
> 只有确实需要"副标题段落"时才用 `add_paragraph` + `style: "Subtitle"`。

### `add_heading` — 标题

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `text` | string | `""` | 标题文本 |
| `level` | int | `1` | `0` = 封面主标题（Word 的 Title 样式），`1~4` = 一~四级章节标题 |

```jsonl
{"action": "add_heading", "params": {"text": "项目周报", "level": 0}}
{"action": "add_heading", "params": {"text": "第一章 引言", "level": 1}}
{"action": "add_heading", "params": {"text": "1.1 背景", "level": 2}}
```

### `add_paragraph` — 段落

| 参数 | 类型 | 说明 |
|---|---|---|
| `text` | string | 单 run 纯文本（与 `runs` 二选一；同时传以 `runs` 为准） |
| `runs` | array | 多 run 混排，元素字段见下 |
| `style` | string | 内置样式名：`List Bullet` / `List Number` / `Subtitle`（及其 2/3 级变体） |
| `alignment` | string | 段落级对齐：`left` / `center` / `right` / `justify` |

`runs` 元素字段（**仅字符级格式**，没有段落级字段）：
`text` / `bold` / `italic` / `underline` / `color_hex`（6 位 hex，不带 `#`）/
`size_pt` / `font`（西文字体）/ `east_asia_font`（中文字体）。

列表**必须用内置样式**，绝不手写 `•` 或 `1.`：

| 级别 | Bullet 样式 | Number 样式 |
|---|---|---|
| 0 | `List Bullet` | `List Number` |
| 1 | `List Bullet 2` | `List Number 2` |
| 2 | `List Bullet 3` | `List Number 3` |

> 内置最深 3 级。需要更深嵌套时应**重组内容结构**，而不是手写 `List Bullet 4`
> ——该样式不存在，运行会报错。

```jsonl
{"action": "add_paragraph", "params": {"text": "这是一段正文。"}}
{"action": "add_paragraph", "params": {"text": "2026 年第 22 周", "style": "Subtitle"}}
{"action": "add_paragraph", "params": {"text": "一级要点", "style": "List Bullet"}}
{"action": "add_paragraph", "params": {"text": "二级要点", "style": "List Bullet 2"}}
{"action": "add_paragraph", "params": {"runs": [{"text": "重要："}, {"text": "请按时提交", "bold": true, "color_hex": "C00000"}, {"text": "，谢谢配合。"}]}}
```

### `add_table` — 固定布局表格

| 参数 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `data` | array<array> | 是 | 二维数组，每个元素是一个 cell |

Cell 只有两种合法形态（**不支持 `runs` 多 run 混排**）：

| 形态 | 示例 | 说明 |
|---|---|---|
| 字符串 | `"张三"` | 纯文本 cell |
| 单 run 对象 | `{"text": "字段", "bold": true, "color_hex": "FF0000"}` | 整个 cell 共享一组字符格式 |

Cell 对象支持的字段与 `add_paragraph.runs` 元素完全一致。

> **单元格内无法做"段内局部高亮"**（一句话里只标红其中几个字）。
> 有这类需求时把高亮文本拆出表格，作为表格上方/下方的独立 `add_paragraph + runs` 段落。

```jsonl
{"action": "add_table", "params": {"data": [[{"text": "任务", "bold": true}, {"text": "负责人", "bold": true}, {"text": "DDL", "bold": true}], ["完成联调", "张三", "周三"], ["性能压测", "李四", "周四"]]}}
```

### `add_page_break` — 分页

```jsonl
{"action": "add_page_break", "params": {}}
```

## 完整示例

这是一份 `.jsonl` 文件的**真实形态**——每行一条 action，表格压缩为单行，行间无空行：

```jsonl
{"action": "add_heading", "params": {"text": "项目周报", "level": 0}}
{"action": "add_paragraph", "params": {"text": "2026 年第 22 周", "style": "Subtitle"}}
{"action": "add_heading", "params": {"text": "一、本周进展", "level": 1}}
{"action": "add_paragraph", "params": {"text": "完成核心模块开发，进入联调阶段。"}}
{"action": "add_paragraph", "params": {"text": "完成 API 设计评审", "style": "List Bullet"}}
{"action": "add_paragraph", "params": {"text": "完成 60% 核心代码", "style": "List Bullet"}}
{"action": "add_heading", "params": {"text": "二、风险提示", "level": 1}}
{"action": "add_paragraph", "params": {"runs": [{"text": "需重点关注："}, {"text": "依赖方接口延期", "bold": true, "color_hex": "C00000"}, {"text": "，预计影响排期 2 天。"}]}}
{"action": "add_heading", "params": {"text": "三、下周计划", "level": 1}}
{"action": "add_table", "params": {"data": [[{"text": "任务", "bold": true}, {"text": "负责人", "bold": true}, {"text": "DDL", "bold": true}], ["完成联调", "张三", "周三"], ["性能压测", "李四", "周四"], ["发版评审", "王五", "周五"]]}}
```

---

本文件改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 的
`skills/wecomcli-doc/references/doc-create.md`（MIT License，© WecomTeam），
补充了 DesireCore 环境下的环境变量前置、输出路径规则与排错表。
