#!/usr/bin/env bash
# nodejs-runtime probe: 输出 Node.js 环境快照（JSON）
# 协议：见 ../../dev-environment-setup/references/probe-snapshot.md

set +e

detect_tool() {
  local name="$1"
  local path
  path=$(command -v "$name" 2>/dev/null)
  if [ -z "$path" ]; then
    printf '{"path":"","version":""}'
    return
  fi
  local version
  version=$("$name" --version 2>&1 | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
  printf '{"path":"%s","version":"%s"}' "$path" "${version:-}"
}

# ── 平台 ────────────────────────────────
case "$(uname -s)" in
  Darwin) PLATFORM="darwin" ;;
  Linux)  PLATFORM="linux"  ;;
  *)      PLATFORM="other"  ;;
esac
ARCH=$(uname -m)
case "$ARCH" in
  arm64|aarch64) ARCH="arm64" ;;
  x86_64|amd64)  ARCH="x64"   ;;
esac

# ── DesireCore API ──────────────────────
DESIRECORE_API=""
PORT_FILE="${DESIRECORE_ROOT}/agent-service.port"
if [ -r "$PORT_FILE" ]; then
  PORT=$(cat "$PORT_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$PORT" ]; then
    if curl -sk --max-time 0.5 "https://127.0.0.1:${PORT}/api/runtime/environment" >/dev/null 2>&1; then
      DESIRECORE_API="https://127.0.0.1:${PORT}"
    fi
  fi
fi

# ── 系统 Node / npm ─────────────────────
SYS_NODE=$(detect_tool node)
SYS_NPM=$(detect_tool npm)

# ── DesireCore Volta ────────────────────
VOLTA_BIN="${DESIRECORE_ROOT}/runtime/volta/volta"
VOLTA_PATH=""
VOLTA_VERSION=""
if [ -x "$VOLTA_BIN" ]; then
  VOLTA_PATH="$VOLTA_BIN"
  VOLTA_VERSION=$("$VOLTA_BIN" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
fi

# Volta 已装工具（直接读 image 目录最稳）
VOLTA_IMG="${DESIRECORE_ROOT}/runtime/volta/tools/image"
list_dir() {
  local dir="$1"
  if [ -d "$dir" ]; then
    local items
    items=$(ls -1 "$dir" 2>/dev/null | sort -V | tr '\n' ',' | sed 's/,$//')
    if [ -n "$items" ]; then
      echo "[\"$(echo "$items" | sed 's/,/","/g')\"]"
      return
    fi
  fi
  echo "[]"
}
NODE_VERSIONS=$(list_dir "$VOLTA_IMG/node")
PNPM_VERSIONS=$(list_dir "$VOLTA_IMG/pnpm")
YARN_VERSIONS=$(list_dir "$VOLTA_IMG/yarn")
NPM_VERSIONS=$(list_dir "$VOLTA_IMG/npm")

# ── package.json#volta ──────────────────
PKG_VOLTA="null"
if [ -f "package.json" ]; then
  PKG_VOLTA=$(python3 -c "import json,sys; d=json.load(open('package.json')); print(json.dumps(d.get('volta')))" 2>/dev/null || echo "null")
  [ -z "$PKG_VOLTA" ] && PKG_VOLTA="null"
fi

# ── 社区方案 ────────────────────────────
NVM_PATH=""
[ -s "$HOME/.nvm/nvm.sh" ] && NVM_PATH="$HOME/.nvm/nvm.sh"
FNM_PATH=$(command -v fnm 2>/dev/null)

# ── npm config ──────────────────────────
REGISTRY=""
PROXY=""
if command -v npm >/dev/null 2>&1; then
  REGISTRY=$(npm config get registry 2>/dev/null | tr -d '\r\n')
  PROXY=$(npm config get https-proxy 2>/dev/null | tr -d '\r\n')
  [ "$PROXY" = "null" ] && PROXY=""
fi

# ── 输出 JSON ───────────────────────────
cat <<EOF
{
  "platform": "${PLATFORM}",
  "arch": "${ARCH}",
  "desirecore_api": "${DESIRECORE_API}",
  "system_node": ${SYS_NODE},
  "system_npm": ${SYS_NPM},
  "volta_path": "${VOLTA_PATH}",
  "volta_version": "${VOLTA_VERSION}",
  "volta_tools": {
    "node": ${NODE_VERSIONS},
    "pnpm": ${PNPM_VERSIONS},
    "yarn": ${YARN_VERSIONS},
    "npm": ${NPM_VERSIONS}
  },
  "package_json_volta": ${PKG_VOLTA},
  "nvm_path": "${NVM_PATH}",
  "fnm_path": "${FNM_PATH:-}",
  "registry": "${REGISTRY}",
  "proxy": "${PROXY}"
}
EOF
