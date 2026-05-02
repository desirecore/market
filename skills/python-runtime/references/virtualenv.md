# Python 虚拟环境

虚拟环境隔离项目依赖，避免污染全局环境。**强烈建议每个项目独立 venv**。

## venv（标准库，首选）

```bash
# 创建（Python 3.3+ 自带）
python3 -m venv .venv

# 激活
# macOS / Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 验证（路径应指向 .venv）
which python    # macOS / Linux
where python    # Windows

# 安装依赖
pip install -r requirements.txt

# 退出
deactivate
```

### 用 Hatch 安装的 Python 创建 venv

```bash
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 -m venv .venv
source .venv/bin/activate
```

## pipx（全局 CLI 工具）

`pipx` 把每个 CLI 工具装在独立 venv 里，对外暴露 shim，不污染系统/项目 Python。

```bash
# 安装 pipx
brew install pipx                # macOS
sudo apt install pipx            # Ubuntu/Debian
pip install --user pipx          # 通用兜底
pipx ensurepath
exec "$SHELL"

# 安装 CLI 工具
pipx install black
pipx install ruff
pipx install markitdown
pipx install poetry
pipx install uv

# 升级
pipx upgrade-all

# 卸载
pipx uninstall black

# 列表
pipx list
```

适用场景：black / ruff / mypy / poetry / uv / markitdown 等命令行工具。

## conda / miniconda（数据科学）

适用于：需要 BLAS / CUDA / 非 Python 依赖（科学计算）。

```bash
# 安装 miniconda（macOS / Linux）
curl -fsSL "https://repo.anaconda.com/miniconda/Miniconda3-latest-$(uname -s)-$(uname -m).sh" -o miniconda.sh
bash miniconda.sh -b -p "$HOME/miniconda3"
eval "$("$HOME/miniconda3/bin/conda" shell.$(basename $SHELL) hook)"

# Windows: 下载 https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe 安装

# 创建环境
conda create -n myproject python=3.12
conda activate myproject

# 装包（conda 优先，pip 兜底）
conda install numpy pandas scikit-learn
pip install some-pypi-only-package

# 导出 / 还原
conda env export > environment.yml
conda env create -f environment.yml

# 退出
conda deactivate
```

### conda 与 DesireCore Hatch 共存

两者都把 Python 装在用户目录，互不影响。规则：
- 数据科学项目（涉及 numpy/pandas/jupyter/CUDA）→ conda
- 普通 Web/CLI/办公技能 → Hatch + venv

## requirements.txt 与 pyproject.toml

### requirements.txt（简单）

```
fastapi==0.111.0
pydantic>=2.0,<3.0
markitdown
```

### pyproject.toml（现代）

```toml
[project]
name = "myproj"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.111",
  "pydantic>=2.0,<3.0",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
```

安装：`pip install -e .` 或 `pip install -e ".[dev]"`。

## 何时用哪个

| 场景 | 工具 |
|------|------|
| 普通 Python 项目 | venv + pip |
| 全局 CLI 工具（black/ruff/markitdown） | pipx |
| 数据科学 / Jupyter / CUDA | conda |
| 现代项目管理（含构建发布） | Hatch（自带项目管理）或 uv |
| 严格隔离 / 多 Python 版本快速切换 | DesireCore Hatch + venv |

## 常见误区

- ❌ `sudo pip install` —— 永远不要这样做
- ❌ 在系统 Python 上直接 `pip install` —— PEP 668 会拒绝
- ❌ 多个虚拟环境工具同时激活（venv + conda 嵌套）—— 路径会乱
- ❌ 把 venv 加入 git —— `.venv/` 应该在 `.gitignore` 里
