/// Sanitize a file name by removing illegal characters; returns `None` if the result is empty.
pub fn sanitize_filename(name: &str) -> Option<String> {
    let options = sanitize_filename::Options {
        truncate: true,
        windows: true,
        replacement: "_",
    };
    let sanitized = sanitize_filename::sanitize_with_options(name, options);
    // Return None if the sanitized result is empty (all illegal characters), so the caller can fallback
    if sanitized.is_empty() {
        None
    } else {
        Some(sanitized)
    }
}
