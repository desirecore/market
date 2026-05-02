# 系统工具安装

办公技能、PDF/OCR、文档转换会用到的系统级二进制工具。

## LibreOffice（文档转换 / 公式重算）

```bash
# macOS
brew install --cask libreoffice

# Ubuntu / Debian
sudo apt install libreoffice

# Fedora / RHEL
sudo dnf install libreoffice

# Arch
sudo pacman -S libreoffice-fresh

# Windows
winget install TheDocumentFoundation.LibreOffice
```

无头转换（CLI）：
```bash
soffice --headless --convert-to pdf input.docx
soffice --headless --calc --convert-to xlsx input.csv
```

## Poppler（PDF 工具集）

提供 `pdftotext` / `pdftoppm` / `pdfimages` / `pdftohtml` 等。

```bash
# macOS
brew install poppler

# Ubuntu / Debian
sudo apt install poppler-utils

# Fedora / RHEL
sudo dnf install poppler-utils

# Arch
sudo pacman -S poppler

# Windows（通过 conda 或手动）
conda install -c conda-forge poppler
# 或下载 https://github.com/oschwartz10612/poppler-windows/releases，将 bin/ 加入 PATH
```

常用：
```bash
pdftotext input.pdf output.txt
pdftoppm -png input.pdf prefix       # 每页一张 PNG
pdfimages -png input.pdf prefix      # 提取嵌入图片
```

## qpdf（PDF 操作）

合并 / 拆分 / 解密 / 加密。

```bash
# macOS
brew install qpdf

# Ubuntu / Debian
sudo apt install qpdf

# Fedora / RHEL
sudo dnf install qpdf

# Windows
winget install QPDF.QPDF
```

常用：
```bash
qpdf --decrypt --password=secret input.pdf output.pdf
qpdf --split-pages input.pdf output-%d.pdf
qpdf --empty --pages a.pdf b.pdf -- merged.pdf
```

## Pandoc（文档格式互转）

```bash
# macOS
brew install pandoc

# Ubuntu / Debian
sudo apt install pandoc

# Fedora / RHEL
sudo dnf install pandoc

# Arch
sudo pacman -S pandoc

# Windows
winget install JohnMacFarlane.Pandoc
```

常用：
```bash
pandoc input.docx -o output.md
pandoc input.md -o output.pdf --pdf-engine=xelatex
pandoc input.html -o output.docx
```

## Tesseract（OCR 引擎）

```bash
# macOS
brew install tesseract

# Ubuntu / Debian
sudo apt install tesseract-ocr

# Fedora / RHEL
sudo dnf install tesseract

# Arch
sudo pacman -S tesseract

# Windows
winget install UB-Mannheim.TesseractOCR
```

### 中文语言包

```bash
# macOS
brew install tesseract-lang

# Ubuntu / Debian
sudo apt install tesseract-ocr-chi-sim tesseract-ocr-chi-tra

# Fedora
sudo dnf install tesseract-langpack-chi_sim tesseract-langpack-chi_tra
```

使用：
```bash
tesseract image.png output -l chi_sim          # 简体
tesseract image.png output -l chi_sim+eng      # 中英混合
```

## ImageMagick（图像处理，可选）

```bash
brew install imagemagick                # macOS
sudo apt install imagemagick            # Ubuntu / Debian
sudo dnf install ImageMagick            # Fedora
winget install ImageMagick.ImageMagick  # Windows
```

## Ghostscript（PDF / PostScript 渲染）

```bash
brew install ghostscript                # macOS
sudo apt install ghostscript            # Ubuntu / Debian
sudo dnf install ghostscript            # Fedora
winget install ArtifexSoftware.GhostScript  # Windows
```

## Git（版本控制，必备）

```bash
brew install git                # macOS
sudo apt install git            # Ubuntu / Debian
sudo dnf install git            # Fedora
sudo pacman -S git              # Arch
winget install Git.Git          # Windows
```

macOS 上 `xcode-select --install` 也会带 git。

## 跨平台一键检查脚本

```bash
for cmd in soffice pandoc pdftoppm pdftotext pdfimages qpdf tesseract magick gs git; do
  command -v "$cmd" >/dev/null 2>&1 \
    && echo "  OK: $cmd ($(command -v "$cmd"))" \
    || echo "  MISSING: $cmd"
done
```

## 故障排查

### macOS: "soffice: command not found"

`/Applications/LibreOffice.app/Contents/MacOS/soffice` 是真实路径。建立软链：
```bash
ln -s /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/soffice
```

### Tesseract 找不到中文语言包

```bash
tesseract --list-langs               # 检查已安装语言
# 找到语言数据目录
tesseract --print-parameters | grep tessdata
# macOS Apple Silicon: /opt/homebrew/share/tessdata
# 把缺失的 chi_sim.traineddata 放进去
```

下载链接：https://github.com/tesseract-ocr/tessdata_fast

### Windows 工具未在 PATH

winget 安装后通常自动加入 PATH，重启终端即生效。手动安装的（如 poppler-windows）需要把 `<安装目录>\bin` 加入系统 PATH：

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";C:\poppler\bin",
  [EnvironmentVariableTarget]::User
)
```

重启终端验证：
```powershell
pdftotext --version
```
