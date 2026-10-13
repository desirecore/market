---
{
  "name": "app-developer",
  "description": "用户要求开发、修改或发布自己的工作台应用，或把固定应用版本分发到 GitHub/Gitea 与 Registry 时使用。按所选技术栈使用的外部 Node/Docker 运行时、托管、Git 服务和数据库须有真实环境或连接及适用条款，可能另行部署或收费；缺能力时说明原因。",
  "license": "MIT",
  "compatibility": "Requires DesireCore app-authoring-v1 capability handshake. Depending on the chosen stack, Node/Docker runtimes, hosting, GitHub/Gitea and databases require actual authorized environments or connections and applicable licensing/deployment terms; separate costs may apply. Unavailable capabilities stop the affected operation.",
  "version": "1.0.0",
  "requiredClientVersion": "10.0.180",
  "type": "procedural",
  "risk_level": "high",
  "status": "enabled",
  "disable-model-invocation": true,
  "provides": {
    "tools": [
      "HttpRequest"
    ]
  },
  "tags": [
    "application",
    "workbench",
    "development",
    "publishing"
  ],
  "metadata": {
    "author": "desirecore",
    "updated_at": "2026-10-13",
    "i18n": {
      "default_locale": "en-US",
      "source_locale": "zh-CN",
      "locales": [
        "zh-CN",
        "en-US"
      ],
      "zh-CN": {
        "name": "应用开发与发布",
        "short_desc": "开发个人工作台并发布到我的应用，按需分发固定版本",
        "description": "用户要求开发、修改或发布自己的工作台应用，或把固定应用版本分发到 GitHub/Gitea 与 Registry 时使用。按所选技术栈使用的外部 Node/Docker 运行时、托管、Git 服务和数据库须有真实环境或连接及适用条款，可能另行部署或收费；缺能力时说明原因。",
        "body": "./SKILL.zh-CN.md",
        "source_hash": "sha256:0c8e3d49d807e945",
        "translated_by": "ai:gpt-6",
        "translated_at": "2026-10-13"
      },
      "en-US": {
        "name": "Application Development and Publishing",
        "short_desc": "Develop a personal workbench, publish it to My Apps, and distribute fixed releases on request",
        "description": "Use when the user asks to develop, modify or publish a personal workbench application, or distribute a fixed release through GitHub/Gitea and Registry. Node/Docker runtimes, hosting, Git services and databases used by the chosen stack need actual environments or connections and applicable terms; separate deployment or costs may apply. Report unavailable capabilities.",
        "body": "./SKILL.md",
        "source_hash": "sha256:0c8e3d49d807e945",
        "translated_by": "ai:gpt-6",
        "translated_at": "2026-10-13"
      }
    }
  },
  "market": {
    "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"white\" stroke-width=\"1.6\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"3\"/><path d=\"M3 8h18M8 8v13M12 13h5M12 17h5\"/></svg>",
    "category": "development",
    "maintainer": {
      "name": "DesireCore Official",
      "verified": true
    },
    "channel": "latest"
  }
}
---

# Application Development and Publishing

## L0: Responsibility

The Agent chooses the implementation, framework and working method. The platform verifies material identity, scope, publication, runtime and collaboration facts. Reuse file and execution tools, Task/Run and the existing installation writer. Do not create a fixed business workflow or execute commands extracted from installation prose.

## L1: Read Capabilities and Context

1. Read or create the task's single file-based Plan, preserving the actual Agent/session, device, authorized work directory and development Task. Continue within the user's existing requirements and authorization.
2. Use the current authorized HttpRequest connection to read `GET /api/apps/capabilities`. Require `protocol: app-authoring-v1` and inspect supported, authorized, available and reason independently. The minimum client version is a code baseline; an already released client with the same version string does not thereby support this protocol.
3. Natural-language development needs no additional handoff protocol. Installation, registration, update or uninstall continues through ApplicationManagement-v2 and the single writer. Read `app-install-manager` when available; never edit installed-entries.json directly.
4. Read [authoring interfaces](references/authoring-api.zh-CN.md) and [distribution](references/distribution.zh-CN.md) on demand. The candidate main-repository authority is `docs/功能/市场系统/API/应用开发发布接口.md`; an external PR does not establish a shipped client or official seed. `examples/static-workbench/` and `examples/service-workbench/` are editable teaching materials, not evidence of autonomous Agent development or production acceptance.

## L2: Development, Preview and Personal Publication

