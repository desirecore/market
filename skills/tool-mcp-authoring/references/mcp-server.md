# Self-authored MCP connection contract

Use when operations share connection/state or other MCP clients need the capability. Choose the implementation language and SDK. Implement initialization, listing, parameter schemas and calls against the chosen installed SDK's actual protocol and documentation; never fabricate success receipts.

## Service, dependencies and host

Keep source, dependency manifests/locks and configuration schemas in authorized directories. Use the actual runtime path. A local stdio process writes only MCP protocol to stdout and diagnostics to stderr. Verify startup directory and module resolution rather than assuming Electron bundles your library or platform-specific native driver.

Shared state belongs to the actual service process. Multiple Agents configuring the same stdio command normally start separate processes and do not automatically share serial handles. For an exclusive shared device, choose an appropriate governed service owner or explicit connection/locking design. MCP does not inherently serialize requests: implement device queues, concurrency and disconnect recovery as the protocol requires. The same mount name or a catalog listing does not resolve resource contention.

Identify the Agent Service host that accesses the device. A remote server's COM/USB devices are not the browser computer's hardware. External libraries, hardware and hosted services require their actual licenses, deployment and authorization; registering a connection does not provide them. Stop the affected operation and report missing prerequisites.

## Attach to your own Agent

The current McpConnectionRequest/Schema defines the accepted request. Through the current permitted local API path, optionally `POST /api/mcp/test-connection` with `{connection: <connection request>}`, then `POST /api/agents/<own-id>/mcp-servers`, for example:

```json
{
  "serverId": "example-device",
  "config": {
    "transport": "stdio",
    "command": "<actual absolute Node executable on the host>",
    "args": ["<absolute installed server entry>"],
    "cwd": "<absolute authorized service directory>"
  }
}
```

Replace angle-bracket placeholders with actual paths before execution. Keep executable/args separate. Use original connection/secret-reference facilities for sensitive values, never platform tokens/passwords in source or CLI arguments. Connection requests and persisted agent.json mcp_servers entries have different shapes: let this endpoint convert, or inspect the actual agent.json Schema before using authorized file tools to edit your own configuration followed by `RefreshAgentFS(changeTypes=["agent"])`. `ManageAgent.update` does not accept mcp_servers; its rejection is not lack of MCP support.

Ordinary embedded local non-governance APIs, remote/standalone and mediated modes have different access rules. Follow current prompts and actual permissions. If mediated or unavailable, use an offered original configuration capability or report the missing entry; do not extract platform credentials, forge Origin or borrow another identity. First connection can actually start a process and remains subject to the original file, execution, request and MCP-call approvals.

For remote connections, use the client's actual transport, endpoint and OAuth/secretRef contract. An ordinary self-authored local server needs no invented external catalog acquisition identity. Catalog-owned services retain their original acquisition/installation contract; do not impersonate provenance or replace someone else's installation.

## Discover, reuse and actually invoke

Inspect connection-test lists/diagnostics; handshake and listing do not prove a device operation succeeded. After saving, obtain the real model-facing tool name through current catalog/declarations, using `LoadTools` when needed. Do not guess it from the remote declaration or a namespace convention. A fixed worker/background tool ceiling does not expand when new MCP is registered; choose subsequent execution within original authorization and session state.

Actually invoke an authorized harmless tool, then validate device behavior and relevant errors, disconnect/recovery and concurrent device ownership. For a shared catalog, load a service-registration Skill from the actual directory. Attaching to yourself needs no global listing. Other Agents require their own authorized configuration; discoverable does not mean installed or authorized.

Persisted configuration and a live business subscription are separate facts. Current connection owners manage MCP connections and stdio processes; this is not an OS startup service. Continuous subscriptions need an explicit process lifecycle and a real ingress to the Agent. After restart, inspect configuration, rediscover and call, and separately verify business reconnection. Remove your own configuration through the original `DELETE /api/agents/<own-id>/mcp-servers/<serverId>` contract when appropriate; close only your owned resources through their runtime owner, retain user data and leave shared processes alone.
