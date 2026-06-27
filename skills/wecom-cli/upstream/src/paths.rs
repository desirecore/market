use std::path::PathBuf;

use crate::constants::env;

pub fn wecom_home_dir() -> PathBuf {
    if let Ok(dir) = std::env::var(env::CONFIG_DIR) {
        return PathBuf::from(dir);
    }
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".config")
        .join("wecom")
}

pub fn cache_dir() -> PathBuf {
    wecom_home_dir().join("cache")
}

pub fn media_dir() -> PathBuf {
    if let Ok(dir) = std::env::var(env::TMP_DIR) {
        return PathBuf::from(dir).join("media");
    }
    std::env::temp_dir().join("wecom").join("media")
}
