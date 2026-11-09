---
{
  "name": "tool-mcp-authoring",
  "description": "Use when the user needs to build, package or modify a custom Tool, MCP Server or device-protocol integration. Reuse existing execution and approval contracts. Requires actual runtimes, drivers/libraries and authorized devices/services; third-party licenses, deployment and costs depend on the chosen dependencies. Report missing prerequisites.",
  "license": "MIT",
  "compatibility": "Requires DesireCore 10.0.203 or newer and actually available file/execution/configuration capabilities. Runtimes, third-party drivers/libraries, hardware and hosted services are not bundled by this Skill and require their applicable license, deployment, authorization and costs. Report unavailable prerequisites.",
  "version": "1.0.1",
  "requiredClientVersion": "10.0.203",
  "type": "procedural",
  "risk_level": "medium",
  "status": "enabled",
  "disable-model-invocation": true,
  "tags": [
    "tools",
    "mcp",
    "development",
    "devices"
  ],
  "metadata": {
    "author": "desirecore",
    "updated_at": "2026-11-09",
    "i18n": {
      "default_locale": "en-US",
      "source_locale": "zh-CN",
      "locales": [
        "zh-CN",
        "en-US"
      ],
      "zh-CN": {
        "name": "自建 Tool 与 MCP",
        "short_desc": "编写、登记和验证可复用工具与 MCP 服务",
        "description": "在用户需要自主编写、封装或修改自定义 Tool、MCP Server 或设备协议接入能力时使用。复用现有执行与审批合同；依赖真实可用的运行时、驱动/库及获准设备或服务，第三方许可、部署和费用按所选依赖确认，缺条件时报告。",
        "body": "./SKILL.zh-CN.md",
        "source_hash": "sha256:4a1d9c15821f8571",
        "translated_by": "ai:gpt-6",
        "translated_at": "2026-11-09"
      },
      "en-US": {
        "name": "Self-authored Tools and MCP",
        "short_desc": "Build, register and verify reusable tools and MCP services",
        "description": "Use when the user needs to build, package or modify a custom Tool, MCP Server or device-protocol integration. Reuse existing execution and approval contracts. Requires actual runtimes, drivers/libraries and authorized devices/services; third-party licenses, deployment and costs depend on the chosen dependencies. Report missing prerequisites.",
        "body": "./SKILL.md",
        "source_hash": "sha256:4a1d9c15821f8571",
        "translated_by": "ai:gpt-6",
        "translated_at": "2026-11-09"
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

# Self-authored Tools and MCP

## Choose the delivery

Implement the requested capability as verifiable code and contracts that remain usable. The Agent chooses language, libraries and approach; the platform supplies original file tools, execution, discovery, approvals and runtime facts without imposing a business workflow.

| User goal | Possible carrier |
|---|---|
| One diagnosis, read or conversion | A script in the authorized workspace |
| Reusable atomic operation with an input schema | An AgentFS custom Tool |
| Operations sharing a device connection or service state | A self-authored MCP Server attached to the actual Agent Service |
| Reusable method, conventions and supporting scripts | A Skill; it does not register a function tool by itself |
| Configuration UI, multiple devices, installable delivery | An application or plugin, optionally composing existing Tool/MCP capabilities |

Check existing capabilities and the user's choice. An explicit request to build can proceed directly without searching the market first. For application delivery, load the application authoring Skill from the actual directory: authoring actions use `AppAuthoring`, installation lifecycle uses `AppManage`.

## Use real environments and original authority

- Continue the current Plan, work directory and authorization. Creating a tool does not justify changing approval mode, extracting a platform token or widening a child task's authority. Another Agent's installation/configuration needs its original authorization.
- Probe actual runtimes, libraries, drivers and devices/services. Prepare missing prerequisites through available runtime Skills or original execution tools, recording versions and location. Third-party libraries, hardware and hosted services retain their license, deployment and cost requirements; report unavailable prerequisites.
- Keep reviewable code/configuration in permitted directories, private device settings and credentials in private configuration or original connection owners, and out of public Skills, CLI arguments, logs and examples. Registering a connector does not provide external hardware, licenses or services.
- Derive serial ports, baud rates, addresses and endpoints from the actual device and protocol material. Provide descriptions in configuration/parameter schemas. Classify read/write risk by actual effects and test authorized read-only operations or simulated endpoints first without calling them physical-device evidence.

## Read the relevant authoring contract

- Atomic scripts, complete TOOL.md, registration and discovery: [AgentFS Tool](references/agentfs-tool.md).
- Local/remote MCP, dependencies, connections and sharing: [MCP service](references/mcp-server.md).
- For reusable operating methods, load Skill authoring/management guidance from the actual directory. For a shared HTTP/MCP catalog, load service-registration guidance. Attaching MCP to yourself needs no global listing.

## Verify results and lifecycle

Report separately: source/dependencies prepared, configuration saved, registration/discovery successful, actual invocation successful, device behavior observed and restart recovery verified. Earlier stages do not establish later ones.

After registry refresh, call actual current catalog/declaration names. Loading does not increase authority; a worker/background Run with a fixed tool ceiling cannot bypass it by creating new capabilities. Use the error and original context to choose a subsequent turn, a suitable execution Agent or a precise authorization requirement instead of blindly loading again.

Continuous subscriptions such as MQTT need a real process/service carrier and an explicit path through an authorized existing schedule, Webhook or other real ingress to the Agent. MCP list-change notifications are not a general device-event wakeup facility. A saved config, one background command or registered MCP does not prove listening survives an application restart. If choosing scheduling, use `ManageSchedule` rather than writing persistent schedule files directly.

Verify relevant device ownership, timeout, cancellation, disconnect/recovery and concurrency for the chosen delivery. Reconcile uncertain device writes before deciding to retry. Close/remove only your owned connections, processes and registrations rather than shared services. Deliver actual entrypoints, call examples and unverified limits without packaging every simple script as an application.
