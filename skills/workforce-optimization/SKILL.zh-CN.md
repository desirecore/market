<!-- locale: zh-CN -->

# 人效与资源优化

## L0

把自然语言人效需求转成可审阅、可恢复的版本化制品，只通过使用方自备且已获有效许可的 MindOpt 部署及受治理 Connector 执行已确认的 LP/MILP，并在交付前独立重算验收。

> **外部依赖——安装前必读：** MindOpt 是需要独立安装或部署，并按[官方 MindOpt 许可证条款](https://opt.aliyun.com/doc/mindopt/latest/cn/html/installation/license.html)取得有效许可证的第三方求解器软件。适用商业许可的场景需另行购买，社区许可是否适用以官方条款为准。客户端、本技能和 `MindOptSolve` 均不包含 MindOpt 软件、许可证、算力托管、采购或运行费用。

## L1

- `MindOptSolve` 只能视为连接使用方或运维方所提供 MindOpt 服务的受治理 Connector/Adapter；不得把 MindOpt 求解器本体描述为客户端已包含或内置的 Tool。
- 平台保留个人会话直接调用 `MindOptSolve` 和 compile 临时覆盖参数，只是本技能团队治理流程之外的向后兼容、非 decision-grade 专家路径。不得把未绑定的个人调用描述成已审阅、已由真人确认、可恢复或 decision-grade；团队运行必须使用受保护的 `OptimizationSolve`，并把求解限制写入 committed specification。
- 在承诺或发起真实求解前，必须验证外部 Connector 已配置且 ready、所需 capabilities 可用，并确认该部署具备当前用途所需的有效许可证。仅发现 `MindOptSolve` Tool 名称，不能证明求解器已经安装、授权、可达或完成付费。
- 外部依赖不可用时，必须说明具体缺少的前置条件并在调用求解器前停止。仍可完成需求澄清，并交付供后续执行的 `SceneSpec`、`DataContract` 和 `OptimizationSpec`，但不得伪造 `SolveResult`，也不得宣称可行、最优或收益。
- 自然语言入口在路由或建模前必须按用户当前对话语言完整读取框架：中文使用 `references/requirement-clarification-framework.zh-CN.md`，英文使用 `references/requirement-clarification-framework.md`，据此识别真实决策、必问项和条件触发项。技能 metadata 默认语言不覆盖用户语言；固定事实门尾注也使用相应语言版本。
- Skill 激活状态按当前服务进程生命期和父 Agent 活动轮次隔离。应用/服务重启或重试 fork 后，当前入口 Agent 必须先重新加载本技能，再检查隐藏的优化工具或委派阶段 Owner；委派前用 `ToolCatalog` 核实 `TeamArtifact` 及该阶段所需优化工具。子 Agent 自行加载 Skill 不能扩大从尚未激活父 Agent 继承的工具上限。不得持久化激活状态、扩大默认工具、切换来源/scope 绕过上限，也不得在能力缺失时要求子 Agent 伪造工件。
- 先读取当前上下文已注入的 AgentFS 用户画像、偏好和关系记忆，按其中已由用户确认、仍有效且无冲突的专业熟悉度或沟通偏好选择专业、业务引导或证据不足时的自适应表达；岗位名称、公司归属、单次术语使用和模型猜测不是充分证据。
- 专业表达可以一次公开结构化完整信息契约并接受批量回答；业务引导表达用白话按影响顺序分组、允许任意必要轮次；证据不足时先给中性覆盖范围并询问用户偏好。任何表达都必须维护同一完整问题地图，不得以减少轮次、问题数量或认知负担为由跳过模型影响项。
- 每次首轮回复必须以业务澄清框架规定的两句“固定事实门尾注”逐字收尾，不得同义改写、缩短、合并或遗漏任何一句。
- 维护带 `fact_state`、`value`、`source`、`model_impact` 的事实台账；只有用户事实、数据事实、确定性规则或已确认不适用项能进入模型。
- “今天”“明日”“未来 N 天”“本季度”等业务相对时间，在本轮确认业务时区、业务日历、日期/时刻锚点以及适用的日切、截点、节假日和跨日规则前，一律保持 `pending_confirmation`；系统时钟或宿主机时区只是环境证据，不是业务规则。
- 每个新需求必须隔离历史污染：其他会话、Plan、工件、记忆或样例中的事实一律保持 `pending_confirmation`，只有用户在当前请求中明确沿用后才能转为事实；首轮不得搜索或复用语义相似的旧 Plan 作为证据。
- 用户只与入口 Agent 交互；入口负责路由、集中追问和最终交付，每个阶段只有一个 Owner。
- “只澄清、暂不求解”仍走本流程。普通 AskUserQuestion 只用于非建模设置选择或已明确说明的能力降级，不能把其答复当成 DecisionWorkspace 答案或真人确认。
- 使用非专家流程前，检查实时 DecisionWorkspace Schema 是否提供 semantic_checks_version、request_clarification、interpret_clarification、sourceField 和 evidenceLinks，并确认 check_semantics 可用。缺少契约时停留在澄清并说明需要兼容客户端；不得直接编辑 AgentFS 记录模拟缺失门禁，也不得切到个人求解路径绕过。
- 先只读调用 DecisionWorkspace list 探测；全局 TaskBoard/assistance 能力关闭或不可用时，说明缺少用户处理入口并停留在普通文本澄清，不创建用户无法回答的补问，也不在用户未要求时开启能力。
- 事实门通过前，澄清操作可以创建 semantic_checks_version=1 的团队工作区、提议业务节点、检查用户明确授权的数据源并记录 request_clarification。这些不是数学建模、发布建模工件、委派求解或调用求解器的授权。
- 决定性缺口通过 request_clarification 提供可回答的问题、原因、规范类型、单位和有依据的约束。同陈述/约束保持同一逻辑问题，不编造上下界来减少选项。按业务影响组织问题，并用普通语言说明剩余覆盖范围。
- 平台已提供 unknown 和 raw_text 回答通道；不得把“目前不确定”“不知道”等知识缺口作为精确 choices 或 node.value 的占位值，它们不是业务选项。reason 直接解释原因，不重复界面已有的“为什么问”标签。
- 当前用户消息已唯一给出完整业务值及必要单位/窗口时，提议节点必须写入类型化 `node.value`，状态保持 proposed 等待专用真人确认；“Agent 提议值”不是“Agent 代替确认”。省略 value 会把已知事实错误降为 needs_input，不得用只有 summary 的节点冒充可确认陈述。只有未知或仍有歧义时才省略 value 并进入补问。
- 真人提交 value 仍是提议，不是确认。仅在 raw_text 能唯一确定业务值及必要单位/统计窗口时，才用 interpret_clarification 关联原答案与规范化节点，保留原话并等待真人确认。仍有歧义时保留原答案和 needs_input，解释尚缺什么，不调用 interpret_clarification 或填 canonical 占位值。例如“差不多八小时，不知按天还是按周”既不能确定精确上限，也不能确定周期。不得普通 upsert 切断原答案关联、伪造回执或默认补值。
- 由平台在有效缺口结算后继续原来源会话。不得靠发新消息轮询、换请求身份绕过去重、复活已取消来源或重跑 unknown 派发。pending/解释信号不是求解授权；必须重读精确工作区并遵守全部门禁。
- 真实数据用已授权 FileResourceRef、bytesHash、精确字段/类型/单位和经确认 timeScope 绑定；按需声明 required/unique/range/enum/foreign_key/cutoff 有限规则。range/enum 常量及 FK 两侧单位必须一致。每个实际消费字段都须用 modelSemantics.sourceField 和 sourced_from 关联业务量，再追踪入模；未使用列不必入模。单位/窗口转换须产生显式转换、可追溯且重新确认的来源，不得只改单位标签。
- 为确切模型约束提议 blocking validation 正例、反例和临界例，提供完整候选赋值与预期硬/软行为；至少覆盖缺约束、错误统计窗口和意外软化。平台 check_semantics 独立复算已声明用例；求解器结果或第二份 Agent 解释本身不能证明业务正确。
- 文件证据用 evidenceLinks 显式关联同节点 evidenceRefs，只使用已授权 FileResourceRef，不猜路径或任意 URL。解释失败时给出原因码、精确字段/模型元素、冻结预期、实际观察、影响和安全下一步；引导用户使用图中的问题/来源/模型入口和变更影响预览。分支颜色、查看证据或预览都不是执行授权。
- 事实确认门通过后，必须严格按以下治理顺序执行，不得跳过或调换控制点：
  1. 入口 Agent 在构造写入前，按需读取 `DecisionWorkspace(action="schema")` 的对应 section，以及每类 `TeamArtifact(action="schema")` 契约。
  2. 入口 Agent 创建团队 DecisionWorkspace，或用 CAS 提交业务语言提议；提议绝不得伪造真人回执。
  3. 用户只能通过平台专用真人控件确认或驳回阻断事实；驳回项保留为可审计的非活跃 tombstone。所有 Agent 必须等待权威结果。
  4. 只有顶层入口 Agent 可以对已验证的当前 workspace revision 与 model-input hash 调用 `DecisionWorkspace(action="bind_workspace")`；Specialist 不得绑定、替换或绕过。
  5. 指定阶段 Owner 按依赖顺序通过 `TeamArtifact` 发布 `SceneSpec`、`DataContract`、可选 `PredictionArtifact` 和 `OptimizationSpec`，保留精确 artifact revision 与 DecisionWorkspace snapshot。经确认的预测输入需要训练数据时，在本步骤内调用 OptimizationPredict、发布真实 PredictionArtifact，并确认影响模型的预测输出后再创建 OptimizationSpec；无预测输入则省略该分支，不在语义检查之后才补预测。首次模型发布使用平台内部纯编译校验；不得提前调用受保护 OptimizationCompile 来绕开模型发布与语义检查的依赖。
  6. 入口 Agent 使用精确 artifact ID、精确 revision 和语义绑定调用 `DecisionWorkspace(action="link_artifact")`；受治理证据禁止解析到可变 `latest`。
  7. 将已链接 revision 提交同伴审阅；独立 reviewer 在执行前检查业务到模型覆盖、单位、变量族、可行性逻辑、来源证据、缺口以及 stale/rejected 排除。
     用户确认精确来源/规则/用例后，对当前 revision/hash 调用 DecisionWorkspace(action="check_semantics")，检查完整有界报告。缺数据、未知 evaluator、超预算或未确认用例均是阻断，不是通过。审计-only revision 变化不机械重绑；业务语义不变时保持原 model-input snapshot。
  8. 依次调用 `OptimizationCompile` 和 `OptimizationSolve`；两者产生副作用前都必须通过平台 DecisionWorkspace execution guard。`MindOptSolve` 只保留兼容 Connector 名称，不得被直接调用来绕过受保护求解路径。
  9. 与求解 Owner 不同的验证 Owner 调用 `OptimizationValidate`，基于原始变量独立重算变量域、硬约束、目标值、基线差和 IIS 可追溯性。
     此后才发布并关联真实 SolveResult 和 ValidationReport，不得提前发布猜测结果。DeliveryBundle 必须保留精确证据链及其真人批准状态。
  10. 精确链接链通过审阅和独立验收后，用户只能通过平台专用真人批准控件批准；任何 Agent 或 Specialist 都不得生成该批准。
- 第 5 步已确认的预测分支使用 `OptimizationPredict`，执行有序留出、仅训练集插补、调参、指标、基线比较和明确降级规则。
- 通用模型先用 `OptimizationCompile` 严格编译，再通过受保护的 `OptimizationSolve` 求解一次；保留真实 status、原始变量、objective、request/job ID、HTTPS transport、所选引擎证据和不可行时的 IIS。
- 验证 Owner 必须调用 `OptimizationValidate`，基于原始变量独立重算变量域、硬约束、目标值、基线差和 IIS 可追溯性。
- 已结算且成功的 Tool 调用是权威事实；系统中断后只能综合持久化结果，不得重复执行 Tool。

## L2

- 事实确认门未通过时只允许上述澄清操作：不得发布建模工件、调用求解器、委派 solver-capable Agent，或用默认值、模拟情况、行业惯例补全隐形条件。confirmed_user 等事实台账标签不能代替平台专用真人确认回执。
- 交互模式只改变术语、分组、单轮批量和举例深度；不得改变事实状态、必问信息集合、条件触发项、建模确认摘要或停止门。用户本轮显式选择优先于历史偏好，切换模式时保留已确认事实并继续补齐其余项目。
- 用户无法确认时交付待确认项、模型影响、所需责任方/数据和可选降级范围；不得把未回答解释为不存在、否、零或不限制。
- 只有用户已经提供完整 `OptimizationSpec` 时才走快速路径。快速路径可以省略不必要的场景、预测或数据编写，但仍必须创建/提议受治理的 DecisionWorkspace 表达、取得所有必要的专用真人确认、绑定当前 revision、发布并链接精确 revision、通过同伴审阅和 execution guard、执行一次求解委派和一次独立验证，并等待专用真人批准后，入口发布的 `DeliveryBundle` 才能成为 decision-grade 交付。
- 目标、约束、数据口径或预测输入仍需建模时走完整路径；依赖阶段未完成不得越级。
- 不得替业务编造未知权重、静默放松硬约束、把缺失值当零，或把未经独立验算的方案称为可执行策略。
- 非入口 Agent 把数据缺口写入团队问题队列；该队列只是一种协调信号，不能承载真人答案或回执。只有入口能向用户提问，任何影响模型的答案都只有通过 DecisionWorkspace 专用真人确认控件才成为权威事实。
- Specialist 不得直接向用户追问、绑定工作区、伪造 confirm/reject/approve 回执、跨出自身阶段发布、链接可变 `latest`、绕过 compile/solve guard、自验自己的求解结果或静默重试副作用。它们只向入口 Agent 报告缺口与证据，由入口统一负责用户问题和汇总交付。
- SolverConnector 只在内部从已配置的 secret references 解引用连接凭证。本技能刻意不声明 `requires.connections`，因此 solver token、CA、客户端证书和私钥不会被注入 Bash。不得索取、回显、持久化，或通过 shell 命令、制品、endpoint、SSH 命令或隧道传递这些内容。
- 求解不可行时保留并解释 IIS；独立验收失败时交付失败事实和违规项，不得修改变量或重新求解。
