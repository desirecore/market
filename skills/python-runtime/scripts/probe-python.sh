#!/usr/bin/env bash
# python-runtime probe: 输出 Python 环境快照（JSON）
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
PORT_FILE="$HOME/.desirecore/agent-service.port"
if [ -r "$PORT_FILE" ]; then
  PORT=$(cat "$PORT_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$PORT" ]; then
    if curl -sk --max-time 0.5 "https://127.0.0.1:${PORT}/api/runtime/environment" >/dev/null 2>&1; then
      DESIRECORE_API="https://127.0.0.1:${PORT}"
    fi
  fi
fi

# ── 系统 Python / pip ───────────────────
SYS_PY=$(detect_tool python3)
[ "$(echo "$SYS_PY" | grep -c '"path":""')" = "1" ] && SYS_PY=$(detect_tool python)
SYS_PIP=$(detect_tool pip3)
[ "$(echo "$SYS_PIP" | grep -c '"path":""')" = "1" ] && SYS_PIP=$(detect_tool pip)

# ── DesireCore Hatch ────────────────────
HATCH_BIN="$HOME/.desirecore/runtime/hatch/hatch"
HATCH_PATH=""
HATCH_VERSION=""
if [ -x "$HATCH_BIN" ]; then
  HATCH_PATH="$HATCH_BIN"
  HATCH_VERSION=$("$HATCH_BIN" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
fi

# Hatch 已安装的 Python 版本（直接读 local/ 目录，避免依赖 hatch 命令）
HATCH_LOCAL="$HOME/.desirecore/runtime/hatch/local"
HATCH_VERSIONS="[]"
if [ -d "$HATCH_LOCAL" ]; then
  versions=$(ls -1 "$HATCH_LOCAL" 2>/dev/null | sort -V | tr '\n' ',' | sed 's/,$//')
  if [ -n "$versions" ]; then
    HATCH_VERSIONS="[\"$(echo "$versions" | sed 's/,/","/g')\"]"
  fi
fi

# ── 虚拟环境 ────────────────────────────
ACTIVE_VENV="${VIRTUAL_ENV:-}"

# ── PEP 668 ────────────────────────────
PEP668="false"
for marker in /usr/lib/python*/EXTERNALLY-MANAGED /usr/lib/python3/EXTERNALLY-MANAGED /usr/lib/python3*/EXTERNALLY-MANAGED; do
  if [ -e "$marker" ]; then
    PEP668="true"
    break
  fi
done

# ── 社区方案 ────────────────────────────
PYENV_PATH=$(command -v pyenv 2>/dev/null)
[ -z "$PYENV_PATH" ] && [ -d "$HOME/.pyenv/bin" ] && PYENV_PATH="$HOME/.pyenv/bin/pyenv"
CONDA_PATH=$(command -v conda 2>/dev/null)
[ -z "$CONDA_PATH" ] && [ -x "$HOME/miniconda3/bin/conda" ] && CONDA_PATH="$HOME/miniconda3/bin/conda"

# ── 输出 JSON ───────────────────────────
cat <<EOF
{
  "platform": "${PLATFORM}",
  "arch": "${ARCH}",
  "desirecore_api": "${DESIRECORE_API}",
  "system_python": ${SYS_PY},
  "system_pip": ${SYS_PIP},
  "hatch_path": "${HATCH_PATH}",
  "hatch_version": "${HATCH_VERSION}",
  "hatch_versions": ${HATCH_VERSIONS},
  "active_venv": "${ACTIVE_VENV}",
  "pep668": ${PEP668},
  "pyenv_path": "${PYENV_PATH:-}",
  "conda_path": "${CONDA_PATH:-}"
}
EOF
