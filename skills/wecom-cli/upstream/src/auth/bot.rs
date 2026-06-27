use std::fs;
use std::time::{SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};

use anyhow::Result;

use crate::{crypto, fs_util, paths};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bot {
    // Bot ID
    pub id: String,
    // Bot Secret
    pub secret: String,
    // Creation timestamp (unix epoch seconds)
    pub create_time: u64,
}

impl Bot {
    /// Create a new Bot with `create_time` set to the current timestamp.
    pub fn new(id: String, secret: String) -> Self {
        let create_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        Self {
            id,
            secret,
            create_time,
        }
    }
}

/// Read encrypted bot info from disk, decrypt and return it.
/// Returns `None` if the file does not exist or decryption fails.
pub fn get_bot_info() -> Option<Bot> {
    let data = fs::read(bot_info_path()).ok()?;
    crypto::try_decrypt_data(&data).ok()
}

/// Serialize bot info, encrypt and persist to disk.
/// The encryption key is stored in the system keyring when possible, otherwise falls back to an encrypted file.
pub fn set_bot_info(bot: &Bot) -> Result<()> {
    // 1. Load or generate an encryption key
    let key = crypto::load_existing_key().unwrap_or_else(|| {
        let k = crypto::generate_random_key();
        tracing::info!("已生成新的加密密钥");
        k
    });

    // 2. Persist the key (prefer keyring, fall back to file)
    crypto::save_key(&key)?;

    // 3. Serialize bot info → JSON → encrypt
    let encrypted = crypto::encrypt_data(bot, &key)?;

    // 4. Write to file
    let path = bot_info_path();
    fs_util::atomic_write(&path, &encrypted, Some(0o600))?;

    tracing::info!("企业微信机器人信息已保存到 {}", path.display());
    Ok(())
}

/// Remove the stored Bot info from disk.
pub fn clear_bot_info() {
    let path = bot_info_path();
    if path.exists() {
        let _ = fs::remove_file(&path);
        tracing::info!("机器人信息已删除：{}", path.display());
    }
}

/// Return the file path for the encrypted bot credentials.
fn bot_info_path() -> std::path::PathBuf {
    paths::wecom_home_dir().join("bot.enc")
}