- Establish the user's actual work, data ownership and collaboration needs. Choose suitable languages and frameworks; examples do not prescribe a stack. Reuse the actual Task, Plan and originating context.
- Separate program material, business data and secrets. The portable `application.json` contains no sourceId, installation identity, host path, builtin route or credential. Its product identity, version and entrypoints are the single source for release and catalog views.
- Create fixed `app-release.json` from an explicit file whitelist, actual byte hashes, entrypoint mappings, data contract and truthful platform evidence. Exclude the manifest itself from files. `scripts/create-release.mjs` builds the example manifest; the service independently verifies actual bytes.
- Deliver `app-draft.json` with real fileRef, Plan, Agent/session, stable draftId and target installationId. Its workdir points to the actual release material directory; do not guess a release/ subdirectory or fabricate a fileRef. Return a clickable absolute path so the user can read and continue it in the application development workspace.
- Snapshot preview and formal installation use separate identities and data. Freeze a snapshot before publishing a live preview. Replacement uses the actual revision. Ending preview revokes its bridge and disposes only its owned temporary runtime while preserving data and development material. Closing a page does not stop a formal application or accepted Task. Never convert a temporary URL/token into a formal entrypoint.
- A real authorized source development server uses `runtime/development-contracts` for live preview. Its development-only contract cannot become formal startup; mutable source and fixed releases remain separate. The original command must respect owner-injected PORT and APP_DATA_DIR, using shell `${VAR:-default}` only for initial defaults rather than overriding preview ports or formal data roots.
- Personal publication uses prepare, candidate inspection and commit with exact digest, instance, revision and submission ID. Continue authorized publication without repeated per-command questions; new targets or additional data/external effects follow existing governance.
- Saving a release and making it runnable are separate facts. Static files use fixed mappings; services use real original-owner spawn, generation and handshake. Docker releases declare complete registry/repository@sha256 imageRefs, then use `runtime/docker/enrollments/prepare` to receive owned CID/env paths and the actual command. Execute it through original TaskHost approval, then enroll the real terminalId and verify daemon/CID/RepoDigest/mount/port facts. Normal create/start/stop repeats current approval; internal transient preview disposal compensates only its originally approved owned CID; candidate, formal and preview roots/nonces differ. Reconcile unknown outcomes against the original CID before another effect. Missing adapters or supported environments keep the original Agent-managed lifecycle with an honest reason. A CLI exit, format check, port, PID or historical observation does not prove availability.
- For timeout, lost response or disconnection, preserve the original mutation/submission/clientRequest ID and body and query the original result. Do not blindly replay unknown writes with a new ID. Check current material and data compatibility before an update. Investigate interrupted migrations; code rollback is not data recovery.

## L3: Webpage and Agent Collaboration

The webpage uses the finite `window.desirecoreApp.call(method,payload)` and `onEvent` API; Web uses a MessagePort from an independent origin. There is no Conveyor, arbitrary invoke, platform administrator token, arbitrary file proxy or general fetch tool. Disable unavailable or unauthorized actions with the actual reason.

- Formal `connect.application` supplies only the application's source/app/instance prefix. Object namespace, ID and revision need an actual owner. The examples reference the declared notes source file with namespace data-files, objectId notes and the actual readData ETag; they do not invent an owner for individual JSON note objects. The selected note's ID, record version and visible fields remain in the summary. Preview discusses the summary without borrowing a formal instance identity.
- Persist only declared data keys through readData/saveData with expectedAbsent or expectedETag. Recover unknown writes using the original mutationId. A native backend needs a separately authorized data root and must not write business databases into a fixed release directory.
- Publish selections if needed and call prepareWork to propose work. The platform owns final acceptance: native uses real input proof and one-use intent, while Web uses the original trusted chat admission transport. A webpage cannot sign native physical input proof. A proposalRef is not a Task receipt. Only actual reserved/committed work-accepted results establish acceptance; queued does not mean completed.
- Reconnect and lookup preserve the original `{agentId,clientRequestId}`. A reset_required gap needs a fresh snapshot and valid cursor. controlWork uses only actual availableActions, currently abort, without general resume. readWork.resources contains original Task-owned task-binding locators; `openResource({locator})` returning navigation-requested requests platform navigation and does not prove file content loaded. data-files objects use exact authorized references in a read-only inspector. Never fabricate FileRefs/URLs or treat unsupported navigate as a grant.
- Business content stays with its data owner. View state defaults to memory. Device persistence needs an explicit user choice, a declared viewStateContract with finite keys/bytes/format, and saveViewState permission. connect returns actual device readiness and per-key revisions. Keep the original mutationId, expectedRevision and body for unknown CAS writes. Store necessary filter/selection/position only, without business content or credentials.
- Web hosting needs owner-configured TLS, domain, DNS and actual public port. The trusted shell obtains its ticket and explicitly requests SDK bootstrap. Missing host/SDK configuration remains unavailable; never disable TLS verification or allow an application-selected upstream URL/management port.

## L4: Distribution and Evidence

Personal publication is private and local by default. When the user requests distribution, export the fixed complete whitelist and review the exact files and actual target. Exclude databases, .env, credentials, chats, Task/Plan, logs, machine paths and installation identity. Environment templates can describe names without real secret values.

Use already authorized GitHub/Gitea tools to upload and inspect immutable source/artifact results. Then generate Registry manifest.json, catalog-metadata.v1.json and install.md from the same exportRef. The target Provider injects catalog identity; the personal installation remains unchanged. Verify archiveDigest, releaseDigest and source-materialized descriptorDigest independently. A different payload under the same version requires a new revision, not overwriting fixed material.

Report code/functional verification, preview, personal saving, runtime availability, upload, catalog PR/admission and second-user installation independently. A candidate 4.3 Schema, external PR or generated ZIP does not establish official-market availability, client capability release or another device's runtime acceptance. External hosting, databases and Git services require actual connections and applicable licensing/deployment terms and can carry separate costs; when unavailable, stop the affected external operation.
