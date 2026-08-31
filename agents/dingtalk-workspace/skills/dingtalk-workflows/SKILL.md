---
name: dingtalk-workflows
description: 钉钉跨产品编排。Use when 用户要的东西需要串起两个以上钉钉产品——晨间简报（日程+待办+审批+邮件）、会议闭环（听记→待办→文档→日程）、逾期待办巡检并通知、周报生成（日志模版+本周待办+会议）、产物归档（文档→钉盘→知识库）。单产品内的操作不用本技能，直接走对应 dingtalk-* 官方技能的 shortcut。
metadata:
  category: workflow
  requires:
    bins:
      - dws
    tools:
      - Bash
---

# 钉钉跨产品编排

## 什么时候用本技能

**只有跨 ≥2 个钉钉产品时才用。** 单产品内的复合任务（比如 AI 表格批量导入、文档创建后写内容）官方 shortcut 和官方脚本已经覆盖，直接用它们，不要在这里重造。

官方执行契约明确把两件事留给外层：

> 「定时调度由**外层工作流**负责」
> 「无界任务**需要宿主管理进程并持续读取 stdout**」

本技能就站在这个位置。

## 所有 recipe 共用的执行纪律

### 1. 先探可用性，再编排

编排最怕跑到一半发现某个产品没权限，产生半成品。**每个 recipe 开始前先确认它依赖的产品都可用**——用只读命令探一次，失败就提前告诉用户「这个 recipe 缺 X，要么跳过这一步、要么换个做法」。

### 2. Ledger 是强制的

多步编排里**任何一步失败都不能静默跳过**。维护一份步骤台账，最后如实汇报：

```
步骤              状态        说明
今日日程          ok          3 条
我的待办          ok          4 条
待我审批          skipped     响应缺少集合，无法确认是「没有」还是「不可用」
未读邮件          ok          12 封
```

**不要**把 skipped 写成 0，**不要**把不确定写成确定。

### 3. 只读优先，写操作逐条确认

recipe 里的读步骤可以连续跑。**写步骤（建待办、发消息、写文档、排日程）必须先把要写什么完整列给用户，等确认。** 判据用三元组：`effect == destructive || risk == high || confirmation == user_required`。

批量写不超过 30 条。

### 4. ID 只在流程内传递

前一步返回的 ID 直接喂给下一步，**不要**让模型重新"想"一个 ID，也不要用名称当标识符。跨步骤时保持同一个 profile。

---

## Recipe 1 · 晨间简报

**跨产品：** calendar + todo + oa + mail
**性质：** 纯只读，无写操作，可安全自动执行

**步骤**

1. `dws calendar +agenda --format json` —— 今日日程（不传时间默认今天）
2. `dws todo +get-my-tasks --format json` —— 我的待办
3. `dws oa +list-pending --start <今日0点epoch毫秒> --end <现在epoch毫秒> --format json` —— 待我审批
4. `dws mail +recent-mail --format json` —— 收件箱近期会话

**汇总规则**

按「今天必须处理的」优先排序：已过期待办 > 今日会议 > 待审批 > 未读邮件。日程给出时间和标题，待办给出截止时间，审批给出发起人和类型。

**已知失败态**

- `oa +list-pending` 可能返回 `subtype: missing_collection`（响应缺少 `result.values`）。这**不是空结果**——ledger 里记 `skipped`，并说明「审批项无法确认」。可用 `oa +list-forms` 交叉确认该组织是否启用了 OA 审批
- `mail` 返回量可能很大，只取标题/发件人/时间做摘要，不要把正文全灌进上下文

---

## Recipe 2 · 会议闭环

**跨产品：** minutes → todo + doc + calendar
**性质：** 读 + 写，**每个写步骤都要确认**

**步骤**

1. `dws minutes +latest --format json`（或 `+list-mine` 后让用户选）—— 定位目标听记
2. `dws minutes +action-items --format json` —— 取已抽取的行动项
   - ⚠️ **用官方已抽取的行动项，不要自己从逐字稿里"理解"出行动项**。听记产品自己做了这件事，重做会不一致
