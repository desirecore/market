---
name: 电子表格处理
description: >-
  Use this skill any time a spreadsheet file is the primary input or output.
  This means any task where the user wants to: open, read, edit, or fix an
  existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing
  formulas, formatting, charting, cleaning messy data); create a new spreadsheet
  from scratch or from other data sources; or convert between tabular file
  formats. Trigger especially when the user references a spreadsheet file by
  name or path — even casually (like "the xlsx in my downloads") — and wants
  something done to it or produced from it. Also trigger for cleaning or
  restructuring messy tabular data files (malformed rows, misplaced headers,
  junk data) into proper spreadsheets. The deliverable must be a spreadsheet
  file. Do NOT trigger when the primary deliverable is a Word document, HTML
  report, standalone Python script, database pipeline, or Google Sheets API
  integration, even if tabular data is involved. Use when 用户提到 Excel、
  电子表格、xlsx、表格处理、公式计算、数据清洗、图表、CSV导入导出。
version: 1.0.2
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - xlsx
  - excel
  - spreadsheet
  - office
metadata:
  author: anthropic
  updated_at: '2026-04-13'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="xl-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="2.5" fill="url(#xl-a)" fill-opacity="0.1"
    stroke="url(#xl-a)" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9
    3v18M15 3v18" stroke="url(#xl-a)" stroke-width="1"
    stroke-opacity="0.4"/><rect x="9.5" y="3.5" width="5" height="5"
    rx="0.3" fill="#34C759" fill-opacity="0.3"/><circle cx="19" cy="19"
    r="3" fill="#34C759" fill-opacity="0.9"/><path d="M18 18.5l1 1.5 2-2.5"
    stroke="white" stroke-width="1.2" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  short_desc: 创建、编辑和处理 Excel 电子表格（.xlsx）
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# xlsx 技能

## L0：一句话摘要

创建、编辑和分析 Excel 电子表格（.xlsx），支持公式、格式、数据分析和可视化。

## L1：概述与使用场景

### 能力描述

xlsx 是一个**流程型技能（Procedural Skill）**，提供 Excel 电子表格的完整处理能力。基于 Python 库（openpyxl、pandas），支持创建新表格、编辑现有文件、数据分析、公式计算、格式设置和图表生成，并通过 LibreOffice 实现公式重算和错误检测。

### 使用场景

- 用户需要创建新的 Excel 电子表格（财务模型、数据报告等）
- 用户需要编辑或修改现有 .xlsx 文件
- 用户需要进行数据分析、清洗或格式转换（CSV/TSV → XLSX）
- 用户需要添加公式、图表或格式化现有表格

## L2：详细规范

## Prerequisites

### Python 3（必需）

在执行任何 Python 操作之前，先检测 Python 是否可用：

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

如果命令失败（Python 不可用），**必须停止并告知用户安装 Python 3**：

- **macOS**: `brew install python3` 或从 https://www.python.org/downloads/ 下载
- **Windows**: `winget install Python.Python.3` 或从 python.org 下载（安装时勾选 "Add Python to PATH"）
- **Linux (Debian/Ubuntu)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora/RHEL)**: `sudo dnf install python3 python3-pip`

如需更详细的环境配置帮助，加载 `environment-setup` 技能。

### Python 包依赖

本技能依赖以下 Python 包（按需检测）：

- `openpyxl` — Excel 文件创建和编辑（公式、格式）
- `pandas` — 数据分析和读写

检测方法：
```bash
python3 -c "import openpyxl; import pandas" 2>/dev/null || echo "MISSING"
```

缺失时告知用户安装：`pip install openpyxl pandas`

# Requirements for Outputs

## Output Rule

When you create or modify a .xlsx file, you **MUST** tell the user the absolute path of the output file in your response. Example: "文件已保存到：`/path/to/output.xlsx`"

## All Excel files

### Professional Font
- Use a consistent, professional font (e.g., Arial, Times New Roman) for all deliverables unless otherwise instructed by the user

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

## Financial models

### Color Coding Standards
Unless otherwise stated by the user or existing template

#### Industry-Standard Color Conventions
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated

### Number Formatting Standards

#### Required Format Rules
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use $#,##0 format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
- Use cell references instead of hardcoded values in formulas
- Example: Use =B5*(1+$B$6) instead of =B5*1.05

#### Formula Error Prevention
- Verify all cell references are correct
- Check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)
- Verify no unintended circular references

