use std::{collections::HashMap, path::PathBuf};

use anyhow::Result;
use serde::{Deserialize, Serialize, de::DeserializeOwned};

use crate::{fs_util, json_rpc, paths};

#[derive(Deserialize, Serialize, Clone)]
pub struct ServiceTool {
    pub name: String,
    pub description: Option<String>,

    #[serde(rename = "inputSchema")]
    pub input_schema: Option<serde_json::Value>,

    #[serde(flatten)]
    pub extra_properties: HashMap<String, serde_json::Value>,
}

/// 获取指定品类的工具列表（文件缓存 → 远程请求）
pub async fn get_category_tools(name: &str) -> Result<Vec<ServiceTool>> {
    let cache_file = paths::cache_dir().join(format!("service_{name}.json"));

    if let Some(tools) = get_cache_content::<Vec<ServiceTool>>(&cache_file) {
        return Ok(tools);
    }

    // 远程请求
    let response = json_rpc::send(name, "tools/list", None, None).await?;

    let Some(tools) = response
        .pointer("/result/tools")
        .and_then(|r| serde_json::from_value::<Vec<ServiceTool>>(r.clone()).ok())
    else {
        anyhow::bail!("无法获取 {} 品类的工具列表: {response}", name);
    };

    // 写入文件缓存（失败仅 warn，不阻断主流程）
    if let Ok(json) = serde_json::to_string(&tools) {
        if let Err(e) = fs_util::atomic_write(&cache_file, json.as_bytes(), None) {
            tracing::warn!(path = %cache_file.display(), error = %e, "Failed to write service cache");
        }
    }

    Ok(tools)
}

fn get_cache_content<T: DeserializeOwned>(cache_file: &PathBuf) -> Option<T> {
    let metadata = std::fs::metadata(cache_file).ok()?;
    let modified = metadata.modified().ok()?;

    if modified.elapsed().unwrap_or_default().as_secs() >= 86400 {
        return None;
    }

    let content = std::fs::read_to_string(cache_file).ok()?;
    let result = serde_json::from_str::<T>(&content);

    match result {
        Ok(data) => Some(data),
        Err(e) => {
            tracing::warn!(path = %cache_file.display(), error = %e, "Ignoring corrupted discovery cache");
            None
        }
    }
}