3. **列给用户确认**：打算建哪几条待办、指派给谁、截止什么时候
4. 确认后 `dws todo +assign`（单人）或 `+assign-multi`（多人）—— 按姓名自动解析 userId
   - 姓名有多个候选时**必须问**，禁止取第一个
5. 可选：`dws doc` 把会议纪要写成文档
6. 可选：`dws calendar +book` 排跟进会议

**回滚语义**

步骤 4 建了一半失败时：**不要自动回滚已建的待办**（用户可能已经看到通知）。改为在 ledger 里列出「已建 N 条 / 失败 M 条」，把失败的原因和参数给用户，让用户决定重试还是手工补。

`calendar +book` 自带回滚（邀请参会人失败时会自动删除日程），这是官方行为，不要重复实现。

---

## Recipe 3 · 逾期待办巡检并通知

**跨产品：** todo + contact/aisearch + ding 或 chat
**性质：** 读 + **对外发通知**，风险最高，确认要求最严

**步骤**

1. `dws todo +get-related-tasks --format json` —— 与我相关的全部待办（创建人/执行人/参与人三种角色并集，已按 taskId 去重）
2. 本地筛出逾期项（对比截止时间与当前时间）
3. 解析负责人：已有 userId 直接用；只有姓名时走 `dws aisearch +search-person --query <姓名>`，**多候选必须问**
4. **完整列出**：要给谁、发什么内容、走什么通道，等用户确认
5. 确认后发送：
   - 常规提醒 → `dws chat` 单聊
   - 强提醒（应用内/短信/电话）→ `dws ding +send-personal`

**红线**

- **对外发消息是不可逆的。** 没有明确确认绝不发送
- 不要群发。逐个发，每个人的内容单独列出
- `ding` 是强打扰（会响铃/发短信/打电话），除非用户明确要求「紧急」，否则默认用 `chat`
- 一次不超过 30 人

---

## Recipe 4 · 周报生成

**跨产品：** report + todo + calendar + minutes
**性质：** 读 + 写（提交日志），提交前必须确认

**步骤**

1. `dws report +template-search --format json` —— 找到可用的日志模板（周报模板名称各组织不同，**不要猜**）
2. `dws todo +get-related-tasks --format json` —— 本周完成的待办
3. `dws calendar +agenda --start <本周一> --end <本周日> --format json` —— 本周会议
4. 可选 `dws minutes +list-mine` —— 本周听记，补充关键结论
5. 按模板字段组织内容，**完整展示给用户确认**
6. 确认后按模板提交

**注意**

- 日志模板的字段是组织自定义的，必须先读模板结构再填，**禁止猜字段名**
- `report` 的时间参数是 ISO-8601，跨度不得超过 180 天（与 `oa` 的 epoch 毫秒不同，别搞混）

---

## Recipe 5 · 产物归档

**跨产品：** doc/minutes → drive → wiki
**性质：** 读 + 写

**步骤**

1. 定位产物：`dws doc +find-doc --keyword <词>` 或 `dws minutes +export-pack`
2. `dws drive +list` / `+create-folder` —— 确认或创建归档目录
3. 移动/复制到归档位置
4. 可选：`dws wiki space list` → `wiki +node-*` 挂到知识库

**边界提醒**

这条最容易走错产品域。判据：
- **文档正文**的编辑与导出 → `doc`
- **文件的存储管理**（移动/复制/权限/回收站）→ `drive`
- **知识库空间与节点组织** → `wiki`

问自己「换个文件类型这个操作还成立吗」——成立就是存储层（drive），不成立就是内容层（doc）。

---

## 定时与事件驱动

recipe 本身只描述**做什么**，**什么时候做**交给 DesireCore：

- 固定时间（如每天早上的晨间简报）→ DesireCore 的调度
- 事件触发（如收到审批就提醒）→ `dws event consume --flatten` 长连接

⚠️ **禁止用轮询模拟事件驱动。** 官方契约明文禁止「写脚本轮询消息历史或审批列表」。长连接需要宿主持续读取 stdout——这是 DesireCore 平台侧的能力，不要在技能里用 `while true` + `sleep` 硬凑。
