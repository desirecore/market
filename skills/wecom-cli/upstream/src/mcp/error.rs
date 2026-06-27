use super::config::GetMcpConfigResponse;

/// Errors returned by `fetch_mcp_config` / `get_mcp_config`.
#[derive(Debug)]
pub enum FetchMcpConfigError {
    /// Business-level failure: the server responded, but `errcode != 0`.
    Api(GetMcpConfigResponse),
    /// Http-level failure: the server returned a non-200 status.
    Http(GetMcpConfigHttpError),
    /// Everything else (network, deserialization, I/O …).
    Other(anyhow::Error),
}

#[derive(Debug)]
pub struct GetMcpConfigHttpError {
    pub status: u16,
    pub body: String,
}

impl std::fmt::Display for FetchMcpConfigError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Api(resp) => write!(
                f,
                "获取 MCP 配置失败：[{}] {}",
                resp.errcode,
                resp.errmsg.as_deref().unwrap_or("unknown")
            ),
            Self::Http(e) => write!(f, "获取 MCP 配置失败：HTTP {}: {}", e.status, e.body),
            Self::Other(e) => write!(f, "{e}"),
        }
    }
}

impl std::error::Error for FetchMcpConfigError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Api(_) => None,
            Self::Http(_) => None,
            Self::Other(e) => Some(e.as_ref()),
        }
    }
}

impl From<anyhow::Error> for FetchMcpConfigError {
    fn from(e: anyhow::Error) -> Self {
        Self::Other(e)
    }
}
