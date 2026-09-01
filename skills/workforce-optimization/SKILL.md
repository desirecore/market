---
name: workforce-optimization
description: >-
  排班、工时上限、人员配置的第一轮澄清（含“只澄清、暂不求解”）也先用 Skill 工具加载本技能，再用 DecisionWorkspace 补问和真人确认卡；普通 AskUserQuestion 不能代替业务事实闭环。Load this Skill for the first clarification of staffing, shifts, work-hour limits, service coverage, resource allocation, targets, task scheduling or LP/MILP, including clarify only / do not solve yet requests. Use DecisionWorkspace question and human-confirmation cards for model-changing facts; generic AskUserQuestion is not a substitute. Clarification needs no connected solver. Actual MindOpt solving requires a separately licensed/deployed solver and configured connector; software, licenses, hosting and fees are not included. MindOpt 软件、许可证、部署及相关费用需使用方另行取得或承担。
compatibility: >-
  Requirement clarification works without a connected solver. Actual MindOpt solving requires separately installed or deployed MindOpt, a valid license under its official terms, and configured solver.mindopt connections; commercial licenses and operating costs are separate when applicable. 需求澄清不要求先连接求解器；实际 MindOpt 求解仍需外部安装部署、有效许可证及 solver.mindopt 连接，适用的商业许可和运行费用另行承担。
version: 2.6.0
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - workforce-optimization
  - operations-research
  - mindopt
  - multi-agent
provides:
  tools:
    - DecisionWorkspace
    - TeamArtifact
    - OptimizationPredict
    - OptimizationCompile
    - OptimizationSolve
    - MindOptSolve
    - OptimizationValidate
metadata:
  author: workforce-optimization-team
  updated_at: '2026-09-01'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 人效与资源优化
      short_desc: 用决策工作区共管人效建模、受保护求解与独立验收；MindOpt 需外部授权部署
      description: >-
        用户提出排班、工时上限、人员配置、服务覆盖、资源分配、绩效目标、任务调度或 LP/MILP，即使“只澄清、暂不求解”，也先用 Skill 工具加载本技能。影响模型的事实使用 DecisionWorkspace 补问及真人确认卡，不能用普通 AskUserQuestion 代替。澄清无需连接求解器；实际 MindOpt 求解需使用方另行取得适用许可证、部署并配置连接，软件、许可证、算力托管及费用均不包含在技能中。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:22565520b50770c1
      translated_by: ai:codex
    en-US:
      name: Workforce and Resource Optimization
      short_desc: Co-manage workforce models, guarded solving, and independent validation; MindOpt is externally licensed
      description: >-
        Load this Skill for the first clarification of staffing, shifts, work-hour limits, service coverage, resource allocation, targets, task scheduling or LP/MILP, including clarify only / do not solve yet requests. Use DecisionWorkspace question and human-confirmation cards for model-changing facts; generic AskUserQuestion is not a substitute. Clarification needs no connected solver. Actual MindOpt solving requires a separately licensed/deployed solver and configured connector; software, licenses, hosting and fees are not included.
      body: ./SKILL.md
      source_hash: sha256:22565520b50770c1
      translated_by: ai:codex
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="bwo-a" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop offset="1" stop-color="#007AFF"/></linearGradient></defs><path d="M5 17.5V11m7 6.5V6m7 11.5V9" stroke="url(#bwo-a)" stroke-width="2" stroke-linecap="round"/><path d="M3.5 20.5h17" stroke="#34C759" stroke-width="1.5" stroke-linecap="round"/><circle cx="5" cy="8" r="2" fill="#34C759"/><circle cx="12" cy="3.5" r="2" fill="#007AFF"/><circle cx="19" cy="6.5" r="2" fill="#AF52DE"/></svg>
  category: business
  maintainer:
    name: 人效与资源优化项目组
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.127
---

# Workforce and Resource Optimization

## L0

Turn natural-language workforce-efficiency requests into reviewable and recoverable artifacts, execute approved LP/MILP only through a user-provided, licensed MindOpt deployment and the governed connector, and independently recompute every result before delivery.

