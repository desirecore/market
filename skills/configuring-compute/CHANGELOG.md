# Changelog

## [1.0.2] - 2026-07-11

- 修复“配置算力”市场图标引脚不对称且贴近 viewBox 边缘导致的显示异常

## [1.0.0] - 2026-07-07

- 首个版本：通过 Agent Service HTTP API 配置算力供应商与 API Key
- 密钥只写不读安全模型（secrets 端点只写、config 响应掩码、明文查看仅限用户 UI）
- 完整流程：查看配置 → 创建/更新 provider → 写入密钥 → 验证 → 启用/同步模型 → reload 刷新
