<!-- locale: zh-CN -->

# 贝壳 Wings 人效优化

## L0

把自然语言人效需求转成可审阅、可恢复的版本化制品，只通过受治理的 MindOpt Connector 执行已确认的 LP/MILP，并在交付前独立重算验收。

## L1

- 用户只与入口 Agent 交互；入口负责路由、集中追问和最终交付，每个阶段只有一个 Owner。
- 完整路径必须按依赖顺序通过 `TeamArtifact` 发布 `SceneSpec`、`DataContract`、`PredictionArtifact`、`OptimizationSpec`、`SolveResult`、`ValidationReport` 和 `DeliveryBundle`。
- 有训练数据时必须调用 `OptimizationPredict`，执行有序留出、仅训练集插补、调参、指标、基线比较和明确降级规则。
- 通用模型先用 `OptimizationCompile` 严格编译，再用 `MindOptSolve` 求解一次；保留真实 status、原始变量、objective、request/job ID、HTTPS transport、solver 证据和不可行时的 IIS。
- 验证 Owner 必须调用 `OptimizationValidate`，基于原始变量独立重算变量域、硬约束、目标值、基线差和 IIS 可追溯性。
- 已结算且成功的 Tool 调用是权威事实；系统中断后只能综合持久化结果，不得重复执行 Tool。

## L2

- 用户已经提供完整 `OptimizationSpec` 时才走快速路径：一次求解委派、一次验证委派，然后由入口发布 `DeliveryBundle`。
- 目标、约束、数据口径或预测输入仍需建模时走完整路径；依赖阶段未完成不得越级。
- 不得替业务编造未知权重、静默放松硬约束、把缺失值当零，或把未经独立验算的方案称为可执行策略。
- 非入口 Agent 把数据缺口写入团队问题队列，只有入口能向用户提问。
- Connector 凭证只从声明的 connection refs 获取；不得索取、回显或把 token、CA、客户端证书、私钥、endpoint、SSH 命令或隧道写入制品。
- 求解不可行时保留并解释 IIS；独立验收失败时交付失败事实和违规项，不得修改变量或重新求解。
