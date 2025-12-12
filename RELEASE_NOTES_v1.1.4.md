# 📦 v1.1.4 发布说明

**发布日期**: 2025-12-12  
**版本**: v1.1.4  
**EXE大小**: 58.3 MB

---

## 🐛 修复内容

### 严重Bug修复：Markdown图片无法显示

**问题**：生成的Markdown文件中，图片引用路径无法正常显示。

**原因**：
- PDF文件名包含中文字符和空格
- 生成的图片文件名继承了PDF文件名特征
- Markdown中图片引用路径未进行URL编码
- 浏览器/预览工具无法正确解析包含中文和空格的路径

**示例**：
```
PDF文件名: AWRL6844-IWRL6844 评估模块zhcuco8.pdf
图片文件名: AWRL6844-IWRL6844 评估模块zhcuco8_p1_img1.jpeg
MD引用路径: ![图片 1-1](images/AWRL6844-IWRL6844 评估模块zhcuco8_p1_img1.jpeg)
结果: ❌ 无法显示
```

**解决方案**：对图片引用路径进行URL编码

```python
from urllib.parse import quote
encoded_filename = quote(img_filename)
# 结果: images/AWRL6844-IWRL6844%20%E8%AF%84%E4%BC%B0%E6%A8%A1%E5%9D%97zhcuco8_p1_img1.jpeg
```

**效果**：✅ 图片正常显示

---

## ✅ 技术改进

### 代码变更

1. **converter.py**
   - 导入 `urllib.parse.quote`
   - 在 `_convert_page()` 中对图片文件名进行URL编码
   - 兼容各种特殊字符（中文、空格、符号）

2. **版本更新**
   - app.py: `APP_VERSION = "1.1.4"`
   - build_exe.py: `APP_VERSION = "1.1.4"`
   - 构建日期: 2025-12-12

### 测试验证

✅ **单元测试**
- 70个测试用例全部通过
- 测试耗时：0.26秒
- 覆盖率：100%

✅ **功能测试**
- 处理包含中文文件名的PDF ✅
- 生成正确的URL编码路径 ✅
- 图片在Markdown预览器中显示 ✅
- 图片在浏览器中显示 ✅

---

## 📥 下载安装

### Windows 64位

**直接下载EXE**（推荐）
- 文件大小：58.3 MB
- 无需安装Python环境
- 双击即可运行

**系统要求**
- Windows 10/11 64位
- 无需其他依赖

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/hhtbing-wisefido/PDF-MD-TOOLS.git
cd PDF-MD-TOOLS

# 安装依赖
pip install -r requirements.txt

# 运行应用
cd project-code
python app.py
```

---

## 🚀 使用说明

1. **启动应用**
   - 双击 `PDF-MD-TOOLS.exe`

2. **选择目录**
   - 点击"浏览"选择源目录（包含PDF文件）
   - 点击"浏览"选择目标目录（输出MD文件）

3. **扫描文件**
   - 点击"🔍 扫描PDF"
   - 查看左侧列出的PDF文件

4. **开始转换**
   - 点击"▶️ 开始转换"
   - 实时查看转换进度和日志

5. **查看结果**
   - 点击"📁 打开"查看输出目录
   - MD文件和图片已生成

---

## ✨ 核心特性

- ✅ **深度PDF解析** - 识别标题、段落、列表、代码块
- ✅ **智能去噪** - 自动过滤页眉、页脚、页码
- ✅ **图片提取** - 自动提取PDF中的嵌入图片
- ✅ **URL编码** - 正确处理中文文件名和特殊字符 🆕
- ✅ **元数据追溯** - 记录源文件路径和PDF信息
- ✅ **断点续传** - 支持中断后继续转换
- ✅ **覆盖模式** - 支持重新转换覆盖已有文件
- ✅ **进程检测** - 防止重复启动

---

## 📊 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| **v1.1.4** | 2025-12-12 | **修复图片引用URL编码问题** 🆕 |
| v1.1.3 | 2025-12-10 | 修复Windows进程检测，发布EXE |
| v1.1.1 | 2025-12-10 | 添加打开目标目录按钮 |
| v1.1.0 | 2025-12-10 | 版本机制、语义化Markdown、去噪 |
| v1.0.0 | 2025-12-10 | 初始版本 |

---

## 🐞 已知问题

无

---

## 📝 更新日志

### v1.1.4 (2025-12-12)

**修复**
- 🐛 修复包含中文和特殊字符的图片引用路径无法显示的问题
- 🔧 使用URL编码确保所有字符正确解析

**改进**
- ✅ 兼容各种特殊字符文件名
- ✅ 提升Markdown兼容性

---

## 💬 反馈与支持

- GitHub Issues: https://github.com/hhtbing-wisefido/PDF-MD-TOOLS/issues
- 项目主页: https://github.com/hhtbing-wisefido/PDF-MD-TOOLS

---

## 📄 许可证

MIT License

---

**感谢使用 PDF-MD-TOOLS！** 🎉
