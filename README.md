# cli-anything-WPS-mac

<h3 align="center">跨平台 AI 工具集 —— Office 操控 + Zotero 学术研究</h3>

<p align="center">
  <img src="https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/协议-MIT-green" alt="License">
</p>

---

## 包含项目

### 1. cli-anything-office — 跨平台 Office 操控

- **Windows**: WPS COM 接口
- **macOS/Linux**: LibreOffice headless

```bash
cli-anything-office document new --type writer --name "报告"
cli-anything-office export render report.pdf -p pdf
```

### 2. cli-anything-zotero — 学术研究智能体

文献管理 + 27 个学术 Skill 集成。写综述、写论文、审稿、做图表一站式。

```bash
cli-anything-zotero skills list                    # 列出所有学术 Skill
cli-anything-zotero skills pipeline thesis          # 学位论文推荐流程
cli-anything-zotero skills journal "Nature"         # 期刊图表规范
```

**7 大 Skill 分类:** search(3) / research(4) / writing(5) / review(5) / visualization(4) / analysis(3) / pipeline(2)

---

## 安装

### Windows (WPS + pywin32)
```bash
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
pip install pywin32
```

### macOS (LibreOffice)
```bash
brew install --cask libreoffice
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

### Linux
```bash
sudo apt install libreoffice
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

## PPT 设计系统

4 套预设 (academic/consultant/business/tech) + 14 种布局 + 5 维度质量审查

```bash
cli-anything-office preset apply academic --talk-type conference
```

## 许可证

MIT
