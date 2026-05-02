#!/usr/bin/env bash
# dev-environment-setup probe: 输出系统级环境快照（JSON）
# 协议：见 ../references/probe-snapshot.md

set +e

# ── 工具检测 ─────────────────────────────
detect_tool() {
  local name="$1"
  local version_flag="${2:---version}"
  local path
  path=$(command -v "$name" 2>/dev/null)
  if [ -z "$path" ]; then
    printf '{"available":false}'
    return
  fi
  local version
  version=$("$name" $version_flag 2>&1 | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
  printf '{"available":true,"path":"%s","version":"%s"}' "$path" "${version:-}"
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

# ── DesireCore API 探测 ─────────────────
PORT_FILE="$HOME/.desirecore/agent-service.port"
DESIRECORE_API=""
PORT_FILE_EXISTS="false"
if [ -r "$PORT_FILE" ]; then
  PORT_FILE_EXISTS="true"
  PORT=$(cat "$PORT_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$PORT" ]; then
    if curl -sk --max-time 0.5 "https://127.0.0.1:${PORT}/api/runtime/environment" >/dev/null 2>&1; then
      DESIRECORE_API="https://127.0.0.1:${PORT}"
    fi
  fi
fi

# ── 工具检测结果 ────────────────────────
PY=$(detect_tool python3)
[ "$(echo "$PY" | grep -o false)" = "false" ] && PY=$(detect_tool python)
PIP=$(detect_tool pip3)
[ "$(echo "$PIP" | grep -o false)" = "false" ] && PIP=$(detect_tool pip)
NODE=$(detect_tool node)
NPM=$(detect_tool npm)
DOCKER=$(detect_tool docker)
PODMAN=$(detect_tool podman)
GIT=$(detect_tool git)

# ── 输出 JSON ───────────────────────────
cat <<EOF
{
  "platform": "${PLATFORM}",
  "arch": "${ARCH}",
  "desirecore_api": "${DESIRECORE_API}",
  "desirecore_port_file": ${PORT_FILE_EXISTS},
  "tools": {
    "python3": ${PY},
    "pip3": ${PIP},
    "node": ${NODE},
    "npm": ${NPM},
    "docker": ${DOCKER},
    "podman": ${PODMAN},
    "git": ${GIT}
  },
  "wsl": null
}
EOF
