---
name: dingtalk-guide
description: >-
  钉钉能力覆盖与边界查询。Use when 用户问某个钉钉产品「怎么用 / 支不支持 / 能不能做 /
  有什么限制 / 为什么不行」，或需要按产品域查功能覆盖、权益门槛、已知边界（如「钉盘同步怎么用」
  「消息搜索为什么返回受限」「视频会议能做到哪一步」「为什么每条命令都要审批」）。也用于 dws
  报错后的分诊。本技能只回答「能力与边界」，不执行钉钉业务操作——具体命令走 dingtalk-* 官方技能，
  安装与自检走 dingtalk-onboarding，跨产品编排走 dingtalk-workflows。
metadata:
  category: reference
  requires:
    tools: [Read]
---

# 钉钉能力说明查询

本技能不含答案正文，只含**索引**。回答前先 Read 下表中匹配的参考文件，按文件内容作答；
不要凭记忆回答产品边界与权益门槛——这些随钉钉侧开通状态变化，写死会误导用户。

## 使用方式

1. 从用户问题里识别产品域，在下表定位文件
2. `Read` 该文件的绝对路径（`${SKILL_DIR}` 会被替换成本技能目录）
3. 按文件内容作答；文件没覆盖的，如实说不确定，并给出 `dws schema` 的自查方式
4. 命中多个产品域时按需读多个文件，不要只读第一个

## 参考文件索引

| 问题涉及 | Read 这个文件 |
| --- | --- |
| 找人、通讯录、语义搜索、多候选 | `${SKILL_DIR}/references/通讯录与找人.md` |
| 发消息、撤回、群管理、机器人、**消息搜索权益** | `${SKILL_DIR}/references/群聊与消息.md` |
| 日程、会议室、闲忙、**视频会议边界** | `${SKILL_DIR}/references/日程与会议.md` |
| 待办、TODO、OA 审批查询与处理 | `${SKILL_DIR}/references/待办与审批.md` |
| 在线文档、电子表格、AI 多维表、导出 | `${SKILL_DIR}/references/文档与表格.md` |
| 钉盘、知识库、文件与节点的分界 | `${SKILL_DIR}/references/钉盘与知识库.md` |
| 邮件收发、搜索、附件 | `${SKILL_DIR}/references/邮件.md` |
| AI 听记、摘要、逐字稿、行动项 | `${SKILL_DIR}/references/AI听记.md` |
| 考勤打卡、排班、日志日报周报 | `${SKILL_DIR}/references/考勤与日志.md` |
| 实时事件、长连接、**为什么禁止轮询** | `${SKILL_DIR}/references/实时事件.md` |
| 跨产品工作流、晨间简报、会议闭环、周报 | `${SKILL_DIR}/references/跨产品工作流.md` |
| 审批闸门、审批模式、命令一直被拦 | `${SKILL_DIR}/references/界面与审批.md` |
| 报错分诊、`dws` 命令失败 | `${SKILL_DIR}/references/故障排查.md` |

## 边界

- 本技能**不执行**任何钉钉命令。用户确认要做某件事时，交回对应的 `dingtalk-*` 官方技能
- 命令目录（有哪些命令、参数是什么）不在这些文件里，也不该写进来——那由 `dws schema`
  与官方技能提供，随二进制升级变化。这里只写**能力覆盖、边界与权益门槛**
- 参考文件里的结论若与 `dws schema` 实际输出冲突，以 schema 为准，并如实告知用户文档可能滞后
