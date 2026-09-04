# 审批 · 考勤 · OKR

**对助手说**：「我有什么待审批的」「上个月我的打卡记录」「看看我这季度的 OKR」

**实测命令**：

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user   # 1=待办 2=已办
lark-cli attendance user_tasks query --employee-type employee_no \
  --data '{"user_ids":[],"check_date_from":20260810,"check_date_to":20260901}' --as user
lark-cli okr +cycle-list --user-id ou_xxx --as user
```

**要点**：
- **考勤查询区间上限 30 天**，超了会报 `interval is larger than 30`。
- 考勤的 `--employee-type` 是必填的独立参数，塞进 `--params` 会被覆盖掉。
- **审批待办不是飞书任务**，两者是不同系统；妙记里的 AI 待办又是第三种。助手会按来源正确分流。
- OKR 的「分数」和「进度」是两回事：说「完成度 75%」通常指量化指标或进展记录，不是评分。
- OKR 周期由管理员创建，个人无法自建——没有开放周期时查询会返回空。

---

> 命令与结论均来自真机验证（2026-09-01，220 个已授权 scope）。未实际跑通的能力在[能力边界](./13-能力边界.md)中如实标注。
> 返回：[Agent 说明](../README.md) · [文档索引](./README.md)
