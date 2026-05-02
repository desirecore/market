# Node.js 故障排查

## "node: command not found" / "npm: command not found"

```bash
# 1. 找一下二进制
which node 2>/dev/null
ls /usr/bin/node /usr/local/bin/node /opt/homebrew/bin/node 2>/dev/null

# 2. nvm 已装但未加载？
[ -s "$HOME/.nvm/nvm.sh" ] && echo "nvm installed but not loaded"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node --version

# 3. Volta 已装但未在 PATH？
ls ~/.desirecore/runtime/volta/volta 2>/dev/null && \
  echo "运行 ~/.desirecore/runtime/volta/volta 直接调用，无需 PATH"
```

**根治**：按主 SKILL.md 决策树重新执行 L1–L3 安装路径。

## npm EACCES（全局安装权限错误）

**症状**：`npm install -g <pkg>` 报 `EACCES: permission denied, mkdir '/usr/local/lib/node_modules'`。

**原因**：npm 默认全局目录是系统目录，无写权限。

**修复（推荐：改 npm prefix 到用户目录）**

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc   # 或 ~/.bashrc
source ~/.zshrc

# 现在可以正常全局安装
npm install -g pkg
```

**禁忌**：`sudo npm install -g` ——会把文件 owner 改成 root，后续 npm 升级/卸载报错。

## node-gyp 编译失败

**症状**：安装包含原生扩展的依赖（sqlite3 / sharp / canvas）时报 `node-gyp rebuild failed`。

| 平台 | 修复 |
|------|------|
| macOS | `xcode-select --install` |
| Ubuntu/Debian | `sudo apt install build-essential python3` |
| Fedora/RHEL | `sudo dnf groupinstall "Development Tools" && sudo dnf install python3` |
| Windows | `npm install --global windows-build-tools`（管理员）或装 Visual Studio Build Tools |

某些包提供预编译版本：检查 `package.json` 是否有 `prebuild-install` 钩子，没有再编译。

## SSL / TLS 错误

```bash
# 临时不验证（仅调试）
npm config set strict-ssl false

# 永久（不推荐）
npm config set ca null

# 公司证书 / Zscaler
npm config set cafile /path/to/company-ca.pem
```

## 代理环境

```bash
# 设置
npm config set proxy http://proxy:port
npm config set https-proxy http://proxy:port

# 检查
npm config get proxy
npm config get https-proxy

# 取消
npm config delete proxy
npm config delete https-proxy
```

注意：HTTP_PROXY / HTTPS_PROXY 环境变量也会被 npm 识别。

## "Cannot find module" 错误

```bash
# 1. 是否在正确目录
pwd
ls package.json

# 2. node_modules 是否安装
ls node_modules/<missing-module> 2>/dev/null

# 3. 是否在虚拟切换中（nvm/Volta 没切对）
node -e "console.log(process.execPath)"

# 4. 重装
rm -rf node_modules package-lock.json
npm install
```

## 版本冲突

`package.json#engines` 限制 Node 版本：

```json
{
  "engines": { "node": ">=20" }
}
```

Volta 会强制使用 `volta` 字段；nvm/fnm 用 `.nvmrc`。检查冲突：

```bash
node --version
cat package.json | grep -A2 '"volta"\|"engines"'
cat .nvmrc 2>/dev/null
```

## Windows PowerShell 执行策略

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

之后才能运行 npm / pnpm / yarn 脚本。

## 镜像与 CDN 慢

```bash
# 切换到淘宝镜像
npm config set registry https://registry.npmmirror.com/
pnpm config set registry https://registry.npmmirror.com/

# 部分二进制（sharp / puppeteer）有独立 CDN
export SHARP_DIST_BASE_URL=https://npmmirror.com/mirrors/sharp/
export PUPPETEER_DOWNLOAD_HOST=https://npmmirror.com/mirrors/
```

## EnvironmentSnapshot 信号速查

probe-node.sh 输出后，按字段快速判断：

| 字段 | 期望 | 失败原因 |
|------|------|----------|
| `system_node.version` | 非空且 ≥ 18 | 未装或版本太低 |
| `system_npm.version` | 非空 | 应随 Node 自带 |
| `volta_path` | 非空 | DesireCore Volta 未释放，调 `POST /api/runtime/volta/install` |
| `volta_tools.node` | 非空数组 | 还未装任何 Volta 管理的 Node 版本 |
| `package_json_volta` | 项目用 Volta | 优先 Volta，不要切到 nvm |
| `registry` | `*.npmmirror.com` | 已加速；空字符串可能是 npm 未装 |
| `proxy` | 非空 | 公司代理已设；如有问题先查代理 |

## 重置整个 Node.js 环境（最后手段）

```bash
# 1. 删除全局缓存
npm cache clean --force
pnpm store prune
yarn cache clean

# 2. 删除项目锁文件 + node_modules
rm -rf node_modules package-lock.json pnpm-lock.yaml yarn.lock

# 3. 重新探测
bash skills/nodejs-runtime/scripts/probe-node.sh

# 4. 按主 SKILL.md 决策树重新安装并 install
```
