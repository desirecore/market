---
name: beike-workforce-optimization
description: >-
  Structure, predict, compile, solve, independently validate, and recover Beike workforce-efficiency optimization through versioned multi-agent artifacts and a governed MindOpt connector. Use for brokerage territory design, store/building/opportunity allocation, performance targets, centralized customer-service task scheduling, staffing, shifts, or general LP/MILP. 用户提到贝壳、人效、辖区、资源划分、绩效目标、客服调度、排班、运筹优化或 MindOpt 时使用。
version: 2.3.0
type: procedural
risk_level: medium
status: enabled
disable-model-invocation: true
tags:
  - beike
  - workforce-optimization
  - operations-research
  - mindopt
  - multi-agent
provides:
  tools:
    - TeamArtifact
    - OptimizationPredict
    - OptimizationCompile
    - MindOptSolve
    - OptimizationValidate
requires:
  connections:
    - solver.mindopt.endpoint
    - solver.mindopt.server-name
    - solver.mindopt.token
    - solver.mindopt.ca
    - solver.mindopt.client-cert
    - solver.mindopt.client-key
metadata:
  author: beike-workforce-optimization-team
  updated_at: '2026-08-06'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 贝壳人效优化
      short_desc: 用版本化多智能体流水线梳理、预测、求解并独立验收人效优化
      description: >-
        将贝壳经纪人辖区、资源划分、绩效目标、客服调度、排班和通用 LP/MILP 需求转成可恢复的场景、预测、模型、MindOpt 求解与独立验收制品。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:1fceb54ea600e33b
      translated_by: human
    en-US:
      name: Beike Workforce Optimization
      short_desc: Structure, solve, and independently validate workforce optimization with versioned multi-agent artifacts
      description: >-
        Turn Beike territory, resource, performance, customer-service scheduling, staffing, and general LP/MILP requests into recoverable scene, prediction, model, MindOpt solve, and independent validation artifacts.
      body: ./SKILL.md
      source_hash: sha256:1fceb54ea600e33b
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="bwo-a" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop offset="1" stop-color="#007AFF"/></linearGradient></defs><path d="M5 17.5V11m7 6.5V6m7 11.5V9" stroke="url(#bwo-a)" stroke-width="2" stroke-linecap="round"/><path d="M3.5 20.5h17" stroke="#34C759" stroke-width="1.5" stroke-linecap="round"/><circle cx="5" cy="8" r="2" fill="#34C759"/><circle cx="12" cy="3.5" r="2" fill="#007AFF"/><circle cx="19" cy="6.5" r="2" fill="#AF52DE"/></svg>
  category: business
  maintainer:
    name: 贝壳人效优化项目组
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.100
---

# Beike Workforce Optimization

## L0

Turn natural-language workforce-efficiency requests into reviewable and recoverable artifacts, execute approved LP/MILP only through the governed MindOpt connector, and independently recompute every result before delivery.

## L1

- Before routing or modeling, the natural-language entry Agent must read `references/requirement-elicitation-decision-tree.md` in full and follow its real-decision, mandatory-question, and conditional-question branches.
- First read the AgentFS user profile, preferences, and relationship memories already injected into the current context. Choose professional, business-guided, or evidence-insufficient adaptive language only from user-confirmed, current, non-conflicting evidence about expertise or communication preference. Employer, job title, one use of jargon, or model inference is not sufficient evidence.
- Professional language may expose the complete structured information contract at once and accept a batch answer. Business-guided language uses plain-language groups in impact order for as many turns as needed. When evidence is insufficient, show a neutral coverage outline and ask the user's preference. Every mode maintains the same complete question map; never omit a model-changing item merely to reduce turns, question count, or cognitive load.
- End every first response with the two-sentence fixed fact-gate footer defined by the requirement-clarification framework. Do not paraphrase, shorten, merge, or omit either sentence.
- Maintain a fact ledger with `fact_state`, `value`, `source`, and `model_impact`. Only confirmed user facts, confirmed data, deterministic rules, or confirmed non-applicability may enter a model.
- Treat relative business-time expressions such as today, tomorrow, the next N days, or this quarter as `pending_confirmation` until the current request confirms the business timezone, business calendar, date-time anchor, and applicable day-boundary, cutoff, holiday, and overnight rules. A system clock or host timezone is environment evidence, not a business rule.
- Isolate every new request from historical contamination. Facts from another conversation, Plan, artifact, memory, or sample remain `pending_confirmation` until the user explicitly carries them into the current request; do not search for or reuse a semantically similar Plan as evidence for the first response.
- Use one entry Agent for routing, consolidated questions, and final delivery. Assign one owner to each stage.
- For the full path, publish `SceneSpec`, `DataContract`, `PredictionArtifact`, `OptimizationSpec`, `SolveResult`, `ValidationReport`, and `DeliveryBundle` in dependency order through `TeamArtifact`.
- When training data exists, call `OptimizationPredict`; use ordered holdout, train-only imputation, tuning, metrics, baseline comparison, and explicit fallback rules.
- Compile general models with `OptimizationCompile`, solve once with `MindOptSolve`, and retain status, variables, objective, request/job IDs, HTTPS transport, solver evidence, and IIS when infeasible.
- Require the validation owner to call `OptimizationValidate` and recompute variable domains, hard constraints, objective, baseline delta, and IIS traceability from raw values.
- Treat every settled successful Tool call as authoritative. After an interruption, synthesize the persisted result without repeating the Tool.

## L2

- Until the fact-confirmation gate passes, clarify only: do not publish modeling artifacts, call a solver, delegate a solver-capable Agent, or fill hidden conditions with defaults, simulations, or industry convention.
- Interaction mode changes terminology, grouping, per-turn batch size, and example depth only. It never changes fact states, mandatory information, triggered conditions, the modeling-confirmation summary, or the stop gate. The user's explicit choice in the current request overrides historical preference; switching mode preserves confirmed facts and continues with every remaining item.
- If the user cannot confirm an item, deliver the gap, model impact, required owner/data, and optional reduced scope. Never interpret an omitted answer as absent, false, zero, or unlimited.
- Use the fast path only when the user supplied a complete `OptimizationSpec`: one solve delegation, one validation delegation, then an entry-owned `DeliveryBundle`.
- Use the full path when objectives, constraints, data definitions, or predictive inputs still need modeling. Never advance a stage before its declared dependencies are complete.
- Do not invent unknown business weights, relax hard constraints silently, treat missing values as zero, or describe an unvalidated solution as executable.
- Non-entry Agents place missing information in the team question queue. Only the entry Agent asks the user.
- Obtain connector secrets only from declared connection references. Never request, reveal, or persist tokens, CA material, client certificates, private keys, endpoints, SSH commands, or tunnels in artifacts.
- If the solver reports infeasible, preserve and explain its IIS; if validation fails, deliver the failure and violated checks instead of modifying variables or re-solving.
