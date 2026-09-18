# Install DesireCore Control from the marketplace

DesireCore Control is a standalone application for external agents such as ChatGPT and Codex. MCP is its outward protocol, not an internal DesireCore service registration. Version 1.4.0 includes a local dashboard, multi-instance discovery and managed startup/shutdown/readiness observations for the official ChatGPT tunnel client.

## Application catalog

The marketplace's application data comes from [desirecore/registry](https://github.com/desirecore/registry); this repository maintains Agents, Teams and Skills. The authoritative application entry is [entries/desirecore-control](https://github.com/desirecore/registry/tree/main/entries/desirecore-control). Do not create a second MCP service listing or mislabel the application as Docker.

On a compatible client, synchronize the catalog and search for **DesireCore Control** under **Market → Applications**. Verify version **1.4.0** before requesting installation. The listing requires native-app client support (minimum **10.0.169**) and the core Agent's **app-install-manager 1.4.0 or newer**. Catalog sync does not update the desktop client or Agent skills. An older client may omit the entry or require an upgrade; do not change its type or bypass receipt/version checks. Marketplace installation remains unavailable until the required client and skill are actually deployed.

The installer uses the resolver-authorized fixed release URL and SHA-256, installs into an independent user directory, verifies the installed version and empty-instance startup, then records an App receipt. It does not start DesireCore, register internal MCP tools, enable control/tunnels, or install an autostart hook. Installed and running are distinct states.

## After installation

Start Control using the resource action or the exact independent command returned by the installer, then open its local dashboard in the system browser. The optional official `tunnel-client` is separately installed, not bundled with Control. In the local ChatGPT tunnel panel, first enter the per-run `admin-token` from the private file identified by Control's terminal output, then provide the Tunnel ID and runtime API key. This management token is separate from Control's outward MCP token and the OpenAI runtime key; never send any of them to the marketplace installation conversation. Normal Control shutdown terminates only the `tunnel-client` process it owns, not DesireCore or other tunnel clients, and does not delete the Tunnel configured on OpenAI Platform.

### Optional external dependency: OpenAI tunnel

Before enabling a tunnel, follow the [official setup guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels): obtain a Tunnel associated with the intended organization/workspace, a dedicated runtime key with Tunnels Read + Use, separate ChatGPT developer-mode permission, and outbound HTTPS access. Creating or editing a Tunnel additionally requires Manage permission. The user installs a compatible official binary and verifies its license/notices; Control's MIT license does not replace those terms.

OpenAI usage is governed by the applicable [terms and policies](https://openai.com/policies/) and the user's subscription/order/account billing. No free tunnel service, free model use or inclusion in the Control installation price is promised. Confirm applicable costs locally before enabling the optional connection. If the binary or permission is missing, do not start the tunnel or fall back to public CDP. If readiness is false or unknown, do not issue ChatGPT tool operations: check the client installation, account association and connectivity first. A running process is not readiness, and readiness is not end-to-end acceptance. Control's local dashboard remains available without a tunnel; disabling this optional connection does not uninstall Control.

## Maintenance

[desirecore-agent/desirecore-cdp-mcp](https://github.com/desirecore-agent/desirecore-cdp-mcp) maintains the MIT-licensed application and releases. Registry owns its catalog metadata and pinned lifecycle guide; app-install-manager executes authorized installation and writes exact receipts; the desktop client projects native-app records and launch entries. Publishing only one repository is not evidence that the entire installation chain is deployed.

Updates and uninstallation preserve exact source/device/operationId ownership and the original lifecycle receipt. No internal services are derived. Deleting user credentials or data requires separate consent. Use the Registry's currently authorized install.md rather than stale chat instructions.
