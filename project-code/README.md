# 📂 project-code

> PDF-MD-TOOLS 源代码目录

---

## 📁 目录结构

```
project-code/
├── pdf_parser/          PDF解析模块
│   ├── __init__.py      模块入口
│   ├── extractor.py     文本提取
│   └── layout.py        布局分析
├── md_generator/        Markdown生成模块
│   ├── __init__.py      模块入口
│   ├── converter.py     格式转换
│   └── formatter.py     格式化
├── __init__.py          包入口
├── app.py               🖥️ GUI桌面应用（主程序）
└── README.md            本文件
```

---

## 🚀 运行

```bash
# 从项目根目录
python run_app.py

# 或从project-code目录
python app.py
```

---

## 📦 模块说明

### pdf_parser
PDF文档解析，支持PyMuPDF和pdfplumber

### md_generator
将解析结果转换为结构化Markdown

### utils
通用工具函数

---

**最后更新**: 2025-12-10
