# 📂 project-code

> PDF-MD-TOOLS 源代码目录 | **v1.1.3**

---

## 📁 目录结构

```
project-code/
├── pdf_parser/          PDF深度解析模块
│   ├── __init__.py      模块入口
│   ├── extractor.py     深度内容提取（文本+图片+去噪）
│   └── layout.py        布局分析
├── md_generator/        Markdown生成模块
│   ├── __init__.py      模块入口
│   ├── converter.py     语义化转换（标题/列表/代码/引用）
│   └── formatter.py     格式化工具
├── tests/               单元测试 ⭐
│   ├── test_extractor.py   PDF解析测试（24个）
│   ├── test_converter.py   Markdown转换测试（29个）
│   ├── test_app.py         应用逻辑测试（17个）
│   ├── run_tests.py        测试运行器（带进度条）
│   └── README.md           测试说明
├── __init__.py          包入口
├── app.py               🖥️ GUI桌面应用主程序
└── README.md            本文件
```

---

## 🚀 运行

```bash
# 启动桌面应用
python app.py

# 运行测试
python tests/run_tests.py
```

---

## 📦 模块说明

### pdf_parser（PDF解析）
- **extractor.py** - 深度提取PDF内容
  - 文本块提取（保留字体、位置信息）
  - 嵌入图片提取
  - 页眉/页脚/页码去噪
  - 多栏布局支持

### md_generator（Markdown生成）
- **converter.py** - 语义化转换
  - 标题层级识别（H1-H3）
  - 列表转换（项目符号、编号）
  - 代码块识别（等宽字体）
  - 引用块转换
  - 数学公式（上标/下标）

### tests（单元测试）
- 70个测试用例，100%通过
- 带进度条和详细统计

---

## 🧪 测试覆盖

| 模块 | 测试数 | 覆盖内容 |
|------|--------|----------|
| pdf_parser | 24 | 页码检测、块类型、去噪、多栏 |
| md_generator | 29 | 标题、列表、代码、引用、段落 |
| app | 17 | 版本、状态、锁文件、进程检测 |

---

## 🔧 版本信息

- **当前版本**: v1.1.3
- **构建日期**: 2025-12-10
- **Python**: 3.9+

---

**最后更新**: 2025-12-10
