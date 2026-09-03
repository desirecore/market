---
name: wecom-media
description: >-
  企业微信媒体文件搬运：把本地文件上传换取 media_id，或把 media_id 下载成本地文件。
  当用户说"把这张图发到群里""下载邮件里的附件看看""这个 PDF 传到微盘"，
  而流程中出现"需要 media_id"或"拿到了 media_id 却看不到内容"时使用；
  它是 wecom-message / wecom-email / wecom-disk 的基础依赖，通常由这些技能在流程中间调用，很少被用户直接点名。
  本技能只搬运文件本身，不解析文件内容（不做 OCR、不读 PDF/Word/Excel 正文、不看图问答）——
  解析交给读到本地路径之后的常规文件读取；发消息走 wecom-message，发邮件走 wecom-email，传微盘走 wecom-disk。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - wecom
  - media
---

# 企业微信媒体文件（上传 / 下载）

企业微信里"文件"在接口层有两种形态：**本地路径**和 **`media_id`**（企微媒体暂存里的一份副本）。
本技能是这两种形态之间唯一的转换器，只做搬运，不看内容。

它几乎不会被用户直接点名，而是被别的技能在流程中间调用：
发图片/文件消息、读邮件附件、把已有素材放进微盘，都要先经过这里换一次形态。

> **前置**：执行任何 `wecom-cli` 命令前，必须先完成 `wecom-shared` 的前置检查
> （CLI 已安装、版本达标、`auth show --status` 为 `authorized`；具体版本门槛以 `wecom-shared` 为准）。

## 能力清单

| 能力 | 命令 | 风险 |
|---|---|---|
| 本地文件 → `media_id` | `wecom-cli media upload` | write-low |
| `media_id` → 本地文件 | `wecom-cli media download` | read |

两个方法都不产生对外可见的副作用：`upload` 只把文件放进企微媒体暂存换一个 ID，
在被别的接口引用之前谁也看不到；`download` 只往本地磁盘写文件。

> 因此本技能虽含一个 write-low 方法，`risk_level` 仍定为 `low`——判据是
> **对他人的实际影响**而非有没有写操作。真正让文件被别人看见的是引用 `media_id`
> 的那一步（发消息 / 发邮件 / 传微盘），确认闸门加在那里，不在这里。

## 上下游衔接：谁在什么时候调它

这是本技能最容易搞错的地方——**不是所有"带文件"的操作都需要先调 `media upload`**。
下表是唯一判据：

| 上游场景 | 要不要先调 `media upload`？ | 说明 |
|---|:--:|---|
| `wecom-message` 发图片 / 文件 / 语音 / 视频消息 | **要** | 消息接口只认 `media_id`，本地路径不接受。这是本技能最主要的用途 |
| `wecom-disk` 上传文件到微盘 | **不用**（有本地文件时） | `disk files upload` 的 `--file-path` 可直接传本地路径，CLI 内部完成上传 |
| `wecom-disk` 上传文件到微盘 | **复用**（上下文已有 `media_id` 时） | 直接把现成 `media_id` 填 `disk files upload --file-content-media`，不要为此再上传一次 |
| `wecom-email` 发带附件 / 内嵌图的邮件 | **不用** | `mail send` 的 `attachments[]` / `inline_images[]` 每项可直接填 `file_path`，CLI 自动上传；已有 `media_id` 时才复用 `media_id` |
| `wecom-doc` 导入本地文件成在线文档 | **不用** | `doc import` 的 `file_path` 与 `media_id` 二选一，**优先 file_path**，CLI 内部完成上传 |
| `wecom-smartsheet` 往记录里传附件 / 图片 | **不用** | `smartsheet files upload` / `images upload` 同样是 `file_path` 与 `media_id` 二选一，优先 `file_path` |
| `wecom-smartpage` 往页面里传文件 / 图片 | **不用** | `smartpage files upload` / `images upload` 同上，优先 `file_path` |
| `wecom-email` 读邮件附件 / 内嵌图的内容 | **要**（下载方向） | `mail get` 返回的 `attachments[].media_id` / `inline_images[].media_id` 必须经 `media download` 落到本地，才能读内容 |
| `wecom-disk` 下载微盘文件 | **不用** | `disk files download` 自己就返回本地 `file_path`，不经过 `media_id` |