#### Documentation Requirements for Hardcodes
- Comment or in cells beside (if end of table). Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"
- Examples:
  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
  - "Source: Company 10-Q, Q2 2025, Exhibit 99.1, [SEC EDGAR URL]"
  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"
  - "Source: FactSet, 8/20/2025, Consensus Estimates Screen"

# XLSX creation, editing, and analysis

## Overview

A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.

## Important Requirements

**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `scripts/recalc.py` script. The script automatically configures LibreOffice on first run, including in sandboxed environments where Unix sockets are restricted (handled by `scripts/office/soffice.py`)

## Reading and analyzing data

### Data analysis with pandas
For data analysis, visualization, and basic operations, use **pandas** which provides powerful data manipulation capabilities:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

# Analyze
df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

# Write Excel
df.to_excel('output.xlsx', index=False)
```

## Excel File Workflows

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable.

### ❌ WRONG - Hardcoding Calculated Values
```python
# Bad: Calculating in Python and hardcoding result
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# Bad: Computing growth rate in Python
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # Hardcodes 0.15

# Bad: Python calculation for average
avg = sum(values) / len(values)
sheet['D20'] = avg  # Hardcodes 42.5
```

### ✅ CORRECT - Using Excel Formulas
```python
# Good: Let Excel calculate the sum
sheet['B10'] = '=SUM(B2:B9)'

# Good: Growth rate as Excel formula
sheet['C5'] = '=(C4-C2)/C2'

# Good: Average using Excel function
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to ALL calculations - totals, percentages, ratios, differences, etc. The spreadsheet should be able to recalculate when source data changes.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the scripts/recalc.py script
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **Verify and fix any errors**: 
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix the identified errors and recalculate again
   - Common errors to fix:
     - `#REF!`: Invalid cell references
     - `#DIV/0!`: Division by zero
     - `#VALUE!`: Wrong data type in formula
     - `#NAME?`: Unrecognized formula name

### Creating new Excel files

```python
# Using openpyxl for formulas and formatting
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### Editing existing Excel files

```python
# Using openpyxl to preserve formulas and formatting
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating formulas

Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `scripts/recalc.py` script to recalculate formulas:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

Example:
```bash
python scripts/recalc.py output.xlsx 30
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts
- Works on both Linux and macOS

## Formula Verification Checklist

Quick checks to ensure formulas work correctly:

### Essential Verification
- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Far-right columns**: FY data often in columns 50+ 
- [ ] **Multiple matches**: Search all occurrences, not just first
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Wrong references**: Verify all cell references point to intended cells (#REF!)
- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets

### Formula Testing Strategy
- [ ] **Start small**: Test formulas on 2-3 cells before applying broadly
- [ ] **Verify dependencies**: Check all cells referenced in formulas exist
- [ ] **Test edge cases**: Include zero, negative, and very large values

### Interpreting scripts/recalc.py Output
The script returns JSON with error details:
```json
{
  "status": "success",           // or "errors_found"
  "total_errors": 0,              // Total error count
  "total_formulas": 42,           // Number of formulas in file
  "error_summary": {              // Only present if errors found
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
- For large files: Use `read_only=True` for reading or `write_only=True` for writing
- Formulas are preserved but not evaluated - use scripts/recalc.py to update values

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
**IMPORTANT**: When generating Python code for Excel operations:
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

**For Excel files themselves**:
- Add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values
- Include notes for key calculations and model sections