use std::future::Future;
use std::pin::Pin;

use crate::{helpers::registry::Helper, json_rpc};
use anyhow::{Context, Result};
use clap::{ArgMatches, Args, Command, FromArgMatches};
use serde_json::{Value, json};

/// 创建智能文档（自动读取本地文件版本）
///
/// 与远程 smartpage_create 相同，但 pages 中的 page_content 改为 page_filepath，
/// 执行时自动以 UTF-8 编码读取本地文件内容，填入 page_content 字段后调用后台接口。
#[derive(Args, Debug)]
pub struct SmartpageCreateArgs {
    /// JSON 格式的参数（与远程 smartpage_create 相同，但 page_content 改为 page_filepath）
    #[arg(hide = true, value_name = "args")]
    pub args: Option<String>,

    /// JSON 格式的参数
    #[arg(long)]
    pub json: Option<String>,

    /// 输出该命令的参数 schema
    #[arg(long, action = clap::ArgAction::SetTrue)]
    pub schema: bool,
}

pub struct SmartpageCreateHelper;

impl SmartpageCreateHelper {
    /// 获取修改后的 schema：将 pages.items.properties 中的 page_content 替换为 page_filepath
    async fn get_modified_schema() -> Result<Value> {
        let tools = crate::registry::get_category_tools("doc").await?;
        let tool = tools
            .iter()
            .find(|t| t.name == "smartpage_create")
            .ok_or_else(|| anyhow::anyhow!("远程工具不存在: smartpage_create"))?;

        let mut schema = serde_json::to_value(tool)?;

        // 修改 schema：将 pages.items.properties 中的 page_content 替换为 page_filepath
        if let Some(props) = schema
            .pointer_mut("/inputSchema/properties/pages/items/properties")
            .and_then(|v| v.as_object_mut())
        {
            props.remove("page_content");
            props.insert(
                "page_filepath".to_string(),
                json!({
                    "description": "本地文件路径，以 UTF-8 编码读取文件内容作为子页面内容",
                    "type": "string"
                }),
            );
        }

        Ok(schema)
    }

    /// 处理 pages 数组：将 page_filepath 替换为 page_content（读取本地文件内容）
    async fn process_pages(pages: &mut [Value]) -> Result<()> {
        for (i, page) in pages.iter_mut().enumerate() {
            let obj = page
                .as_object_mut()
                .ok_or_else(|| anyhow::anyhow!("pages[{}] 不是一个对象", i))?;

            // 如果存在 page_filepath，读取文件内容并替换为 page_content
            if let Some(filepath_val) = obj.remove("page_filepath") {
                let filepath = filepath_val
                    .as_str()
                    .ok_or_else(|| anyhow::anyhow!("pages[{}].page_filepath 必须是字符串", i))?;

                let content = tokio::fs::read_to_string(filepath)
                    .await
                    .with_context(|| format!("读取文件失败: {}", filepath))?;

                obj.insert("page_content".to_string(), Value::String(content));
            }
        }

        Ok(())
    }
}

impl Helper for SmartpageCreateHelper {
    fn category(&self) -> &'static str {
        "doc"
    }

    fn command(&self) -> clap::Command {
        SmartpageCreateArgs::augment_args(
            Command::new("+smartpage_create")
                .about("创建智能主页，支持通过 page_filepath 自动读取本地文件内容作为子页面内容"),
        )
    }

    fn execute<'a>(
        &'a self,
        matches: &'a ArgMatches,
    ) -> Pin<Box<dyn Future<Output = Result<()>> + Send + 'a>> {
        Box::pin(async {
            let args = SmartpageCreateArgs::from_arg_matches(matches)?;

            // 输出修改后的 schema
            if args.schema {
                let schema = Self::get_modified_schema().await?;
                println!("{}", serde_json::to_string_pretty(&schema)?);
                return Ok(());
            }

            // 解析 JSON 参数
            let raw = args
                .json
                .as_deref()
                .or(args.args.as_deref())
                .ok_or_else(|| anyhow::anyhow!("请提供 JSON 格式的参数"))?;
            let mut params: Value = serde_json::from_str(raw).context("JSON 参数解析失败")?;

            // 提取并处理 pages 数组
            let pages = params
                .get_mut("pages")
                .and_then(|v| v.as_array_mut())
                .ok_or_else(|| anyhow::anyhow!("参数中缺少 pages 数组"))?;

            // 读取本地文件，将 page_filepath 替换为 page_content
            Self::process_pages(pages).await?;

            // 调用后台接口 smartpage_create
            let res = json_rpc::call_tool("doc", "smartpage_create", params).await?;
            println!("{res}");

            Ok(())
        })
    }
}
