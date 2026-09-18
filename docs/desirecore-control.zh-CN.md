# 从市场安装 DesireCore Control

DesireCore Control 是面向 ChatGPT、Codex 等外部智能体的独立应用，MCP 只是对外协议。它不向 DesireCore 内部智能体注册 MCP，不随 DesireCore 启停。1.4.0 包含本机实例管理及官方 ChatGPT tunnel-client 的启停与就绪检查。

## 应用目录

市场的“应用”数据来自 [desirecore/registry](https://github.com/desirecore/registry)，本仓库维护 Agent/Team/Skill。应用的正式索引为 [entries/desirecore-control](https://github.com/desirecore/registry/tree/main/entries/desirecore-control)，不是本仓库的 MCP 服务条目。不要复制成第二份服务或伪装成 Docker。

在支持原生应用的 DesireCore 客户端中同步市场目录，然后在“市场 → 应用”搜索 **DesireCore Control**，核对版本 **1.4.0** 并发起安装。安装流程要求 `native-app` 客户端支持（条目标注最低 **10.0.169**）和应用安装管理技能 **1.4.0**。同步目录不会自动升级桌面客户端或核心智能体技能；旧版看不到条目或提示升级时，不应改类型、重建收据或绕过版本检查。客户端尚未发布或技能尚未更新时，市场一键安装仍不可用。

安装器使用受信 resolver 的固定版本、下载地址和 SHA-256。默认安装在独立用户目录，验证包版本与空实例启动后才回写 App 安装收据。不会启动真实 DesireCore 实例，不创建内部 MCP，不默认启用控制、隧道或开机启动。应用安装成功和应用进程运行是两个状态。

## 安装后

使用资源中的启动操作或安装器给出的准确独立命令启动 Control，在系统浏览器打开本机管理页。ChatGPT 隧道客户端需单独安装；Tunnel ID 和运行 key 由用户在本机页面提供，不能发到市场安装对话。正常退出 Control 时只清理自己的隧道，不停止 DesireCore。

## 维护与版本

应用实现与 MIT 发行包由 [desirecore-agent/desirecore-cdp-mcp](https://github.com/desirecore-agent/desirecore-cdp-mcp) 维护。Registry 负责市场分类、版本、固定制品及生命周期指南；核心 Agent 的 app-install-manager 负责按 App 授权执行安装与回写；DesireCore 客户端负责 native-app 的目录和安装投影。单独更新其中一个仓库不能证明整个安装链路已经部署。

升级/卸载保留精确来源、设备、operationId 与原始生命周期收据，不派生服务；用户数据和凭据的删除需要独立确认。完整命令以 Registry 当前被审核的 install.md 为准，不从聊天历史取过期步骤。
