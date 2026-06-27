use clap::{Args, Command};

use crate::{helpers::HelperRegistry, registry::ServiceTool};

use super::categories::CategoryInfo;

#[derive(Args, Debug)]
pub struct MethodCmdArgs {
    /// JSON 格式的参数
    #[arg(hide = true, value_name = "args")]
    pub args: Option<String>,

    /// JSON 格式的参数
    #[arg(long)]
    pub json: Option<String>,

    /// 输出 method schema
    #[arg(long, action = clap::ArgAction::SetTrue)]
    pub schema: bool,
}

pub fn build_service_cmd(
    helper_registry: &HelperRegistry,
    category: &CategoryInfo,
    tools: Option<&Vec<ServiceTool>>,
) -> Command {
    let mut cmd = Command::new(category.name)
        .about(category.description)
        .arg_required_else_help(true)
        .disable_help_flag(true);

    for helper in helper_registry.list_in_category(category.name) {
        cmd = cmd.subcommand(helper.command().disable_help_flag(true));
    }

    if let Some(tools) = tools {
        for tool in tools {
            let mut tool_cmd = MethodCmdArgs::augment_args(
                Command::new(tool.name.clone()).disable_help_flag(true),
            );
            if let Some(desc) = &tool.description {
                tool_cmd = tool_cmd.about(desc.clone());
            }
            cmd = cmd.subcommand(tool_cmd);
        }
    }

    cmd
}
