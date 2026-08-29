---
name: workforce-optimization
description: >-
  Use this Skill when a user naturally asks about workforce efficiency, staffing, shifts, service coverage, hierarchical resource allocation, performance targets, centralized task scheduling, operations research, or general LP/MILP. Govern the request through DecisionWorkspace, versioned multi-agent artifacts, guarded compile/solve, independent validation, and human approval. MindOptSolve is only a compatible connector Tool: the MindOpt solver software, applicable license, separate deployment, and related fees are external and not bundled. 用户自然提到人效、人员配置、排班、服务范围、资源划分、绩效目标、任务调度、运筹优化或 LP/MILP 时使用；通过 DecisionWorkspace、人机确认、版本化制品、受保护求解、独立验收和真人批准完成治理；MindOpt 软件、适用许可证、独立部署及费用不随本技能或客户端提供。
compatibility: >-
  Requires a separately installed or deployed MindOpt solver, a valid license obtained under the official terms, and configured solver.mindopt connections; commercial licenses and operating costs are purchased separately when applicable. 需要外部安装或部署 MindOpt、按官方条款取得有效许可证并配置 solver.mindopt 连接；适用的商业许可及运行费用需另行采购承担。
version: 2.3.4
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
  updated_at: '2026-08-29'
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
        当用户自然提出服务范围、分层资源分配、绩效目标、集中任务调度、人员配置、排班或通用 LP/MILP 需求时，通过 DecisionWorkspace 的人机确认、精确版本制品、入口 Agent 绑定、同伴审阅、执行门禁、独立验收和真人批准形成可恢复治理链。选择 MindOpt 引擎时，实际求解仍依赖使用方另行取得适用许可证、部署并接入 MindOpt；客户端和本技能不包含求解器软件、许可证、算力托管或相关费用。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:ce2258330f6df550
      translated_by: human
    en-US:
      name: Workforce and Resource Optimization
      short_desc: Co-manage workforce models, guarded solving, and independent validation; MindOpt is externally licensed
      description: >-
        When users naturally request service coverage, hierarchical resource allocation, performance targets, centralized task scheduling, staffing, shift planning, or general LP/MILP, use DecisionWorkspace human confirmation, exact-version artifacts, entry-Agent binding, peer review, execution guards, independent validation, and human approval to create a recoverable governance chain. When MindOpt is selected, actual solving still requires the user to obtain an applicable license, deploy MindOpt, and configure its connector; the client and this Skill do not include the solver, license, hosted compute, or related fees.
      body: ./SKILL.md
      source_hash: sha256:ce2258330f6df550
      translated_by: human
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
- Before routing or modeling, the natural-language entry Agent must read the [requirement-clarification framework](references/requirement-clarification-framework.md) in full and follow its real-decision, mandatory-question, and conditional-question branches.
- First read the AgentFS user profile, preferences, and relationship memories already injected into the current context. Choose professional, business-guided, or evidence-insufficient adaptive language only from user-confirmed, current, non-conflicting evidence about expertise or communication preference. Employer, job title, one use of jargon, or model inference is not sufficient evidence.
- Professional language may expose the complete structured information contract at once and accept a batch answer. Business-guided language uses plain-language groups in impact order for as many turns as needed. When evidence is insufficient, show a neutral coverage outline and ask the user's preference. Every mode maintains the same complete question map; never omit a model-changing item merely to reduce turns, question count, or cognitive load.
- End every first response with the two-sentence fixed fact-gate footer defined by the requirement-clarification framework. Do not paraphrase, shorten, merge, or omit either sentence.
- Maintain a fact ledger with `fact_state`, `value`, `source`, and `model_impact`. Only confirmed user facts, confirmed data, deterministic rules, or confirmed non-applicability may enter a model.
- Treat relative business-time expressions such as today, tomorrow, the next N days, or this quarter as `pending_confirmation` until the current request confirms the business timezone, business calendar, date-time anchor, and applicable day-boundary, cutoff, holiday, and overnight rules. A system clock or host timezone is environment evidence, not a business rule.
- Isolate every new request from historical contamination. Facts from another conversation, Plan, artifact, memory, or sample remain `pending_confirmation` until the user explicitly carries them into the current request; do not search for or reuse a semantically similar Plan as evidence for the first response.
- Use one entry Agent for routing, consolidated questions, and final delivery. Assign one owner to each stage.
- After the fact-confirmation gate passes, follow this governed sequence without skipping or reordering its control points:
  1. The entry Agent reads the needed `DecisionWorkspace(action="schema")` sections and each `TeamArtifact(action="schema")` contract before constructing writes.
  2. The entry Agent creates the team DecisionWorkspace or submits CAS-protected proposals in business language; proposals never manufacture human receipts.
  3. The user confirms or rejects blocking facts only through the platform's dedicated human controls. A rejection remains an auditable inactive tombstone. All Agents wait for the authoritative result.
  4. Only the top-level entry Agent calls `DecisionWorkspace(action="bind_workspace")` for the validated current workspace revision and model-input hash. Specialists may not bind, replace, or bypass it.
  5. The assigned stage owner publishes `SceneSpec`, `DataContract`, optional `PredictionArtifact`, `OptimizationSpec`, `SolveResult`, `ValidationReport`, and `DeliveryBundle` in dependency order through `TeamArtifact`, retaining the returned exact artifact revision and DecisionWorkspace snapshot.
  6. The entry Agent calls `DecisionWorkspace(action="link_artifact")` with the exact artifact ID, exact revision, and semantic bindings; never resolve governed evidence through `latest`.
  7. Submit the linked revision for peer review. An independent reviewer checks business-to-model coverage, units, variable families, feasibility logic, provenance, gaps, and stale/rejected exclusions before execution.
  8. Invoke `OptimizationCompile` and then `OptimizationSolve`; both must pass the platform's DecisionWorkspace execution guard before side effects. `MindOptSolve` remains a compatible connector name and must never be called directly to bypass the guarded solve path.
  9. A validation owner independent from the solver owner calls `OptimizationValidate` and recomputes domains, hard constraints, objective, baseline delta, and IIS traceability from raw values.
  10. The user approves only through the platform's dedicated human approval control after the exact linked chain passes review and independent validation. No Agent or specialist may create that approval.
