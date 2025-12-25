# 📋 GitHub Release 发布指南 - v1.1.4

**版本**: v1.1.4  
**发布日期**: 2025-12-12  
**状态**: ✅ 准备就绪

---

## 📦 发布资源

### 可执行文件
- **文件位置**: `project-code/release/PDF-MD-TOOLS_v1.1.4.exe`
- **文件大小**: 58.3 MB (61,165,449 bytes)
- **MD5**: (上传前计算)

### 发布说明
- **文件位置**: `RELEASE_NOTES_v1.1.4.md`
- **内容**: 详细的版本更新说明、修复内容、使用指南

---

## 🚀 发布步骤

### 1. 访问GitHub Release页面
```
https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/releases/new
```

### 2. 填写Release信息

**Tag version**: `v1.1.4`  
**Release title**: `v1.1.4 - 修复图片引用URL编码问题`

**Release描述**（复制以下内容）：

```markdown
## 🐛 重要修复

### 修复图片无法显示的问题

在 v1.1.3 及之前版本中，当PDF文件名包含中文字符或空格时，生成的Markdown文件中的图片引用无法正常显示。本版本通过对图片路径进行URL编码完全解决此问题。

**影响范围**: 所有包含中文或特殊字符的PDF文件  
**修复状态**: ✅ 已完全修复

---

## ✨ 改进内容

- 🔧 对图片引用路径进行URL编码，支持中文和特殊字符
- ✅ 兼容各种Markdown预览器和浏览器
- 📊 所有70个单元测试通过

---

## 📥 下载安装

### Windows 64位

**直接下载EXE**（推荐）
- 文件大小：58.3 MB
- 无需安装Python
- 双击即可运行
- 支持 Windows 10/11 64位

### 使用方法

1. 下载 `PDF-MD-TOOLS.exe`
2. 双击运行
3. 选择源目录（包含PDF）
4. 选择目标目录（输出MD）
5. 点击"扫描PDF" → "开始转换"
6. 查看生成的Markdown文件和图片

---

## 🔄 从旧版本升级

如果您使用的是 v1.1.3 或更早版本：

1. 下载新版本 v1.1.4
2. **重要**：重新转换包含中文文件名的PDF
3. 旧版本生成的图片引用可能无法显示，需要重新转换

---

## ✨ 核心特性

- ✅ 深度PDF解析（标题、段落、列表、代码块）
- ✅ 智能去噪（页眉、页脚、页码）
- ✅ 图片提取（自动提取嵌入图片）
- ✅ **URL编码**（正确处理中文文件名）🆕
- ✅ 元数据追溯（记录源文件路径）
- ✅ 断点续传
- ✅ 覆盖模式
- ✅ 进程检测

---

## 📊 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| **v1.1.4** | 2025-12-12 | **修复图片URL编码** 🆕 |
| v1.1.3 | 2025-12-10 | 修复进程检测 |
| v1.1.1 | 2025-12-10 | 添加打开目录按钮 |
| v1.1.0 | 2025-12-10 | 语义化Markdown |

---

## 🐞 已知问题

无

---

## 💬 反馈与支持

如有问题或建议，请提交 [Issue](https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/issues)

---

## 📄 许可证

MIT License

---

**完整更新日志**: [RELEASE_NOTES_v1.1.4.md](https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/blob/main/RELEASE_NOTES_v1.1.4.md)
```

### 3. 上传文件

**拖拽或选择上传**：
- `project-code/release/PDF-MD-TOOLS_v1.1.4.exe`

**重命名为**：
- `PDF-MD-TOOLS.exe` （方便用户识别）

### 4. 发布选项

- ✅ **Set as the latest release**（设为最新版本）
- ⬜ Set as a pre-release（不勾选）
- ⬜ Create a discussion（可选）

### 5. 点击 "Publish release"

---

## ✅ 发布后验证

### 1. 检查Release页面
```
https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/releases/tag/v1.1.4
```

### 2. 验证内容
- [ ] 版本号正确：v1.1.4
- [ ] 标题正确
- [ ] 描述内容完整
- [ ] EXE文件已上传
- [ ] 下载链接有效
- [ ] 文件大小正确显示

### 3. 测试下载
- [ ] 下载EXE文件
- [ ] 验证文件大小（58.3 MB）
- [ ] 运行EXE测试基本功能
- [ ] 测试中文文件名PDF转换
- [ ] 验证图片正常显示

---

## 📢 发布公告

发布后，可以在以下渠道宣布：

1. **GitHub Discussions**（如有）
2. **README.md** - 已更新下载链接
3. **项目文档** - 已更新版本信息

---

## 🔄 后续工作

- [ ] 监控Issue反馈
- [ ] 收集用户反馈
- [ ] 规划下一版本功能

---

**准备人**: AI  
**状态**: ✅ 已完成所有准备工作  
**最后更新**: 2025-12-12
