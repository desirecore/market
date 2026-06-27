use std::collections::{HashMap, HashSet};
use std::path::Path;

use anyhow::{Context, Result};
use base64::Engine as _;
use serde_json::{Value, json};

use crate::json_rpc;

#[derive(Debug, Clone)]
pub enum DocIdentifier {
    DocId(String),
    Url(String),
}

/// 从参数中提取文档标识（`docid` 或 `url`）。
pub fn extract_doc_identifier(params: &Value) -> Result<DocIdentifier> {
    if let Some(docid) = params.get("docid").and_then(|v| v.as_str()) {
        if !docid.is_empty() {
            return Ok(DocIdentifier::DocId(docid.to_string()));
        }
    }
    if let Some(url) = params.get("url").and_then(|v| v.as_str()) {
        if !url.is_empty() {
            return Ok(DocIdentifier::Url(url.to_string()));
        }
    }
    anyhow::bail!("参数中缺少 docid 或 url（文档访问链接），上传图片时需要文档标识信息")
}

/// 扫描 records 并自动上传本地文件/图片，将路径替换为上传结果。
pub async fn process_records(records: &mut [Value], doc_id: &DocIdentifier) -> Result<()> {
    // 收集需要上传的本地路径
    let mut image_paths: HashSet<String> = HashSet::new();
    let mut file_paths: HashSet<String> = HashSet::new();

    for record in records.iter() {
        if let Some(values) = record.get("values").and_then(|v| v.as_object()) {
            for (_field, cell) in values {
                collect_upload_paths(cell, &mut image_paths, &mut file_paths);
            }
        }
    }

    // 上传图片
    let image_map = if !image_paths.is_empty() {
        upload_images(&image_paths.into_iter().collect::<Vec<_>>(), doc_id).await?
    } else {
        HashMap::new()
    };

    // 上传文件
    let file_map = if !file_paths.is_empty() {
        upload_files(&file_paths.into_iter().collect::<Vec<_>>()).await?
    } else {
        HashMap::new()
    };

    // 用上传结果替换本地路径
    for record in records.iter_mut() {
        if let Some(values) = record.get_mut("values").and_then(|v| v.as_object_mut()) {
            for (_field, cell) in values.iter_mut() {
                replace_upload_results(cell, &image_map, &file_map);
            }
        }
    }

    Ok(())
}

/// 获取 JSON 对象中指定字段的字符串值
fn get_str<'a>(item: &'a Value, key: &str) -> Option<&'a str> {
    item.get(key).and_then(|v| v.as_str())
}

/// 收集 cell 中需要上传的本地路径
fn collect_upload_paths(
    cell: &Value,
    image_paths: &mut HashSet<String>,
    file_paths: &mut HashSet<String>,
) {
    if let Value::Array(arr) = cell {
        for item in arr {
            if let Some(p) = get_str(item, "image_path") {
                image_paths.insert(p.to_string());
            }
            if let Some(p) = get_str(item, "file_path") {
                file_paths.insert(p.to_string());
            }
        }
    }
}

/// 用上传结果替换 cell 中的本地路径
fn replace_upload_results(
    cell: &mut Value,
    image_map: &HashMap<String, ImageUploadResult>,
    file_map: &HashMap<String, FileUploadResult>,
) {
    if let Value::Array(arr) = cell {
        for item in arr.iter_mut() {
            // 图片：用上传结果替换 image_path
            if let Some(p) = get_str(item, "image_path").map(String::from) {
                if let Some(result) = image_map.get(&p) {
                    if let Some(obj) = item.as_object_mut() {
                        obj.remove("image_path");
                        obj.insert("image_url".to_string(), Value::String(result.url.clone()));
                        if let Some(title) = &result.title {
                            obj.insert("title".to_string(), Value::String(title.clone()));
                        }
                    }
                }
            }

            // 附件：用上传结果替换 file_path
            if let Some(p) = get_str(item, "file_path").map(String::from) {
                if let Some(result) = file_map.get(&p) {
                    if let Some(obj) = item.as_object_mut() {
                        obj.remove("file_path");
                        obj.insert("file_id".to_string(), Value::String(result.fileid.clone()));
                    }
                }
            }
        }
    }
}

#[derive(Debug, Clone)]
struct ImageUploadResult {
    url: String,
    title: Option<String>,
}

#[derive(Debug, Clone)]
struct FileUploadResult {
    fileid: String,
}

/// 图片最大 30 MB
const MAX_IMAGE_SIZE: u64 = 30 * 1024 * 1024;
/// 文件最大 10 MB
const MAX_FILE_SIZE: u64 = 10 * 1024 * 1024;

