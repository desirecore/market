use crate::auth::{Bot, get_bot_info};
use anyhow::Result;
use clap::{ArgMatches, Args, Command, FromArgMatches, Subcommand};

#[derive(Subcommand)]
#[command(subcommand_required = true, arg_required_else_help = true)]
pub enum AuthSubcmds {
    /// Show current authentication state
    Show(ShowArgs),
}

#[derive(Args)]
pub struct ShowArgs {
    /// 展示认证状态详情
    #[arg(long)]
    pub auth_status: bool,
}

pub fn build_auth_cmd() -> Command {
    AuthSubcmds::augment_subcommands(Command::new("auth")).hide(true)
}

pub async fn handle_auth_cmd(matches: &ArgMatches) -> Result<()> {
    match AuthSubcmds::from_arg_matches(matches)? {
        AuthSubcmds::Show(args) => handle_auth_show(&args),
    }
}

fn handle_auth_show(args: &ShowArgs) -> Result<()> {
    let bot = get_bot_info();

    if args.auth_status {
        return handle_auth_show_auth_status(bot);
    }

    handle_auth_show_default(bot)
}

fn handle_auth_show_default(bot: Option<Bot>) -> Result<()> {
    if let Some(bot) = bot {
        let view = serde_json::json!({
            "id": bot.id,
            "create_time": bot.create_time,
        });
        println!("{}", serde_json::to_string_pretty(&view)?);
    } else {
        println!("unauthorized");
    }
    Ok(())
}

fn handle_auth_show_auth_status(bot: Option<Bot>) -> Result<()> {
    if bot.is_some() {
        println!("authorized");
    } else {
        println!("unauthorized");
    }
    Ok(())
}