> **External dependency — read before installation:** MindOpt is third-party solver software that must be installed or deployed separately and activated with a valid license under the [official MindOpt license terms](https://opt.aliyun.com/doc/latest/en/html/installation/license.html). Commercial licenses and operating costs must be purchased separately when applicable; community-license eligibility remains subject to those official terms. The client, this Skill, and `MindOptSolve` do not bundle the MindOpt software, a license, hosted compute, procurement, or operating fees.

## L1

- Treat `MindOptSolve` only as a governed connector/adapter to a MindOpt service supplied by the user or operator. Never describe MindOpt itself as an included or built-in Tool.
- The platform retains direct personal `MindOptSolve` and compile-option overrides only as a backward-compatible, non-decision-grade expert path outside this Skill's governed team workflow. Never present an unbound personal call as reviewed, human-confirmed, recoverable, or decision-grade; team runs must use the guarded `OptimizationSolve` path and solver limits recorded in the committed specification.
- Before promising or requesting an actual solve, verify that the external connector is configured and ready, required capabilities are available, and the deployment has a valid applicable license. A registered Tool name alone is not evidence that the solver is installed, licensed, reachable, or paid for.
- If the external dependency is unavailable, state which prerequisite is missing and stop before the solver call. You may still finish requirement clarification and produce reviewable `SceneSpec`, `DataContract`, and `OptimizationSpec` artifacts for later execution, but must not fabricate a `SolveResult`, feasibility, optimality, or benefit claim.
- Before routing or modeling, read the framework matching the user's current conversation language in full: for Chinese use [中文澄清框架](references/requirement-clarification-framework.zh-CN.md), and for English use the [English framework](references/requirement-clarification-framework.md). Follow its real-decision, mandatory-question and conditional-question branches. The Skill's default metadata locale does not override the user's language; use that framework's matching-language fixed footer.
- Skill activation is intentionally scoped to the current service-process lifetime and active parent turn. After an app/service restart or retry fork, the current entry Agent must load this Skill again before checking hidden optimization tools or delegating a stage owner; verify `TeamArtifact` and the stage-required optimization tools in `ToolCatalog` before delegation. A child Agent loading the Skill cannot expand a ceiling inherited from an unactivated parent. Do not persist activation, widen default tools, switch source/scope to evade the ceiling, or ask a child to fabricate artifacts when capability is absent.
- First read the AgentFS user profile, preferences, and relationship memories already injected into the current context. Choose professional, business-guided, or evidence-insufficient adaptive language only from user-confirmed, current, non-conflicting evidence about expertise or communication preference. Employer, job title, one use of jargon, or model inference is not sufficient evidence.
- Professional language may expose the complete structured information contract at once and accept a batch answer. Business-guided language uses plain-language groups in impact order for as many turns as needed. When evidence is insufficient, show a neutral coverage outline and ask the user's preference. Every mode maintains the same complete question map; never omit a model-changing item merely to reduce turns, question count, or cognitive load.
- End every first response with the two-sentence fixed fact-gate footer defined by the requirement-clarification framework. Do not paraphrase, shorten, merge, or omit either sentence.
- Maintain a fact ledger with `fact_state`, `value`, `source`, and `model_impact`. Only confirmed user facts, confirmed data, deterministic rules, or confirmed non-applicability may enter a model.
- Treat relative business-time expressions such as today, tomorrow, the next N days, or this quarter as `pending_confirmation` until the current request confirms the business timezone, business calendar, date-time anchor, and applicable day-boundary, cutoff, holiday, and overnight rules. A system clock or host timezone is environment evidence, not a business rule.
- Isolate every new request from historical contamination. Facts from another conversation, Plan, artifact, memory, or sample remain `pending_confirmation` until the user explicitly carries them into the current request; do not search for or reuse a semantically similar Plan as evidence for the first response.
- Use one entry Agent for routing, consolidated questions, and final delivery. Assign one owner to each stage.
- Clarify-only requests still use this workflow. Generic AskUserQuestion may handle non-modeling setup choices or an explicitly explained capability fallback, but its replies never become DecisionWorkspace answers or human confirmations.
- Before using the nonexpert workflow, inspect the live DecisionWorkspace schemas for semantic_checks_version, request_clarification, interpret_clarification, sourceField and evidenceLinks, and confirm check_semantics is available. If the client lacks these contracts, remain in clarification and explain that a compatible client is required. Never emulate missing gates by editing AgentFS records or using the personal solver path.
- Preflight with a read-only DecisionWorkspace list call. If global TaskBoard/assistance capability is disabled or unavailable, explain the missing user interaction surface and remain in plain-text clarification; do not create questions the user cannot answer, and do not enable capabilities without their request.
- Clarification itself may create a team workspace with semantic_checks_version=1, propose business nodes, inspect an explicitly authorized data source, and record request_clarification before the fact gate passes. These are clarification operations, not permission to build a mathematical model, publish modeling artifacts, delegate solving or call a solver.
- Ask model-changing gaps through request_clarification with an answerable question, reason, canonical type, declared unit and justified constraints. Keep the same logical question while its statement/constraints remain unchanged. Do not invent bounds to reduce choices. Group questions by business impact and explain the remaining coverage in ordinary language.
- The platform already offers unknown and raw_text response channels. Do not add epistemic placeholders such as "not sure yet" or "unknown" to exact choices or node.value. These describe missing knowledge, not a business option. Explain the reason without repeating the UI's "why ask" label.
- When the current user message uniquely supplies a complete business value and every required unit/window, proposals must include a typed `node.value` and remain proposed until the dedicated human confirmation. An Agent-proposed value is not an Agent confirmation. Omitting value incorrectly downgrades a known fact to needs_input; a summary-only node is not a confirmable statement. Omit value only for genuinely unknown or still-ambiguous facts and ask a clarification instead.
- Human value answers are proposed, not confirmed. Use interpret_clarification only if raw_text uniquely determines the business value and every necessary unit/time scope. Preserve the original wording and link the normalized node to that answer; the user must explicitly confirm the new statement. If ambiguity remains, keep the original answer and needs_input, explain the remaining gap, and do not call interpret_clarification or fill a canonical placeholder. For example, "about eight hours, not sure per day or week" determines neither an exact limit nor a time window. Never use ordinary upsert to detach the original answer, manufacture a receipt, or default unknown.
- Let the platform continue the original source conversation after its effective gaps settle. Do not poll by starting new messages, change request identities to evade deduplication, revive canceled sources or retry unknown dispatch outcomes. A pending/interpretation signal is not solve authorization; reread the exact workspace and honor all gates.
- Bind real data with an authorized FileResourceRef, bytesHash, exact fields/types/units and confirmed timeScope. Add finite required/unique/range/enum/foreign_key/cutoff rules as applicable. Range/enum constants and FK fields must use consistent units. Every consumed data field must have modelSemantics.sourceField plus a sourced_from relationship before its business quantity is traced into the model. Unused columns need not be modeled. Unit/window conversions require an explicitly transformed, traceable and reconfirmed source; do not change only its unit label.
- Propose blocking validation nodes with confirmed positive, negative and boundary examples for exact model constraints. Include complete candidate assignments and the intended hard/soft behavior. Cover missing constraints, wrong time aggregation and accidental softening. Platform check_semantics independently evaluates the declared examples; a solver result or a second Agent explanation alone does not establish business correctness.
- Attach file evidence with evidenceLinks whose ref matches the node's evidenceRefs; use only authorized FileResourceRef identities, not guessed paths or arbitrary URLs. Explain report failures using their reason code, exact field/model element, frozen expectation, observed value, impact and next safe action. Direct the user to the graph's issue/source/model controls and change-impact preview; a colored branch, viewed evidence or preview never grants execution approval.
- After the fact-confirmation gate passes, follow this governed sequence without skipping or reordering its control points:
  1. The entry Agent reads the needed `DecisionWorkspace(action="schema")` sections and each `TeamArtifact(action="schema")` contract before constructing writes.
  2. The entry Agent creates the team DecisionWorkspace or submits CAS-protected proposals in business language; proposals never manufacture human receipts.
  3. The user confirms or rejects blocking facts only through the platform's dedicated human controls. A rejection remains an auditable inactive tombstone. All Agents wait for the authoritative result.
  4. Only the top-level entry Agent calls `DecisionWorkspace(action="bind_workspace")` for the validated current workspace revision and model-input hash. Specialists may not bind, replace, or bypass it.
  5. The assigned stage owners publish `SceneSpec`, `DataContract`, optional `PredictionArtifact`, and `OptimizationSpec` in dependency order through `TeamArtifact`, retaining exact artifact revisions and the DecisionWorkspace snapshot. When confirmed predictive inputs require training data, call OptimizationPredict inside this step, publish its real PredictionArtifact and confirm its model-changing outputs before creating OptimizationSpec. Without predictive inputs, omit this branch; do not predict after semantic checks. Initial model publication performs the platform's internal pure compilation checks; do not call guarded OptimizationCompile early to break the model-publication/semantic-check dependency.
  6. The entry Agent calls `DecisionWorkspace(action="link_artifact")` with the exact artifact ID, exact revision, and semantic bindings; never resolve governed evidence through `latest`.
  7. Submit the linked revision for peer review. An independent reviewer checks business-to-model coverage, units, variable families, feasibility logic, provenance, gaps, and stale/rejected exclusions before execution.
     After the user confirms the exact source/rules/examples, call DecisionWorkspace(action="check_semantics") for the current revision/hash and inspect its complete bounded report. Missing data, unsupported evaluators, budget limits or unconfirmed examples are blocked, not passes. Do not rebind the workspace merely because an audit-only revision changed; retain the model-input snapshot until business semantics change.
  8. Invoke `OptimizationCompile` and then `OptimizationSolve`; both must pass the platform's DecisionWorkspace execution guard before side effects. `MindOptSolve` remains a compatible connector name and must never be called directly to bypass the guarded solve path.
  9. A validation owner independent from the solver owner calls `OptimizationValidate` and recomputes domains, hard constraints, objective, baseline delta, and IIS traceability from raw values.
     Only then publish and link the real SolveResult and ValidationReport. Never prepublish guessed results. DeliveryBundle must preserve the exact evidence chain and its human approval status.
  10. The user approves only through the platform's dedicated human approval control after the exact linked chain passes review and independent validation. No Agent or specialist may create that approval.
- In step 5's confirmed prediction branch, use `OptimizationPredict` with ordered holdout, train-only imputation, tuning, metrics, baseline comparison, and explicit fallback rules.
- Compile general models with `OptimizationCompile`, solve once through guarded `OptimizationSolve`, and retain status, variables, objective, request/job IDs, HTTPS transport, selected-engine evidence, and IIS when infeasible.
- Require the validation owner to call `OptimizationValidate` and recompute variable domains, hard constraints, objective, baseline delta, and IIS traceability from raw values.
- Treat every settled successful Tool call as authoritative. After an interruption, synthesize the persisted result without repeating the Tool.

## L2

- Until the fact-confirmation gate passes, use only the clarification operations above: do not publish modeling artifacts, call a solver, delegate a solver-capable Agent, or fill hidden conditions with defaults, simulations, or industry convention. Ledger labels such as confirmed_user are not substitutes for dedicated platform confirmation receipts.
- Interaction mode changes terminology, grouping, per-turn batch size, and example depth only. It never changes fact states, mandatory information, triggered conditions, the modeling-confirmation summary, or the stop gate. The user's explicit choice in the current request overrides historical preference; switching mode preserves confirmed facts and continues with every remaining item.
- If the user cannot confirm an item, deliver the gap, model impact, required owner/data, and optional reduced scope. Never interpret an omitted answer as absent, false, zero, or unlimited.
- Use the fast path only when the user supplied a complete `OptimizationSpec`. It may omit unnecessary scene, prediction, or data-authoring work, but it must still create/propose the governed DecisionWorkspace representation, obtain every required dedicated human confirmation, bind the current revision, publish and link exact revisions, pass peer review and execution guards, delegate one solve and one independent validation, and wait for dedicated human approval before an entry-owned `DeliveryBundle` is decision-grade.
- Use the full path when objectives, constraints, data definitions, or predictive inputs still need modeling. Never advance a stage before its declared dependencies are complete.
- Do not invent unknown business weights, relax hard constraints silently, treat missing values as zero, or describe an unvalidated solution as executable.
- Non-entry Agents place missing information in the team question queue. The queue is only a coordination signal: it cannot carry a human answer or receipt. Only the entry Agent asks the user, and model-changing answers become authoritative only through the dedicated DecisionWorkspace human confirmation controls.
- Specialists must not ask the user directly, bind a workspace, forge confirm/reject/approval receipts, publish outside their owned stage, link a mutable `latest`, bypass compile/solve guards, validate their own solve, or silently retry side effects. They report gaps and evidence to the entry Agent, which owns all user-facing questions and consolidated delivery.
- Connector credentials are resolved internally by SolverConnector from configured secret references. This Skill deliberately declares no `requires.connections`, so solver tokens, CA material, client certificates, and private keys are never injected into Bash. Never request, reveal, persist, or pass them through shell commands, artifacts, endpoints, SSH commands, or tunnels.
- If the solver reports infeasible, preserve and explain its IIS; if validation fails, deliver the failure and violated checks instead of modifying variables or re-solving.
