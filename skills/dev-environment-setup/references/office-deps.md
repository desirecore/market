# 办公技能依赖速查

DesireCore 办公四件套（DOCX / PDF / XLSX / PPTX）所需依赖汇总。Python 包通过 `python-runtime` skill 决策树安装；Node.js 包通过 `nodejs-runtime` skill；系统工具见 `system-tools.md`。

## DOCX（Word 文档）

```bash
# Python 包
pip install lxml defusedxml

# Node.js 包
npm install -g docx

# 系统工具
# pandoc      —— 文本提取
# LibreOffice —— PDF 转换
```

## PDF（PDF 文档）

```bash
# Python 核心
pip install pypdf pdfplumber Pillow

# Python 可选
pip install reportlab     # PDF 创建
pip install pdf2image     # PDF 转图片（需 poppler）
pip install pytesseract   # OCR（需 tesseract）

# 系统工具
# poppler-utils —— pdftotext / pdftoppm / pdfimages
# qpdf          —— 合并 / 拆分 / 解密
# tesseract     —— OCR 引擎
```

## XLSX（电子表格）

```bash
# Python
pip install openpyxl pandas

# 系统工具
# LibreOffice —— 公式重算
```

## PPTX（演示文稿）

```bash
# Python
pip install "markitdown[pptx]" Pillow

# Node.js
npm install -g pptxgenjs

# 系统工具
# LibreOffice    —— PDF 转换
# poppler-utils  —— PDF 转图片
```

## 一键安装四件套全部依赖

### macOS / Linux

```bash
# Python（在虚拟环境中，或用 pipx 安装 CLI 工具）
pip install lxml defusedxml pypdf pdfplumber Pillow reportlab openpyxl pandas "markitdown[pptx]"

# Node.js（用户级 prefix，避免 sudo）
npm install -g docx pptxgenjs

# 系统工具（macOS）
brew install --cask libreoffice
brew install poppler qpdf pandoc tesseract tesseract-lang

# 系统工具（Ubuntu/Debian）
sudo apt install libreoffice poppler-utils qpdf pandoc tesseract-ocr tesseract-ocr-chi-sim
```

### Windows

```powershell
# Python
pip install lxml defusedxml pypdf pdfplumber Pillow reportlab openpyxl pandas "markitdown[pptx]"

# Node.js
npm install -g docx pptxgenjs

# 系统工具
winget install TheDocumentFoundation.LibreOffice
winget install JohnMacFarlane.Pandoc
# poppler / qpdf / tesseract 见 system-tools.md
```

## 包名 vs import 名

| 安装名（pip） | import 名 |
|---------------|-----------|
| Pillow | PIL |
| beautifulsoup4 | bs4 |
| python-dateutil | dateutil |
| markitdown | markitdown |
| pypdf | pypdf |

## 环境验证脚本

四件套依赖速查（保存为 `check-office.sh`）：

```bash
#!/usr/bin/env bash
echo "=== Python ==="
python3 --version 2>/dev/null || echo "MISSING: python3"

echo "=== pip ==="
pip3 --version 2>/dev/null || echo "MISSING: pip3"

echo "=== Node.js ==="
node --version 2>/dev/null || echo "MISSING: node"

echo "=== npm ==="
npm --version 2>/dev/null || echo "MISSING: npm"

echo "=== Python Packages ==="
python3 - <<'PY'
packages = {
    'lxml': 'lxml',
    'defusedxml': 'defusedxml',
    'pypdf': 'pypdf',
    'pdfplumber': 'pdfplumber',
    'PIL': 'Pillow',
    'openpyxl': 'openpyxl',
    'pandas': 'pandas',
    'markitdown': 'markitdown',
    'reportlab': 'reportlab',
}
for mod, pkg in packages.items():
    try:
        __import__(mod)
        print(f'  OK: {pkg}')
    except ImportError:
        print(f'  MISSING: {pkg}')
PY

echo "=== Node.js Global Packages ==="
for pkg in docx pptxgenjs; do
    node -e "require('$pkg')" 2>/dev/null && echo "  OK: $pkg" || echo "  MISSING: $pkg"
done

echo "=== System Tools ==="
for cmd in soffice pandoc pdftoppm pdftotext qpdf tesseract; do
    command -v "$cmd" >/dev/null 2>&1 && echo "  OK: $cmd" || echo "  MISSING: $cmd"
done
```

## 跨 skill 协作

办公技能（docx / pdf / xlsx / pptx）报告依赖缺失时，按以下顺序：

1. **Python 缺失** → 触发 `python-runtime` skill 决策树
2. **Node.js 缺失** → 触发 `nodejs-runtime` skill 决策树
3. **Python/Node.js 包缺失** → 上方一键命令
4. **系统工具缺失** → `system-tools.md`

## 在 DesireCore 应用内通过 API 装包

DesireCore 内置 Hatch/Volta，但**不直接管理 pip / npm 包安装**——只管理 Python / Node 自身版本。包安装仍走 `pip install` / `npm install`。

如果使用 Hatch 创建的 Python：
```bash
${DESIRECORE_ROOT}/runtime/hatch/local/3.12/python/bin/python3 -m pip install lxml defusedxml
```

如果使用 Volta 安装的 Node：
```bash
${DESIRECORE_ROOT}/runtime/volta/bin/npm install -g docx pptxgenjs
```
