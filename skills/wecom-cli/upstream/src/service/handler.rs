use crate::{helpers::HelperRegistry, json_rpc, media, registry, service::command::MethodCmdArgs};

use anyhow::Result;
use clap::{ArgMatches, FromArgMatches};
use serde_json::json;

/// Handle the `call` subcommand: dispatch a JSON-RPC tool invocation for a given category and method.
pub async fn handle_service_cmd(
    helper_registry: &HelperRegistry,
    category_name: &str,
    matches: &ArgMatches,
) -> Result<()> {
    let Some((method_name, matches)) = matches.subcommand() else {
        return Ok(());
    };

    if let Some(helper) = helper_registry.get(category_name, method_name) {
        return helper.execute(matches).await;
    }

    let args = MethodCmdArgs::from_arg_matches(matches)?;

    if args.schema {
        let tools = registry::get_category_tools(category_name).await?;
        let Some(tool) = tools.iter().find(|t| t.name == method_name) else {
            anyhow::bail!("工具不存在: {}", method_name);
        };
        println!("{}", serde_json::to_string_pretty(tool)?);
        return Ok(());
    }

    // 优先使用 --json，其次位置参数 args，都没有则默认空对象
    let json_args = if let Some(raw) = args.json.as_deref().or(args.args.as_deref()) {
        serde_json::from_str(raw)?
    } else {
        json!({})
    };

    let mut res = json_rpc::call_tool(category_name, method_name, json_args).await?;

    if method_name == "get_msg_media" {
        res = media::intercept_media_response(res).await?;
    }

    println!("{res}");
    Ok(())
}
