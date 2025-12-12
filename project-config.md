# 📋 项目配置 - PDF-MD-TOOLS

**项目名称**: PDF-MD-TOOLS  
**项目类型**: Windows桌面应用 + Python工具  
**创建日期**: 2025-12-10  
**当前版本**: v1.1.4  
**GitHub Release**: [下载EXE](https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/releases/tag/v1.1.4)

---

## 🎯 项目说明

Windows桌面应用 - 批量将PDF转换为语义化Markdown。

**核心功能**：
- PDF深度解析（文本+图片）
- 语义化Markdown（标题/列表/代码块）
- 元数据追溯（源文件路径）
- 进程检测防重复启动

---

## 📁 目录映射

| 通用名称 | 本项目目录 | 说明 |
|---------|-----------|------|
| [代码目录] | `project-code/` | 项目源代码 |
| [文档目录] | `项目文档/` | 项目开发文档 |
| [需求设计目录] | `1-需求与设计/` | 需求、架构、设计 |
| [开发记录目录] | `2-开发记录/` | 开发过程记录 |
| [部署运维目录] | `3-部署运维/` | 部署、配置 |
| [完成度检查目录] | `4-完成度检查/` | 质量检查 |
| [归档目录] | `9-归档/` | 历史归档 |
| [知识库目录] | `知识库/` | 只读参考资料 |

---

## 🔧 技术栈

- **语言**: Python 3.9+
- **GUI**: customtkinter
- **PDF解析**: PyMuPDF / pdfplumber
- **打包**: PyInstaller

---

## 📂 代码结构

```
project-code/
├── pdf_parser/          PDF深度解析模块
│   ├── __init__.py
│   ├── extractor.py     深度提取（文本+图片+去噪）
│   └── layout.py        布局分析
├── md_generator/        Markdown生成模块
│   ├── __init__.py
│   ├── converter.py     语义化转换
│   └── formatter.py     格式化
├── tests/               单元测试（70个）
│   ├── test_extractor.py
│   ├── test_converter.py
│   ├── test_app.py
│   └── run_tests.py     测试运行器
├── app.py               🖥️ GUI主程序
├── build_exe.py         打包脚本
└── README.md            代码说明
```

---

## 🛠️ 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.1.4 | 2025-12-12 | 修复图片引用URL编码问题（中文文件名） |
| v1.1.3 | 2025-12-10 | 修复Windows进程检测，发布EXE |
| v1.1.1 | 2025-12-10 | 添加打开目标目录按钮 |
| v1.1.0 | 2025-12-10 | 版本机制、语义化Markdown、去噪 |
| v1.0.0 | 2025-12-10 | 初始版本 |

---

## ✅ 规则适用

本项目遵循 `.windsurf/rules/` 中的所有规则：
- 00-12号规则完全适用
- 知识库目录为只读
- pip安装使用代理 `socks5://127.0.0.1:4000`

---

**最后更新**: 2025-12-10
