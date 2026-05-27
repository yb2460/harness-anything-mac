# cli-anything-WPS-mac

<h3 align="center">跨平台 Office 自动化 —— Windows 用 WPS，Mac/Linux 用 LibreOffice</h3>

---

## 这是什么

一个命令行工具，让 AI Agent 操控 Office 软件完成文档创建、编辑和导出。

- **Windows 上**——通过 COM 接口操控 WPS Office
- **macOS / Linux 上**——通过 headless 模式操控 LibreOffice

同样的命令，跨平台运行。

## 安装

### Windows（需要 WPS Office）

```bash
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

确保已安装 `pywin32`：

```bash
pip install pywin32
```

### macOS（需要 LibreOffice）

```bash
# 先装 LibreOffice
brew install --cask libreoffice

# 再装本工具
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

### Linux

```bash
sudo apt install libreoffice   # Debian/Ubuntu
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

### 验证安装

```bash
cli-anything-office --help
```

## 快速上手

```bash
# 创建文档
cli-anything-office document new --type writer --name "报告" -o report.json

# 添加内容
cli-anything-office --project report.json writer add-heading -t "前言" -l 1
cli-anything-office --project report.json writer add-paragraph -t "AI 生成的文字。"

# 导出
cli-anything-office --project report.json export render report.pdf -p pdf
cli-anything-office --project report.json export render report.docx -p docx
```

## 支持的操作

| WPS 文字 / Writer | WPS 表格 / Calc | WPS 演示 / Impress |
|---|---|---|
| 段落、标题、列表 | 工作表增删改 | 幻灯片增删改 |
| 表格、图片、分页 | 单元格读写 | 文本框、形状 |
| 字体/字号/颜色 | 公式、合并单元格 | 背景、布局 |
| 查找替换 | 批量填充 | 导出 PPTX/PDF |
| 导出 DOCX/PDF/TXT/HTML | 导出 XLSX/CSV/PDF | |

## 系统要求

| Windows | macOS | Linux |
|---------|-------|-------|
| WPS Office 2019+ | LibreOffice 7+ | LibreOffice 7+ |
| Python 3.10+ | Python 3.10+ | Python 3.10+ |
| pywin32 | — | — |

## 原理

```
CLI 命令 (跨平台统一)
    ↓
platform detection
   ╱           ╲
Windows       macOS/Linux
  WPS COM     LibreOffice headless
```

核心模块（writer/calc/impress/document/session）是纯 Python，不依赖任何平台。只有 `office_backend.py` 根据操作系统选择调用 WPS COM 或 LibreOffice 命令行。

## 开源协议

MIT
