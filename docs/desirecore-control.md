# Install DesireCore Control from the marketplace

DesireCore Control is a standalone application for external agents such as ChatGPT and Codex. MCP is its outward protocol, not an internal DesireCore service registration. Version 1.4.0 includes a local dashboard, multi-instance discovery and managed startup/shutdown/readiness observations for the official ChatGPT tunnel client.

## Application catalog

The marketplace's application data comes from [desirecore/registry](https://github.com/desirecore/registry); this repository maintains Agents, Teams and Skills. The authoritative application entry is [entries/desirecore-control](https://github.com/desirecore/registry/tree/main/entries/desirecore-control). Do not create a second MCP service listing or mislabel the application as Docker.

On a compatible client, synchronize the catalog and search for **DesireCore Control** under **Market → Applications**. Verify version **1.4.0** before requesting installation. The listing requires native-app client support (minimum **10.0.169**) and the core Agent's **app-install-manager 1.4.0**. Catalog sync does not update the desktop client or Agent skills. An older client may omit the entry or require an upgrade; do not change its type or bypass receipt/version checks. Marketplace installation remains unavailable until the required client and skill are actually deployed.

The installer uses the resolver-authorized fixed release URL and SHA-256, installs into an independent user directory, verifies the installed version and empty-instance startup, then records an App receipt. It does not start DesireCore, register internal MCP tools, enable control/tunnels, or install an autostart hook. Installed and running are distinct states.

## After installation

Start Control using the resource action or the exact independent command returned by the installer, then open its local dashboard in the system browser. Install the official tunnel client separately. Enter the Tunnel ID and runtime key locally, never in the marketplace installation conversation. Normal Control shutdown reaps only its owned tunnel, not DesireCore.

## Maintenance

[desirecore-agent/desirecore-cdp-mcp](https://github.com/desirecore-agent/desirecore-cdp-mcp) maintains the MIT-licensed application and releases. Registry owns its catalog metadata and pinned lifecycle guide; app-install-manager executes authorized installation and writes exact receipts; the desktop client projects native-app records and launch entries. Publishing only one repository is not evidence that the entire installation chain is deployed.

Updates and uninstallation preserve exact source/device/operationId ownership and the original lifecycle receipt. No internal services are derived. Deleting user credentials or data requires separate consent. Use the Registry's currently authorized install.md rather than stale chat instructions.