- When training data exists, call `OptimizationPredict`; use ordered holdout, train-only imputation, tuning, metrics, baseline comparison, and explicit fallback rules.
- Compile general models with `OptimizationCompile`, solve once through guarded `OptimizationSolve`, and retain status, variables, objective, request/job IDs, HTTPS transport, selected-engine evidence, and IIS when infeasible.
- Require the validation owner to call `OptimizationValidate` and recompute variable domains, hard constraints, objective, baseline delta, and IIS traceability from raw values.
- Treat every settled successful Tool call as authoritative. After an interruption, synthesize the persisted result without repeating the Tool.

## L2

- Until the fact-confirmation gate passes, clarify only: do not publish modeling artifacts, call a solver, delegate a solver-capable Agent, or fill hidden conditions with defaults, simulations, or industry convention.
- Interaction mode changes terminology, grouping, per-turn batch size, and example depth only. It never changes fact states, mandatory information, triggered conditions, the modeling-confirmation summary, or the stop gate. The user's explicit choice in the current request overrides historical preference; switching mode preserves confirmed facts and continues with every remaining item.
- If the user cannot confirm an item, deliver the gap, model impact, required owner/data, and optional reduced scope. Never interpret an omitted answer as absent, false, zero, or unlimited.
- Use the fast path only when the user supplied a complete `OptimizationSpec`. It may omit unnecessary scene, prediction, or data-authoring work, but it must still create/propose the governed DecisionWorkspace representation, obtain every required dedicated human confirmation, bind the current revision, publish and link exact revisions, pass peer review and execution guards, delegate one solve and one independent validation, and wait for dedicated human approval before an entry-owned `DeliveryBundle` is decision-grade.
- Use the full path when objectives, constraints, data definitions, or predictive inputs still need modeling. Never advance a stage before its declared dependencies are complete.
- Do not invent unknown business weights, relax hard constraints silently, treat missing values as zero, or describe an unvalidated solution as executable.
- Non-entry Agents place missing information in the team question queue. The queue is only a coordination signal: it cannot carry a human answer or receipt. Only the entry Agent asks the user, and model-changing answers become authoritative only through the dedicated DecisionWorkspace human confirmation controls.
- Specialists must not ask the user directly, bind a workspace, forge confirm/reject/approval receipts, publish outside their owned stage, link a mutable `latest`, bypass compile/solve guards, validate their own solve, or silently retry side effects. They report gaps and evidence to the entry Agent, which owns all user-facing questions and consolidated delivery.
- Connector credentials are resolved internally by SolverConnector from configured secret references. This Skill deliberately declares no `requires.connections`, so solver tokens, CA material, client certificates, and private keys are never injected into Bash. Never request, reveal, persist, or pass them through shell commands, artifacts, endpoints, SSH commands, or tunnels.
- If the solver reports infeasible, preserve and explain its IIS; if validation fails, deliver the failure and violated checks instead of modifying variables or re-solving.
