# WSL2 安装与配置（Windows）

WSL2（Windows Subsystem for Linux 2）让 Windows 用户原生运行 Linux 环境，是运行 Python 脚本、Docker、各种开发工具的最佳方式。

## 检测

```powershell
wsl --status                   # 已安装时显示版本与默认发行版
wsl --list --verbose           # 已安装的发行版及版本
```

## 系统要求

- Windows 11（21H2+）或 Windows 10（版本 2004，Build 19041+）
- BIOS 启用 CPU 虚拟化（Intel VT-x / AMD-V）

## 安装

```powershell
# 以管理员身份打开 PowerShell

# 一键安装（含 WSL2 内核 + 默认 Ubuntu）
wsl --install

# 重启计算机后 Ubuntu 窗口自动打开，提示设置用户名密码
```

## 安装指定发行版

```powershell
wsl --list --online                     # 可选发行版
wsl --install -d Ubuntu-24.04
wsl --install -d Debian
wsl --set-default Ubuntu-24.04
```

## 确保使用 WSL2

```powershell
wsl --list --verbose
# VERSION 列应为 2

# 升级到 WSL2
wsl --set-version Ubuntu 2

# 默认 WSL2
wsl --set-default-version 2
```

## 进入 WSL2 后配置开发环境

按 Linux 方式配置即可：

```bash
# 进入
wsl

# 系统更新
sudo apt update && sudo apt upgrade -y

# Python（推荐用 python-runtime skill 走完整决策树）
sudo apt install python3 python3-pip python3-venv

# Node.js（推荐用 nodejs-runtime skill）
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install nodejs

# Docker（推荐 Docker Desktop 的 WSL2 后端，而非在 WSL2 内独立装）
```

## 文件互访

```bash
# WSL2 → Windows
ls /mnt/c/Users/<用户名>/Desktop/

# Windows → WSL2（资源管理器地址栏）
\\wsl$\Ubuntu\home\<用户名>\

# Windows Terminal 打开 WSL2
wsl ~
```

## 常见问题

### "WslRegisterDistribution failed with error: 0x80370102"

CPU 虚拟化未启用。重启进 BIOS，启用 Intel VT-x / AMD-V。

### 网络无法访问互联网

```bash
# 在 WSL2 内
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# 或 Windows 端关闭 Hyper-V 网卡的 DNS 自动管理
```

如果是公司 VPN 干扰，在 Windows 端 `wsl --shutdown` 后重启 VPN。

### 磁盘空间不足

```powershell
# 压缩 WSL2 虚拟磁盘
wsl --shutdown
# 然后用 diskpart 压缩 ext4.vhdx（高级操作，备份后再做）
```

或在 `~/.wslconfig` 限制大小：

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

### Windows 与 WSL2 时间不同步

```bash
sudo hwclock -s
```

或：
```bash
sudo apt install ntpdate
sudo ntpdate -s time.windows.com
```

### DesireCore 在 WSL2 中使用

DesireCore 是 Windows 桌面应用，运行在 Windows 端而非 WSL2 内。但 DesireCore 的环境检查（设置 → 环境检查）可以自动检测 Windows 版本、CPU 虚拟化、WSL2 状态，并提供一键修复入口。

## 性能建议

- 项目文件放在 WSL2 的 Linux 文件系统（`/home/<user>/`），不要放 `/mnt/c/`——后者跨文件系统 IO 极慢
- 编辑器：VS Code + Remote-WSL 扩展，自动跨边界
- Docker：使用 Docker Desktop 的 WSL2 后端，避免 WSL2 内独立 Docker 守护进程
