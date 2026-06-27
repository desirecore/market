use std::fs;
use std::path::Path;

use anyhow::Result;
use clap::{ArgMatches, Command, FromArgMatches, Subcommand};
use serde_json::json;

use crate::paths;

/// 管理本地缓存
#[derive(Subcommand)]
pub enum CacheCmds {
    /// 显示本地缓存状态
    #[command(disable_help_flag = true)]
    Status,
    /// 清除本地缓存
    #[command(disable_help_flag = true)]
    Clear,
}

pub fn build_cache_cmd() -> Command {
    CacheCmds::augment_subcommands(Command::new("cache"))
        .disable_help_flag(true)
        .disable_help_subcommand(true)
        .subcommand_required(true)
        .arg_required_else_help(true)
}

pub async fn handle_cache_cmd(matches: &ArgMatches) -> Result<()> {
    let args = CacheCmds::from_arg_matches(matches);
    let cache_dir = paths::cache_dir();
    match args {
        Ok(CacheCmds::Status) => handle_cache_status(&cache_dir),
        Ok(CacheCmds::Clear) => handle_cache_clear(&cache_dir),
        _ => anyhow::bail!("未知命令"),
    }
}

/// 列出当前缓存目录下所有文件及其修改时间。
fn handle_cache_status(cache_dir: &Path) -> Result<()> {
    let files = collect_cache_files(cache_dir);

    let mut entries: Vec<serde_json::Value> = files
        .iter()
        .filter_map(|path| {
            let metadata = fs::metadata(path).ok()?;
            let modified = metadata
                .modified()
                .ok()?
                .duration_since(std::time::UNIX_EPOCH)
                .ok()?
                .as_secs();
            Some(json!({
                "file": path.file_name().unwrap_or_default().to_string_lossy(),
                "update_time": modified,
            }))
        })
        .collect();

    entries.sort_by(|a, b| {
        a["file"]
            .as_str()
            .unwrap_or_default()
            .cmp(b["file"].as_str().unwrap_or_default())
    });

    println!(
        "{}",
        serde_json::to_string_pretty(&entries).unwrap_or_default()
    );
    Ok(())
}

/// 清除缓存目录下所有文件。
fn handle_cache_clear(cache_dir: &Path) -> Result<()> {
    let mut removed = Vec::new();

    for path in collect_cache_files(cache_dir) {
        match fs::remove_file(&path) {
            Ok(()) => {
                removed.push(
                    path.file_name()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .to_string(),
                );
            }
            Err(e) => {
                tracing::warn!(path = %path.display(), error = %e, "删除缓存文件失败");
            }
        }
    }

    let output = if removed.is_empty() {
        json!({
            "status": "success",
            "message": "未找到需要删除的缓存文件",
        })
    } else {
        json!({
            "status": "success",
            "message": format!("已删除 {} 个缓存文件", removed.len()),
            "removed": removed,
        })
    };

    println!(
        "{}",
        serde_json::to_string_pretty(&output).unwrap_or_default()
    );
    Ok(())
}

/// 收集缓存目录下所有常规文件的路径。
fn collect_cache_files(cache_dir: &Path) -> Vec<std::path::PathBuf> {
    let Ok(read_dir) = fs::read_dir(cache_dir) else {
        return Vec::new();
    };
    read_dir
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.is_file())
        .collect()
}
