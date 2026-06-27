mod utils;

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};

const INBOUND_MAX_BYTES: usize = 20 * 1024 * 1024;

/// Intercept a `get_msg_media` response: decode base64 payload, save to disk, and replace the response with a local file reference.
pub async fn intercept_media_response(res: Value) -> Result<Value> {
    let Some(result) = res.get("result") else {
        return Ok(res);
    };

    // 1. Extract the content array from the MCP result
    let Some(content) = result.get("content").and_then(|c| c.as_array()) else {
        return Ok(res);
    };

    // Find the entry where type="text" and text is a string
    let text_item = content.iter().find(|c| {
        c.get("type").and_then(|t| t.as_str()) == Some("text")
            && c.get("text").and_then(|t| t.as_str()).is_some()
    });
    let Some(text_item) = text_item else {
        return Ok(res);
    };
    let text = text_item["text"].as_str().unwrap();

    // 2. Parse the business JSON
    let biz_data: Value = match serde_json::from_str(text) {
        Ok(v) => v,
        Err(_) => return Ok(res), // Not JSON format, return as-is
    };

    // 3. Validate business response: return as-is when errcode !== 0 or no media_item
    if biz_data.get("errcode").and_then(|c| c.as_i64()) != Some(0) {
        return Ok(res);
    }

    let Some(media_item) = biz_data.get("media_item") else {
        return Ok(res);
    };

    let Some(base64_data) = media_item.get("base64_data").and_then(|d| d.as_str()) else {
        return Ok(res);
    };

    let media_name = media_item.get("name").and_then(|n| n.as_str());
    let media_type = media_item.get("type").and_then(|t| t.as_str());
    let media_id = media_item.get("media_id").and_then(|i| i.as_str());

    // 4. Decode base64 → buffer
    use base64::Engine as _;
    let buffer = base64::engine::general_purpose::STANDARD
        .decode(base64_data)
        .context("base64解码失败")?;

    // Validate size
    if buffer.len() > INBOUND_MAX_BYTES {
        bail!(
            "媒体文件过大: {} 字节 (最大 {} 字节)",
            buffer.len(),
            INBOUND_MAX_BYTES
        );
    }

    // 5. Detect MIME type
    let content_type = utils::detect_mime(media_name, &buffer);

    // 6. Save to local file
    let file_path = utils::save_media(media_name, media_id, &content_type, &buffer).await?;

    // 7. Build a concise response: remove base64_data, add local path
    let new_biz_data = json!({
        "errcode": 0,
        "errmsg": "ok",
        "media_item": {
            "media_id": media_id,
            "name": media_name.unwrap_or_else(|| file_path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("unknown")),
            "type": media_type,
            "local_path": file_path.to_string_lossy(),
            "size": buffer.len(),
            "content_type": content_type,
        },
    });

    // 8. Replace res in-place with the modified MCP result structure
    Ok(json!({
        "result": {
            "content": [{
                "type": "text",
                "text": serde_json::to_string(&new_biz_data)?,
            }],
        },
    }))
}
