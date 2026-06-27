use tracing_subscriber::prelude::*;

use crate::constants::env;

/// Initialize the tracing subscriber with optional stderr and file logging layers.
pub fn init_logging() {
    let stderr_filter = std::env::var(env::LOG_LEVEL).ok();
    let log_file_dir = std::env::var(env::LOG_FILE).ok();

    if stderr_filter.is_none() && log_file_dir.is_none() {
        return;
    }

    let registry = tracing_subscriber::registry();

    // Stderr layer: human-readable
    let stderr_layer = stderr_filter.map(|filter| {
        let env_filter = tracing_subscriber::EnvFilter::new(filter);
        tracing_subscriber::fmt::layer()
            .with_writer(std::io::stderr)
            .with_target(false)
            .compact()
            .with_filter(env_filter)
    });

    // File layer: JSON-line output with daily rotation
    let (file_layer, guard) = if let Some(ref dir) = log_file_dir {
        let file_appender = tracing_appender::rolling::daily(dir, "ww.log");
        let (non_blocking, guard) = tracing_appender::non_blocking(file_appender);
        let layer = tracing_subscriber::fmt::layer()
            .json()
            .with_writer(non_blocking)
            .with_target(true)
            .with_filter(tracing_subscriber::EnvFilter::new("ww=debug"));
        (Some(layer), Some(guard))
    } else {
        (None, None)
    };

    // Compose layers and set as global subscriber.
    // The guard is leaked intentionally so the non-blocking writer stays
    // alive for the lifetime of the process.
    let subscriber = registry.with(stderr_layer).with(file_layer);
    if tracing::subscriber::set_global_default(subscriber).is_ok() {
        // Leak the guard so the non-blocking writer lives for the process lifetime.
        // This is the recommended pattern from tracing-appender docs.
        std::mem::forget(guard);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_init_logging_default_no_panic() {
        unsafe { std::env::remove_var(env::LOG_LEVEL) };
        unsafe { std::env::remove_var(env::LOG_FILE) };
        init_logging();
    }
}
