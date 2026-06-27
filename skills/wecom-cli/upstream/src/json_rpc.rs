use anyhow::Result;
use serde::Serialize;

use crate::{constants, mcp};

#[derive(Debug)]
pub enum JsonRpcError {
    /// 通用 RPC 失败（无 result、isError=true 等）
    RpcError(serde_json::Value),
    /// JSON-RPC 协议层错误（error.code ≠ 0）
    ApiError {
        code: i64,
        payload: serde_json::Value,
    },
    /// 业务逻辑错误（errcode ≠ 0）
    BusinessError {
        errcode: i64,
        payload: serde_json::Value,
    },
    /// 响应格式不符合预期
    MalformedResponse(serde_json::Value),
}

impl std::fmt::Display for JsonRpcError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            JsonRpcError::RpcError(res) => write!(f, "请求失败：{res}"),
            JsonRpcError::ApiError { code, payload } => {
                write!(f, "接口错误 (code={code})：{payload}")
            }
            JsonRpcError::BusinessError { errcode, payload } => {
                write!(f, "业务错误 (errcode={errcode})：{payload}")
            }
            JsonRpcError::MalformedResponse(raw) => {
                write!(f, "响应格式异常：{raw}")
            }
        }
    }
}

impl std::error::Error for JsonRpcError {}

#[derive(Debug, Clone, Serialize)]
struct JsonRpcRequest {
    jsonrpc: &'static str,
    id: String,
    method: String,
    params: Option<serde_json::Value>,
}

pub async fn call_json_tool(
    category: &str,
    method: &str,
    args: serde_json::Value,
) -> Result<serde_json::Value> {
    let res = call_tool(category, method, args).await?;

    let malformed = || -> anyhow::Error { JsonRpcError::MalformedResponse(res.clone()).into() };

    let content = res
        .pointer("/result/content")
        .and_then(|c| c.as_array())
        .filter(|arr| arr.len() == 1)
        .ok_or_else(malformed)?;

    let item = &content[0];
    if item.get("type").and_then(|t| t.as_str()) != Some("text") {
        return Err(malformed());
    }
    let text = item
        .get("text")
        .and_then(|t| t.as_str())
        .ok_or_else(malformed)?;

    let parsed: serde_json::Value = serde_json::from_str(text).map_err(|_| malformed())?;

    // 3. errcode 必须为 0 或不存在
    if let Some(errcode) = parsed.get("errcode").and_then(|c| c.as_i64()) {
        if errcode != 0 {
            return Err(JsonRpcError::BusinessError {
                errcode,
                payload: parsed,
            }
            .into());
        }
    }

    Ok(parsed)
}

pub async fn call_tool(
    category: &str,
    method: &str,
    args: serde_json::Value,
) -> Result<serde_json::Value> {
    let timeout_ms = if method == "get_msg_media" {
        Some(120000)
    } else {
        None
    };
    let params = serde_json::json!({
        "name": method,
        "arguments": args,
    });
    let response = send(category, "tools/call", Some(params), timeout_ms).await?;

    let Some(result) = response.get("result") else {
        return Err(JsonRpcError::MalformedResponse(response).into());
    };

    if result.get("isError").and_then(|r| r.as_bool()) == Some(true) {
        return Err(JsonRpcError::RpcError(response).into());
    }

    Ok(response)
}

/// Send a JSON-RPC 2.0 request to the MCP endpoint for the given category and method.
pub async fn send(
    category: &str,
    method: &str,
    params: Option<serde_json::Value>,
    timeout_ms: Option<i32>,
) -> Result<serde_json::Value> {
    let mcp_url = mcp::get_mcp_url(category).await?;

    let body = JsonRpcRequest {
        jsonrpc: "2.0",
        id: mcp::gen_req_id("mcp_rpc"),
        method: method.to_string(),
        params,
    };

    let timeout = std::time::Duration::from_millis(timeout_ms.unwrap_or(30000) as u64);

    let request = reqwest::Client::builder()
        .build()?
        .post(&mcp_url)
        .timeout(timeout)
        .header("Accept", "application/json")
        .header("User-Agent", constants::get_user_agent())
        .json(&body);

    let response = request.send().await.map_err(|err| {
        if err.is_timeout() {
            anyhow::anyhow!("MCP请求超时 ({}ms)", timeout.as_millis())
        } else {
            anyhow::anyhow!("MCP网络请求失败: {err}")
        }
    })?;

    let status = response.status();

    if !status.is_success() {
        anyhow::bail!("MCP请求失败 (HTTP {status})");
    }

    let body_text = response.text().await?;
    let res = serde_json::from_str::<serde_json::Value>(&body_text)?;

    if let Some(code) = res.pointer("/error/code").and_then(|c| c.as_i64()) {
        if code != 0 {
            return Err(JsonRpcError::ApiError { code, payload: res }.into());
        }
    }

    Ok(res)
}
