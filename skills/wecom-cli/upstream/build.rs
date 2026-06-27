use std::path::Path;
use std::process::Command;

fn main() {
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap();
    let git_dir = Path::new(&manifest_dir).join(".git");

    // Set up git hooks
    if git_dir.exists() {
        let status = Command::new("git")
            .args(["config", "core.hooksPath", ".githooks"])
            .current_dir(&manifest_dir)
            .status();

        match status {
            Ok(s) if !s.success() => {
                println!(
                    "cargo:warning=⚠️ Failed to set core.hooksPath. Run `git config core.hooksPath .githooks` manually."
                );
            }
            Err(e) => {
                println!(
                    "cargo:warning=⚠️ Failed to run git: {e}. Run `git config core.hooksPath .githooks` manually."
                );
            }
            _ => {}
        }
    }

    println!("cargo:rerun-if-changed=.githooks");
}
