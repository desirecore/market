# 配置算力

通过受治理工具配置 DesireCore 算力。禁止从 Bash、HttpRequest 或脚本调用本机
`/api/compute/*` 管理端点；这些端点有意要求可信渲染器 Origin 和实例令牌。

## 安全契约

- 对 Agent 而言 API Key 只写不读。不得读取 `secrets.json`、请求
  `ComputeCredential(action='get', raw=true)`，也不得在工具结果或聊天中复述密钥。
- 使用 `ComputeCredential(action='set')` 为已有的用户自管 Provider 创建或替换密钥。若该
  Provider 尚无凭据引用，工具会创建并挂载专属引用，但不会把明文返回给 Agent。此路径
  受审批、留审计；敏感值在审批卡、工具事件、回执和会话历史中统一脱敏，系统托管凭据
  不可由该操作覆盖。
- 只有当用户已经在当前请求中主动提供了替换密钥时，才把该值传给
  `ComputeCredential(action='set')`；若要求
  Agent 从未接触明文，则用 GUI 聚焦密码输入框，让用户直接输入后再继续保存。不得让用户
  把密钥发到普通聊天，也不得把掩码字段读回模型。
- `credentialMode=none` 表示 Provider 无需密钥。旧配置未声明时，Ollama 也按 `none` 处理。
- 用户询问当前 Key 时，说明 Agent 只能替换、不能读回；人类 UI 的明文查看流程保持独立。

## 已有 Provider 的工作流程

先通过当前工具目录确认 `ManageCompute` 可用。若工具不存在（例如安装版客户端较旧），
整项任务改走下方受治理 GUI 流程；不得回退到本地 HTTP。

1. 调用 `ManageCompute(action='list')`，记录准确的 Provider ID、启用状态、凭据模式、状态和模型数。
2. 若凭据模式为 `required` 且用户已在当前请求中提供新密钥，调用
   `ComputeCredential(action='set', providerId=..., value=...)`；不得回显。若用户要求 Agent 不接触明文，改走
   下方 GUI 人工直填密码框。凭据模式为 `none` 时跳过。
3. 调用 `ManageCompute(action='set_enabled', providerId=..., enabled=true)`。
4. 调用 `ManageCompute(action='sync_models', providerId=...)`。Ollama 会发现本机已安装模型；
   支持的云 Provider 会合并内置模型清单。
5. 调用 `InspectModels` 确认目标模型可选。若用户要求真实测试，发起一次简短固定模型对话，
   并核对运行回执中的 Provider/模型就是目标项。

ManageCompute 和 ComputeCredential 的变更操作会走平台审批策略。除非信息缺失或用户要求
破坏性替换，不要在文字里再加一层重复确认。

## ManageCompute 尚未覆盖的字段

新建自定义 Provider、修改 Base URL/API 格式、删除 Provider、交互式验证密钥目前仍走 GUI。
使用 `ControlDesireCoreGui`，不要使用通用浏览器/CUA 工具：

1. `list_instances`，再对目标 DesireCore 实例执行
   `begin(instance=<id>, mode=control, reason=...)`。默认 `observe` 只能读取界面，不能修改算力。
2. 用受治理 CDP 方法进入“资源 → 算力”完成修改。
3. 执行 `end`。若当前版本有 `ManageCompute`，再调用 `ManageCompute(action='list')`；旧客户端则在 GUI
   内复核保存状态。`InspectModels` 可用时再用它确认模型可选。

若当前版本包含 `ControlDesireCoreGui`，但工具报告 GUI 控制已关闭，实例所有者需设置
`config/security.json#desktopGuiControl.enabled=true` 并重启该实例。若工具目录里完全没有该工具，
说明客户端版本过旧，必须升级；修改开关不能补出旧版本不存在的工具。不得绕过渲染器 HTTP 边界。

## 完成交付

报告 Provider ID、启用状态、同步后的模型数量和真实模型测试结果。不要包含密钥、加密存储内容
或明文指纹。