/// 读取本地文件并编码为 base64，超过 `max_size` 时报错。
async fn read_file_as_base64(path: &str, max_size: u64) -> Result<String> {
    let data = tokio::fs::read(path)
        .await
        .with_context(|| format!("读取文件失败: {}", path))?;
    let size = data.len() as u64;
    if size > max_size {
        anyhow::bail!(
            "文件 {} 大小为 {:.1} MB，超过限制 {:.1} MB",
            path,
            size as f64 / 1024.0 / 1024.0,
            max_size as f64 / 1024.0 / 1024.0,
        );
    }
    Ok(base64::engine::general_purpose::STANDARD.encode(&data))
}

/// 批量上传图片，返回 path → ImageUploadResult 映射。
async fn upload_images(
    paths: &[String],
    doc_id: &DocIdentifier,
) -> Result<HashMap<String, ImageUploadResult>> {
    eprintln!("正在上传 {} 张图片...", paths.len());

    let mut map = HashMap::new();

    for path in paths {
        let base64_content = read_file_as_base64(path, MAX_IMAGE_SIZE).await?;

        // 构造请求参数
        let mut args = json!({ "base64_content": base64_content });
        match doc_id {
            DocIdentifier::DocId(id) => {
                args["docid"] = Value::String(id.clone());
            }
            DocIdentifier::Url(url) => {
                args["url"] = Value::String(url.clone());
            }
        }

        let res = json_rpc::call_json_tool("doc", "upload_doc_image", args)
            .await
            .with_context(|| format!("上传图片失败: {}", path))?;

        let url = res
            .get("url")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();

        if url.is_empty() {
            anyhow::bail!("图片 {} 上传失败：返回结果中缺少 url", path);
        }

        // 文件名作为 title
        let title = Path::new(path)
            .file_name()
            .and_then(|n| n.to_str())
            .map(String::from);

        map.insert(path.clone(), ImageUploadResult { url, title });
    }

    eprintln!("图片上传完成，成功 {} 张", map.len());
    Ok(map)
}

/// 批量上传文件，返回 path → FileUploadResult 映射。
async fn upload_files(paths: &[String]) -> Result<HashMap<String, FileUploadResult>> {
    eprintln!("正在上传 {} 个文件...", paths.len());

    let mut map = HashMap::new();

    for path in paths {
        let file_base64_content = read_file_as_base64(path, MAX_FILE_SIZE).await?;

        // 提取文件名
        let file_name = Path::new(path)
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown")
            .to_string();

        let args = json!({
            "file_name": file_name,
            "file_base64_content": file_base64_content,
        });

        let res = json_rpc::call_json_tool("doc", "upload_doc_file", args)
            .await
            .with_context(|| format!("上传文件失败: {}", path))?;

        let fileid = res
            .get("fileid")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();

        if fileid.is_empty() {
            anyhow::bail!("文件 {} 上传失败：返回结果中缺少 fileid", path);
        }

        map.insert(path.clone(), FileUploadResult { fileid });
    }

    eprintln!("文件上传完成，成功 {} 个", map.len());
    Ok(map)
}

/// 获取远程工具 schema，并新增 `image_path` / `file_path` 字段。
pub async fn get_modified_schema(remote_method: &str) -> Result<Value> {
    let tools = crate::registry::get_category_tools("doc").await?;
    let tool = tools
        .iter()
        .find(|t| t.name == remote_method)
        .ok_or_else(|| anyhow::anyhow!("远程工具不存在: {}", remote_method))?;

    let mut schema = serde_json::to_value(tool)?;

    replace_image_value_schema(&mut schema);
    replace_attachment_value_schema(&mut schema);

    Ok(schema)
}

/// 替换 schema 中的 CellImageValue 定义，只保留 image_path 字段。
fn replace_image_value_schema(schema: &mut Value) {
    if let Some(defs) = schema
        .pointer_mut("/inputSchema/$defs")
        .and_then(|d| d.as_object_mut())
    {
        defs.insert(
            "CellImageValue".to_string(),
            json!({
                "description": "图片类型字段的单元值。只需传入本地图片路径，系统自动上传。",
                "properties": {
                    "image_path": {
                        "description": "本地图片文件路径。传入本地图片路径（如 /path/to/image.png 或 ./photo.jpg），系统会自动上传到文档服务器。",
                        "title": "Image Path",
                        "type": "string"
                    }
                },
                "required": ["image_path"],
                "title": "CellImageValue",
                "type": "object"
            }),
        );
    }
}

/// 替换 schema 中的 CellAttachmentValue 定义，只保留 file_path 字段。
fn replace_attachment_value_schema(schema: &mut Value) {
    if let Some(defs) = schema
        .pointer_mut("/inputSchema/$defs")
        .and_then(|d| d.as_object_mut())
    {
        defs.insert(
            "CellAttachmentValue".to_string(),
            json!({
                "description": "附件类型字段的单元值。只需传入本地文件路径，系统自动上传。",
                "properties": {
                    "file_path": {
                        "description": "传入本地文件路径，系统会自动上传到文档服务器。",
                        "title": "File Path",
                        "type": "string"
                    }
                },
                "required": ["file_path"],
                "title": "CellAttachmentValue",
                "type": "object"
            }),
        );
    }
}
