# write-high 方法完整清单（26 个）+ 条件升级（4 个）

> 数据来源：R2 能力矩阵对 wecom-cli 1.2.0 全部 95 个方法的分级（read 38 / write-low 31 / write-high 26）。
> **判据是 schema description 与上游 SKILL.md 的声明，不是实测**——当前尚未做真实业务调用验证。
> 遇到与实际行为不符的情况，以实际行为为准并回来更正本表。

## 判据

| 级别 | 判据 |
|---|---|
| `read` | 纯查询，对企业微信侧无状态变更（`disk.files.download` / `media.download` 会写本地磁盘，但无远端副作用，仍归 read） |
| `write-low` | 创建新对象或**只增不减**地修改内容（追加、上传、新建子表/字段/视图），错了可以再删/再改回 |
| `write-high` | **对外可见**（发消息、发邮件、邀请他人、授权他人）或**不可逆**（覆盖、删除、完成待办），CLI 无回滚接口 |

## 26 个 write-high

| # | 方法 | 归类 | 所属技能 |
|---|---|---|---|
| 1 | `message.send` | 对外发送 | `wecom-message` |
| 2 | `message.aibot.send` | 对外发送 | `wecom-message` |
| 3 | `mail.send` | 对外发送（发出不可撤回） | 邮件技能 |
| 4 | `meeting.create` | 对外邀请 | 会议技能 |
| 5 | `meeting.update` | 对外通知 | 会议技能 |
| 6 | `meeting.cancel` | 对外通知 + 不可逆 | 会议技能 |
| 7 | `calendar.schedules.create` | 对外邀请（带 `attendees` 时） | 日程技能 |
| 8 | `calendar.schedules.update` | 对外通知 | 日程技能 |
| 9 | `calendar.schedules.cancel` | 对外通知 + 不可逆 | 日程技能 |
| 10 | `todo.delete` | 不可逆 + 对参与人可见 | 待办技能 |
| 11 | `todo.finish` | 不可逆（无「取消完成」方法）；`finished_all` 可代全员完成 | 待办技能 |
| 12 | `doc.members.update` | 权限扩散 | 文档管理技能 |
| 13 | `doc.rules.update` | 权限扩散（可放开**企业外**加入权限） | 文档管理技能 |
| 14 | `doc.contents.overwrite` | 不可逆覆盖 | 文档技能 |
| 15 | `sheet.contents.update` | 不可逆覆盖既有单元格 | 表格技能 |
| 16 | `sheet.subsheets.delete` | 不可逆（描述明写「删除后不可恢复」） | 表格技能 |
| 17 | `smartpage.pages.overwrite` | 不可逆覆盖 | 智能文档技能 |
| 18 | `smartpage.pages.update` | 含 `delete_page`，不可逆 | 智能文档技能 |
| 19 | `smartpage.blocks.update` | 含 `replace` / `delete`，不可逆 | 智能文档技能 |
| 20 | `smartsheet.records.update` | `type` 枚举含 `delete`，单次可影响 2000 行 | 智能表格技能 |
| 21 | `smartsheet.records.delete` | 不可逆 | 智能表格技能 |
| 22 | `smartsheet.fields.delete` | 不可逆（连带删除整列数据） | 智能表格技能 |
| 23 | `smartsheet.sheets.delete` | 不可逆（删整张子表） | 智能表格技能 |
| 24 | `smartsheet.sheets.update` | `type` 枚举含 `delete` | 智能表格技能 |
| 25 | `smartsheet.views.delete` | 不可逆 | 智能表格技能 |
| 26 | `smartsheet.charts.delete` | 不可逆 | 智能表格技能 |

## 4 个条件升级（默认 write-low）

| 方法 | 升级判据 | 升级理由 |
|---|---|---|
| `todo.create` | 传了 `follower_ids` | 分派给他人并触发提醒 |
| `todo.update` | 传了 `followers` | **全量替换**语义，漏传即把人踢出待办 |
| `smartsheet.fields.update` | 变更字段类型 | 可能不可逆地转换/丢弃既有单元格值 |
| `disk.files.rename` | 目标位于共享空间 | 对全体协作者可见 |

## 统一确认措辞

> ⚠️ **高风险操作**：\<会造成什么后果\>。执行前必须向用户复述
> 「\<要做的事的自然语言描述\>」并取得明确同意；用户未明确同意时不得执行。

复述必须包含：**对谁**（可读名称，不是 ID）、**做什么**、**内容是什么**。
用户回复含糊（「嗯」「你看着办」）不算明确同意。

## 一个已知的例外（上游规定，与本约定冲突）

上游 `wecomcli-email` 规定：调 `mail send` 前**必须**先在对话里展示邮件预览，
但**展示完直接发，不等确认、也不许再问「是否发送」**。

这与 DesireCore 的 write-high 确认约定直接冲突。本项目的处置：
**以 DesireCore 的确认约定为准**（发邮件不可撤回，属于最典型的 write-high），
即展示预览后仍需取得明确同意。若后续用户明确要求恢复上游行为，再单独调整邮件技能。
