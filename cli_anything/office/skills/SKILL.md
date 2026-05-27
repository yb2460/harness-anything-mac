---
name: "cli-anything-wps"
description: "WPS Office CLI — 通过命令行操控 WPS 文字/表格/演示文稿"
---

# cli-anything-wps

通过 COM 自动化接口操控 WPS Office 的命令行工具。支持 WPS 文字（Writer）、WPS 表格（Calc）和 WPS 演示（Impress）。

## 前置条件

- **Windows 操作系统**
- **WPS Office**（已安装，版本 12.0+）
- **Python 3.10+**
- **pywin32**：`pip install pywin32`

## 安装

```bash
pip install -e .
# 验证
cli-anything-wps --help
```

## 命令结构

```
wps
├── document          # 文档管理
│   ├── new           # 创建新文档
│   ├── open          # 打开项目文件
│   ├── save          # 保存文档
│   ├── info          # 文档信息
│   ├── profiles      # 页面配置列表
│   └── json          # 打印原始 JSON
├── writer            # WPS 文字
│   ├── add-paragraph
│   ├── add-heading
│   ├── add-list
│   ├── add-table
│   ├── add-page-break
│   ├── add-image
│   ├── remove
│   ├── list
│   ├── set-text
│   └── find-replace
├── calc              # WPS 表格
│   ├── add-sheet
│   ├── remove-sheet
│   ├── rename-sheet
│   ├── set-cell
│   ├── get-cell
│   ├── set-range
│   ├── merge-cells
│   └── list-sheets
├── impress           # WPS 演示
│   ├── add-slide
│   ├── remove-slide
│   ├── set-content
│   ├── list-slides
│   └── add-element
├── style             # 样式管理
│   ├── create
│   ├── modify
│   ├── list
│   ├── apply
│   └── remove
├── export            # 导出
│   ├── presets       # 列出预设
│   ├── preset-info   # 预设详情
│   └── render        # 导出到文件
└── session           # 会话管理
    ├── status
    ├── undo
    ├── redo
    └── history
```

## 使用示例

### 创建并编辑文档

```bash
# 创建新文档
cli-anything-wps document new --type writer --name "报告" -o report.json

# 添加内容
cli-anything-wps --project report.json writer add-heading -t "年度报告" -l 1
cli-anything-wps --project report.json writer add-paragraph -t "这是报告正文内容。"
cli-anything-wps --project report.json writer add-table -r 3 -c 3

# 导出为 DOCX
cli-anything-wps --project report.json export render report.docx -p docx

# 导出为 PDF
cli-anything-wps --project report.json export render report.pdf -p pdf
```

### 使用电子表格

```bash
cli-anything-wps document new --type calc --name "数据" -o data.json
cli-anything-wps --project data.json calc set-cell A1 "姓名"
cli-anything-wps --project data.json calc set-cell B1 "年龄"
cli-anything-wps --project data.json calc set-range A2 -d '[["张三",28],["李四",35]]'
cli-anything-wps --project data.json export render data.xlsx -p xlsx
```

### JSON 输出（Agent 使用）

```bash
# 所有命令都支持 --json 标志用于机器解析
cli-anything-wps --json document new --type writer --name "test"
cli-anything-wps --json --project test.json session status
```

### REPL 模式

```bash
cli-anything-wps
#> document new --type writer --name "演示"
#> writer add-paragraph -t "你好 WPS！"
#> export render demo.docx -p docx
#> quit
```

## Agent 使用指南

1. **所有命令都支持 `--json`**，返回结构化 JSON
2. **使用 `--project` 标志**加载现有项目，然后链式执行命令
3. **会话自动保存**：单次命令模式下，退出时会自动保存修改
4. **REPL 模式**适合交互式探索
5. **导出前确保内容已保存**到项目文件

## 导出预设

| 预设 | 说明 | 适用类型 |
|------|------|---------|
| docx | Word 文档 | writer |
| doc | Word 97-2003 | writer |
| pdf | PDF（从 Writer） | writer |
| txt | 纯文本 | writer |
| html | 网页 | writer |
| xlsx | Excel 工作簿 | calc |
| xls | Excel 97-2003 | calc |
| csv | CSV | calc |
| pdf-calc | PDF（从 Calc） | calc |
| pptx | PowerPoint | impress |
| ppt | PowerPoint 97-2003 | impress |
| pdf-impress | PDF（从 Impress） | impress |

## 原理

此 CLI 通过 Windows COM 接口与 WPS Office 通信：
- `KWPS.Application` → WPS 文字
- `KET.Application` → WPS 表格
- `KWPP.Application` → WPS 演示

WPS COM API 与 Microsoft Office VBA API 高度兼容。