一句话记法：**下行（要看内容）几乎总要经过本技能；上行（要发出去）只有发消息一定要经过，邮件和微盘都能直接吃本地路径。**

拿到 `media_id` 之后交给谁：

```
media upload  →  media_id  →  wecom-message  的媒体消息参数
                          →  wecom-disk      的 disk files upload --file-content-media
                          →  wecom-email     的 attachments[].media_id / inline_images[].media_id（仅复用场景）
```

## 场景：把本地文件变成 media_id（上传）

用户说「把这张截图发到群里」「这个 PDF 发给张三」，而目标接口只认 `media_id` 时走这条。

```bash
wecom-cli media upload --file-path '/abs/path/screenshot.png' --type image
```

等价的 JSON 写法：

```bash
wecom-cli media upload --json '{"file_path": "/abs/path/screenshot.png", "type": "image"}'
```

返回 `media_id`、`type`（`image` / `voice` / `video` / `file`）与 `created_at`。

- `--file-path` 必须是**真实存在的本地绝对路径**，只能来自用户明确给出或前置技能返回，禁止编造。
- `--type` 取值只有 `image` / `voice` / `video` / `file` 四个，写枚举外的值会失败。
- **拿到的 `type` 要和下游对齐**：把 `media_id` 交给 `wecom-message` 发媒体消息时，
  消息的 `msg_type` 必须与这里的 `type` 一致（图片配 `image`、文件配 `file`，不能拿图片当文件发）。

## 场景：把 media_id 变成本地文件（下载）

用户说「邮件里那个附件写了什么」「把那张内嵌图看一下」时，
上游技能（多为 `wecom-email`）会给出 `media_id`，用这条落地：

```bash
wecom-cli media download --media-id '<上游接口返回的 media_id>'
```

返回 `file_path`（绝对路径）、`size`、`content_type`。

拿到 `file_path` 后**直接读这个本地文件**来回答用户的问题——
解析内容不是本技能的职责，本技能到「文件已经在本地了」为止。

## 参数速查

| 方法 | 必填 | 常用可选 |
|---|---|---|
| `media upload` | 无 schema 强制必填，但**没有 `--file-path` 就无从上传** | `--type`（`image`/`voice`/`video`/`file`） |
| `media download` | `--media-id` | — |

`--file-path` 的兼容别名是 `--content-path`（同一字段，CLI 为兼容模型的命名习惯而设），
写新命令时统一用 `--file-path`。

## 易错点

- **`media download` 只接受真正的 `media_id`，不接受任何 URL**。把 `attach_url`、正文里的图片链接、
  微盘分享链接当 `media_id` 传进去会直接报错。
- **防泄漏（DLP）加密链接无法下载**：命中 `work.weixin.qq.com/filepreview/security/` 特征的链接，
  是与用户身份绑定的加密资源，本接口下载不了也解不开。正确做法是把链接原样展示给用户，
  引导其在企业微信客户端内打开，**不要**尝试用其他手段绕过。
- **不要为邮件附件多此一举先上传**：`mail send` 的 `attachments[]` / `inline_images[]` 可直接填 `file_path`，
  多跑一趟 `media upload` 既慢又容易把 `type` 配错。
- **不要为了走 `file_path` 而先下载**：已经有 `media_id` 时直接复用，别下载成本地文件再传路径。
- **`media_id` 和本地 `file_path` 都不给用户看**：两者都是内部标识/中间产物。
  用户问「文件在哪」时用自然语言指代（「你刚发的那个附件」），需要给可点击的东西时用可读链接。
- **不解析内容**：OCR、看图问答、PDF/Word/Excel 正文提取、音视频转写都不在本技能范围内；
  本技能只负责把文件放到本地，之后按常规方式读取。
- **不负责"找" `media_id`**：邮件附件的 `media_id` 由 `wecom-email` 产出，微盘文件的由 `wecom-disk` 产出。
  本技能只接收别人给的 `media_id`，不搜索也不猜。
- **禁止绕过 CLI**：不得用 `curl` / `python` 等手段直接请求企微接口完成上传下载。

---

## 来源

本技能改写自 [wecom-cli](https://github.com/WecomTeam/wecom-cli) 官方 Skill
（MIT License，© WecomTeam），针对 DesireCore 的风险治理与交互约定做了适配。
上游对应技能：`wecomcli-media`。
