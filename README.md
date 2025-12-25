# 📄 PDF-MD-TOOLS

> Windows桌面应用 - 批量将PDF转换为语义化Markdown

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-v1.2.0-green.svg)]()
[![Tests](https://img.shields.io/badge/tests-70%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)]()

---

## ✨ 功能特性

- 🖥️ **Windows桌面应用** - 现代化GUI界面，左右分栏显示
- 🎯 **双模式输出** - 集中输出 / 就地输出到源文件目录（v1.2.0新增）
- 🔄 **深度PDF解析** - 语义化提取（标题层级、列表、代码块、引用）
- 🖼️ **嵌入图片提取** - 自动提取PDF中的图片并保存
- 🧹 **智能去噪** - 自动过滤页眉、页脚、页码
- 📖 **多栏支持** - 正确处理多栏PDF的阅读顺序
- 📋 **元数据追溯** - MD文件包含源PDF绝对路径和元数据
- 🔄 **断点续传** - 支持中断后继续转换
- ✅ **覆盖模式** - 支持重新转换覆盖已有文件
- 🔒 **进程检测** - 防止重复启动

---

## 📥 下载安装

### 方式1：直接下载EXE（推荐）

👉 **[下载 PDF-MD-TOOLS_v1.2.0.exe (58MB)](https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/releases/tag/v1.2.0)**

- 无需安装Python
- 双击即可运行
- 支持Windows 10/11 64位

### 方式2：从源码运行

```bash
pip install -r requirements.txt
```

### 2. 启动桌面应用

```bash
cd project-code
python app.py
```

### 3. 使用步骤

#### 集中输出模式（默认）
1. 选择 **📂 集中输出到目标目录**
2. 点击 **浏览** 选择源目录（包含PDF的目录）
3. 点击 **浏览** 选择目标目录（输出MD的目录）
4. 点击 **🔍 扫描PDF** 扫描文件
5. 点击 **▶️ 开始转换** 开始批量转换
6. 点击 **📁 打开** 查看输出目录

#### 就地输出模式（v1.2.0新增）
1. 选择 **📍 就地输出到源文件目录**
2. 点击 **浏览** 选择源目录（包含PDF的目录）
3. 点击 **🔍 扫描PDF** 扫描文件
4. 点击 **▶️ 开始转换**
5. MD文件和图片将直接保存在PDF所在目录

---

## 📁 项目结构

```
PDF-MD-TOOLS/
├── .windsurf/              Windsurf规则配置
│   └── rules/              规则系统（00-13）
├── .github/                GitHub配置
│   └── instructions/       Copilot指令
├── project-code/           源代码 ⭐
│   ├── pdf_parser/         PDF深度解析模块
│   ├── md_generator/       Markdown转换模块
│   ├── tests/              单元测试（70个测试用例）
│   ├── app.py              🖥️ GUI桌面应用主程序
│   └── README.md           代码说明
├── 项目文档/               开发文档
│   ├── 1-需求与设计/       需求、架构
│   ├── 2-开发记录/         开发过程记录
│   ├── 3-部署运维/         部署指南
│   ├── 4-完成度检查/       质量检查
│   └── 9-归档/             历史归档
├── project-config.md       项目配置
├── requirements.txt        Python依赖
├── .gitignore              Git忽略规则
└── README.md               本文件
```

---

## 🧪 运行测试

```bash
cd project-code
python tests/run_tests.py
```

测试覆盖：
- ✅ PDF解析（24个测试）
- ✅ Markdown转换（29个测试）
- ✅ 应用逻辑（17个测试）

---

## 📊 转换效果

生成的Markdown包含：

```markdown
# 文档标题

> **源文件名**: example.pdf
> **源文件绝对路径**: `D:\docs\example.pdf`
> **作者**: John Doe
> **页数**: 25
> **文件大小**: 1234.5 KB
> **转换时间**: 2025-12-10 16:00:00
> **提取图片**: 8 张

---

## 第一章 标题

正文内容...

![图片 1-1](images/example_p1_img1.png)
```

---

## 📚 文档

- 📋 [项目配置](project-config.md)
- 📖 [需求与设计](项目文档/1-需求与设计/)
- 📝 [开发记录](项目文档/2-开发记录/)
- 🚀 [部署运维](项目文档/3-部署运维/)

---

## 🛠️ 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1.3 | 2025-12-10 | 修复Windows进程检测 |
| v1.1.2 | 2025-12-10 | 进程检测优化 |
| v1.1.1 | 2025-12-10 | 添加打开目标目录按钮 |
| v1.1.0 | 2025-12-10 | 版本机制、语义化Markdown、去噪 |
| v1.0.0 | 2025-12-10 | 初始版本 |

---

## 📄 许可证

MIT License

---

**最后更新**: 2025-12-10 | **当前版本**: v1.1.3
