pub(crate) mod config;
pub(crate) mod error;

use anyhow::Result;
use rand::Rng;

use crate::service::categories;

/// Look up the MCP URL for the given `category` (matched against `biz_type`).
pub async fn get_mcp_url(category: &str) -> Result<String> {
    let Some(list) = config::load_mcp_config() else {
        return Err(anyhow::anyhow!(
            "未找到 MCP 配置缓存，请先运行 `{} init`",
            env!("CARGO_BIN_NAME")
        ));
    };

    let permission_name = categories::get_categories()
        .iter()
        .find(|c| c.name == category)
        .map(|c| c.permission_name)
        .unwrap_or(category);

    let target = list
        .iter()
        .find(|item| item.biz_type.as_deref() == Some(category))
        .ok_or_else(|| {
            anyhow::anyhow!("当前企业暂不支持授权机器人「{permission_name}」使用权限")
        })?;

    target
        .url
        .clone()
        .ok_or_else(|| anyhow::anyhow!("MCP 配置中 {category} 的 url 为空"))
}

/// Generate a request ID in the format: `{prefix}_{timestamp_ms}_{random_hex}`.
pub fn gen_req_id(prefix: &str) -> String {
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis();
    let random = generate_random_hex(8);
    format!("{prefix}_{timestamp}_{random}")
}

/// Generate a random hex string of the specified character length.
fn generate_random_hex(length: usize) -> String {
    let byte_len = length.div_ceil(2);
    let bytes: Vec<u8> = (0..byte_len).map(|_| rand::rng().random::<u8>()).collect();
    let hex = hex::encode(bytes);
    hex[..length].to_string()
}
