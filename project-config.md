# 📋 项目配置 - PDF-MD-TOOLS

**项目名称**: PDF-MD-TOOLS  
**项目类型**: Python工具  
**创建日期**: 2025-12-10  
**版本**: v0.1.0

---

## 🎯 项目说明

将PDF文件转换为Markdown格式的Python工具。

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
- **PDF解析**: PyMuPDF / pdfplumber
- **文本处理**: regex
- **CLI**: argparse / click

---

## 📂 代码结构

```
project-code/
├── pdf_parser/          PDF解析模块
│   ├── __init__.py
│   ├── extractor.py     文本提取
│   └── layout.py        布局分析
├── md_generator/        Markdown生成模块
│   ├── __init__.py
│   ├── converter.py     格式转换
│   └── formatter.py     格式化
├── utils/               工具模块
│   ├── __init__.py
│   └── helpers.py       辅助函数
├── tests/               测试文件
├── main.py              主入口
├── config.py            配置
└── README.md            代码说明
```

---

## ✅ 规则适用

本项目遵循 `.windsurf/rules/` 中的所有规则：
- 00-11号规则完全适用
- 知识库目录为只读

---

**最后更新**: 2025-12-10
