use std::future::Future;
use std::pin::Pin;

use crate::{helpers::registry::Helper, json_rpc};
use anyhow::{Context, Result};
use clap::{ArgMatches, Args, Command, FromArgMatches};

use super::auto_file_upload;

/// 添加智能表格记录，支持通过 image_path/file_path 自动上传本地文件
#[derive(Args, Debug)]
pub struct SmartsheetAddRecordsAutoFileArgs {
    /// JSON 格式的参数（与 smartsheet_add_records 相同，但图片/附件字段可传本地文件路径）
    #[arg(hide = true, value_name = "args")]
    pub args: Option<String>,

    /// JSON 格式的参数
    #[arg(long)]
    pub json: Option<String>,

    /// 输出该命令的参数 schema
    #[arg(long, action = clap::ArgAction::SetTrue)]
    pub schema: bool,
}

pub struct SmartsheetAddRecordsAutoFileHelper;

impl Helper for SmartsheetAddRecordsAutoFileHelper {
    fn category(&self) -> &'static str {
        "doc"
    }

    fn command(&self) -> clap::Command {
        SmartsheetAddRecordsAutoFileArgs::augment_args(Command::new(
            "+smartsheet_add_records_auto_file",
        ))
    }

    fn execute<'a>(
        &'a self,
        matches: &'a ArgMatches,
    ) -> Pin<Box<dyn Future<Output = Result<()>> + Send + 'a>> {
        Box::pin(async {
            let args = SmartsheetAddRecordsAutoFileArgs::from_arg_matches(matches)?;

            if args.schema {
                let schema =
                    auto_file_upload::get_modified_schema("smartsheet_add_records").await?;
                println!("{}", serde_json::to_string_pretty(&schema)?);
                return Ok(());
            }

            let raw = args
                .json
                .as_deref()
                .or(args.args.as_deref())
                .ok_or_else(|| anyhow::anyhow!("请提供 JSON 格式的参数"))?;
            let mut params: serde_json::Value =
                serde_json::from_str(raw).context("JSON 参数解析失败")?;

            // 提取文档标识（docid 或 url），用于图片上传
            let doc_id = auto_file_upload::extract_doc_identifier(&params)?;

            // 提取并处理 records
            let records = params
                .get_mut("records")
                .and_then(|v| v.as_array_mut())
                .ok_or_else(|| anyhow::anyhow!("参数中缺少 records 数组"))?;

            // 扫描并上传本地文件/图片，替换路径
            auto_file_upload::process_records(records, &doc_id).await?;

            // 调用后台接口 smartsheet_add_records
            let res = json_rpc::call_tool("doc", "smartsheet_add_records", params).await?;
            println!("{res}");

            Ok(())
        })
    }
}
