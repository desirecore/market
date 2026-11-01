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
PORT_FILE="${DESIRECORE_ROOT}/agent-service.port"
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
HATCH_DIR="${DESIRECORE_ROOT}/runtime/hatch"
HATCH_TARGET="${PLATFORM}-${ARCH}"

# 二进制与服务同序：手动下载的 runtime/hatch/hatch 优先，其次随包工具链。
# 桌面版的应用目录不在环境变量里，随包路径再看 Volta 入口的链接目标（只读链接，不执行入口；
# Volta 建入口时指向同一工具链目录下的 volta-shim，旧版升级后可能已断）和默认安装位置。
VOLTA_SHIM=$(readlink "${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}/bin/node" 2>/dev/null)
HATCH_PATH=""
for HATCH_BIN in \
  "${HATCH_DIR}/hatch" \
  "${DESIRECORE_STATIC_DIR}/toolchains/${HATCH_TARGET}/hatch/hatch" \
  "${VOLTA_SHIM%/volta/*}/hatch/hatch" \
  /Applications/*.app/Contents/static/toolchains/"${HATCH_TARGET}"/hatch/hatch \
  /opt/*/static/toolchains/"${HATCH_TARGET}"/hatch/hatch
do
  if [ -f "$HATCH_BIN" ] && [ -x "$HATCH_BIN" ]; then
    HATCH_PATH="$HATCH_BIN"
    break
  fi
done

# 客户端解包好的 Hatch 分发（10.0.183 起），调用二进制时经 PYAPP_INSTALL_DIR_HATCH 传入
HATCH_BOOTSTRAP=""
for BOOTSTRAP_DIR in "${HATCH_DIR}/bootstrap/"*-"${HATCH_TARGET}"; do
  [ -f "${BOOTSTRAP_DIR}/.ready" ] && HATCH_BOOTSTRAP="$BOOTSTRAP_DIR"
done

# 随包 Hatch 是 PyApp 引导程序：没有解包好的分发时，连 --version 都会下载分发并解压到用户目录。
# 这时不执行二进制，版本读它旁边的 asset.json
HATCH_VERSION=""
if [ -n "$HATCH_PATH" ] && [ -n "$HATCH_BOOTSTRAP" ]; then
  HATCH_VERSION=$(PYAPP_INSTALL_DIR_HATCH="$HATCH_BOOTSTRAP" "$HATCH_PATH" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
elif [ -n "$HATCH_PATH" ]; then
  HATCH_VERSION=$(grep -m1 '"version"' "${HATCH_PATH%/*}/asset.json" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
fi

# Hatch 已安装的 Python 版本（直接读 local/ 目录，避免依赖 hatch 命令）
HATCH_LOCAL="${HATCH_DIR}/local"
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
  "hatch_bootstrap": "${HATCH_BOOTSTRAP}",
  "hatch_versions": ${HATCH_VERSIONS},
  "active_venv": "${ACTIVE_VENV}",
  "pep668": ${PEP668},
  "pyenv_path": "${PYENV_PATH:-}",
  "conda_path": "${CONDA_PATH:-}"
}
EOF
