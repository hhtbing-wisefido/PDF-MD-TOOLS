# 📄 PDF-MD-TOOLS

> 将PDF文件转换为Markdown格式的Python工具

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-v0.1.0-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)]()

---

## ✨ 功能特性

- 🔄 **PDF转Markdown** - 将PDF文档转换为结构化Markdown
- 📊 **布局分析** - 智能识别标题、段落、列表
- 🖼️ **图片提取** - 支持提取PDF中的图片
- 📋 **表格识别** - 识别并转换表格（计划中）
- 🔧 **批量处理** - 支持批量转换多个PDF文件

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动桌面应用（推荐）

```bash
python run_app.py
```

### 命令行使用

```bash
# 转换单个PDF
python project-code/main.py input.pdf -o output.md

# 批量转换
python project-code/main.py ./pdfs/ -o ./outputs/
```

---

## 📁 项目结构

```
PDF-MD-TOOLS/
├── .windsurf/              Windsurf配置
│   └── rules/              规则系统（00-11）
├── project-code/           源代码 ⭐
│   ├── pdf_parser/         PDF解析模块
│   ├── md_generator/       Markdown生成模块
│   ├── utils/              工具模块
│   ├── tests/              测试文件
│   ├── main.py             主入口
│   └── README.md           代码说明
├── 项目文档/               开发文档
│   ├── 1-需求与设计/       需求、架构
│   ├── 2-开发记录/         开发记录
│   ├── 3-部署运维/         部署指南
│   ├── 4-完成度检查/       质量检查
│   └── 9-归档/             历史归档
├── 知识库/                 只读参考资料（可选）
├── project-config.md       项目配置
├── requirements.txt        依赖
├── .gitignore              Git忽略规则
└── README.md               本文件
```

---

## 🔧 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出路径 | 当前目录 |
| `-f, --format` | 输出格式 | md |
| `--extract-images` | 提取图片 | False |
| `--verbose` | 详细输出 | False |

---

## 📚 文档

- 📋 [项目配置](project-config.md)
- 📖 [需求与设计](项目文档/1-需求与设计/)
- 📝 [开发记录](项目文档/2-开发记录/)
- 🚀 [部署运维](项目文档/3-部署运维/)

---

## 🛠️ 开发计划

- [x] 项目结构初始化
- [ ] PDF文本提取
- [ ] 布局分析
- [ ] Markdown生成
- [ ] 图片提取
- [ ] 表格识别
- [ ] 批量处理

---

## 📄 许可证

MIT License

---

**最后更新**: 2025-12-10
