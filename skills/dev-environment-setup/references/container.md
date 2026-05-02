# 容器运行环境（Docker / Podman）

容器在开发中越来越常见——数据库、消息队列、AI 推理服务等多通过容器部署。

## 检测

```bash
docker --version 2>/dev/null && docker info --format '{{.OperatingSystem}}' 2>/dev/null \
  || echo "Docker NOT FOUND or daemon not running"

podman --version 2>/dev/null || echo "Podman NOT FOUND"
```

## Docker 安装

### macOS

推荐 Docker Desktop（含 Docker Engine + Compose + GUI）：

```bash
# 方式 1：Homebrew Cask（推荐）
brew install --cask docker

# 方式 2：官网下载
# https://www.docker.com/products/docker-desktop/
# 选择 Apple Silicon 或 Intel

# 验证
docker --version
docker run hello-world
```

### Windows

**推荐 Docker Desktop + WSL2 后端**（先装 WSL2，见 `wsl.md`）：

1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 安装时勾选 "Use WSL 2 instead of Hyper-V"
3. Settings → General 确认 "Use the WSL 2 based engine" 已启用

```powershell
winget install Docker.DockerDesktop
docker --version
docker run hello-world
```

**轻量替代（仅 CLI，通过 WSL2 内）**：

```bash
# 在 WSL2 Ubuntu 中
sudo apt update
sudo apt install docker.io docker-compose-v2
sudo usermod -aG docker $USER
# 重新登录 WSL2 后生效
```

### Linux（Debian / Ubuntu）

```bash
# 安装 Docker Engine（官方仓库）
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 免 sudo
sudo usermod -aG docker $USER
newgrp docker

docker run hello-world
```

### Linux（Fedora / RHEL）

```bash
sudo dnf install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

## Podman（无守护进程替代）

兼容 Docker CLI，无后台守护进程，更轻量。

```bash
# macOS
brew install podman
podman machine init
podman machine start

# Ubuntu / Debian
sudo apt install podman

# Fedora（预装）
podman --version

# Windows
winget install RedHat.Podman
```

使用方式与 Docker 一致：
```bash
podman run hello-world
podman ps
podman images
```

### Docker → Podman 别名

```bash
echo 'alias docker=podman' >> ~/.zshrc
```

## 常见问题

### "Cannot connect to the Docker daemon"

```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS / Windows
# 启动 Docker Desktop 应用（系统托盘应有鲸鱼图标）

# WSL2
# 在 Windows 端重启 Docker Desktop
```

### "permission denied while trying to connect to the Docker daemon socket"

```bash
sudo usermod -aG docker $USER
newgrp docker     # 当前 shell 立即生效
# 或重新登录
```

### Docker Desktop 占用资源过高

Docker Desktop Settings → Resources 调 CPU / Memory。WSL2 后端可编辑 `~/.wslconfig`：

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

### 镜像下载慢（中国大陆）

```bash
# 编辑 /etc/docker/daemon.json
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.m.daocloud.io"
  ]
}
EOF
sudo systemctl restart docker
```

macOS / Windows 在 Docker Desktop Settings → Docker Engine 中编辑 JSON。

### 磁盘空间被吃光

```bash
docker system df         # 查用量
docker system prune -a   # 清未用镜像/容器/网络
docker volume prune      # 清未挂载 volume（小心！数据会丢）
```

## 容器场景速查

| 场景 | 镜像 | 启动 |
|------|------|------|
| Postgres 测试 | `postgres:16` | `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=test postgres:16` |
| Redis | `redis:7` | `docker run -d -p 6379:6379 redis:7` |
| MySQL | `mysql:8` | `docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=test mysql:8` |
| MinIO（S3 兼容） | `minio/minio` | `docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address :9001` |

更复杂的场景使用 `docker compose up -d`。
