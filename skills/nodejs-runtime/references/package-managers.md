# 包管理器策略（npm / pnpm / yarn）

## 选型建议

| 场景 | 推荐 |
|------|------|
| 默认（Node.js 自带） | npm |
| 磁盘高效 / 严格依赖 / monorepo | **pnpm**（推荐） |
| 项目已用 yarn | yarn classic / berry |
| DesireCore 应用内 | Volta 管理任何之上 |

## 通过 DesireCore Volta 安装

```bash
VOLTA=~/.desirecore/runtime/volta/volta
export VOLTA_FEATURE_PNPM=1

"$VOLTA" install pnpm@latest
"$VOLTA" install yarn@latest
"$VOLTA" install npm@10
```

或 HTTP API：

```bash
BASE="https://127.0.0.1:$(cat ~/.desirecore/agent-service.port)/api/runtime"
curl -sk -X POST "${BASE}/pkg/pnpm/install" -H "Content-Type: application/json" -d '{"version":"latest"}'
```

## 项目级固定版本

### package.json#volta（首选）

```json
{
  "volta": {
    "node": "22.11.0",
    "pnpm": "9.5.0"
  }
}
```

在装了 Volta 的环境中 `cd` 进项目即自动切换。

### packageManager 字段（Corepack 标准）

```json
{
  "packageManager": "pnpm@9.5.0"
}
```

由 Corepack（Node 16.10+ 自带）解析，被 npm/pnpm/yarn 自身识别。可与 Volta 共存。

## npm 全局安装

### 不要用 sudo

错误：
```bash
sudo npm install -g pkg     # ❌ 文件 owner 变成 root，后续维护麻烦
```

正确：改 npm 全局目录到用户目录。

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

npm install -g pptxgenjs docx
```

或用 Volta（自动隔离，无权限问题）：
```bash
volta install pptxgenjs   # ❌ Volta 不直接装库；只能装 CLI 工具
# 库依赖应通过项目 package.json 管理
```

## pnpm 配置

```bash
# 全局存储位置（pnpm 单存储多链接的核心）
pnpm config get store-dir
# 默认 ~/.local/share/pnpm/store/v3

# 改 registry
pnpm config set registry https://registry.npmmirror.com/

# 全局安装路径（独立于 npm）
pnpm config get global-bin-dir
```

## yarn 配置

```bash
# yarn classic
yarn config set registry https://registry.npmmirror.com/

# yarn berry
yarn config set npmRegistryServer https://registry.npmmirror.com/
```

## 镜像 / 代理

### 中国大陆加速

```bash
npm config set registry https://registry.npmmirror.com/
pnpm config set registry https://registry.npmmirror.com/
yarn config set registry https://registry.npmmirror.com/
```

恢复官方：
```bash
npm config set registry https://registry.npmjs.org/
```

### 公司代理

```bash
npm config set proxy http://proxy:port
npm config set https-proxy http://proxy:port

# 取消
npm config delete proxy
npm config delete https-proxy
```

### 私有 registry（Verdaccio / Nexus）

```bash
# 项目级（.npmrc）
@scope:registry=https://npm.company.com/
//npm.company.com/:_authToken=${NPM_TOKEN}
```

## 卸载与清理

```bash
# 全局列表
npm ls -g --depth=0
pnpm list -g --depth=0
yarn global list

# 卸载
npm uninstall -g pkg
pnpm uninstall -g pkg
yarn global remove pkg

# 清缓存
npm cache clean --force
pnpm store prune
yarn cache clean
```

## 环境快照

probe-node.sh 输出 `volta_tools.{node,pnpm,yarn,npm}` 列出所有 Volta 管理的版本，`registry` / `proxy` 来自 npm 配置。Skill 解析 JSON 即可判断是否需要切换镜像。
