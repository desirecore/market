/// 尝试使用系统默认浏览器打开指定 URL。
/// - 使用 `open` crate 跨平台打开浏览器（macOS: `open`、Windows: `ShellExecuteW`、Linux: `xdg-open`）。
/// - 打开失败不会中断主流程，仅记录日志。
pub fn open_url_by_browser(url: &str) {
    tracing::debug!(url, "正在使用默认浏览器打开链接");

    open::that(url).unwrap_or_else(|err| {
        tracing::debug!(url, %err, "无法打开默认浏览器，请手动在浏览器中打开链接");
    });
}
