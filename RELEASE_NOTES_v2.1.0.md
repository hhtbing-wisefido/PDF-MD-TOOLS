# 📦 PDF-MD-TOOLS v2.1.0 发布说明

**发布日期**: 2026-01-16  
**版本**: 2.1.0  
**文件大小**: ~67 MB

## ✨ 新功能

### 🔍 OCR 支持（扫描版 PDF）
- 新增对扫描版 PDF 的 OCR 文字识别支持
- 自动检测扫描版 PDF（无可提取文字的 PDF）
- 支持中英文混合识别（`chi_sim+eng`）
- GUI 新增"OCR扫描版"选项开关

### 🛠️ 代码质量改进

#### Office 解析器修复
1. **PPT 图片提取**：修复硬编码的 `shape_type == 13` 问题，改用 `MSO_SHAPE_TYPE.PICTURE` 常量
2. **Excel 图片提取**：修复 `_images` 属性访问方式，添加多种获取图片的方法
3. **旧格式转换**：改进 COM 对象清理，添加 `DisplayAlerts=False` 防止弹窗

#### 旧格式支持增强（.doc, .ppt, .xls）
- 延迟初始化 `win32com`，避免导入时错误
- 使用 `try-finally` 确保 COM 对象正确释放
- 添加 `ReadOnly=True` 避免意外修改源文件
- 改进错误处理和清理逻辑

## 📋 系统要求

### 基本要求
- Windows 10/11 64位
- 无需安装 Python

### OCR 功能要求（可选）
要使用 OCR 功能识别扫描版 PDF，需要额外安装 Tesseract-OCR：

1. 下载 Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时勾选语言包：
   - Chinese (Simplified) - 简体中文
   - Chinese (Traditional) - 繁体中文
3. 将 Tesseract 添加到系统 PATH

**注意**：如果未安装 Tesseract，OCR 选项会自动禁用，不影响其他功能正常使用。

## 📥 下载

- **Windows 可执行文件**: [PDF-MD-TOOLS.exe](./release/PDF-MD-TOOLS.exe)

## 🔄 升级指南

从 v2.0.0 升级：
1. 直接替换 `PDF-MD-TOOLS.exe` 文件
2. 无需修改配置

## 📝 更新日志

```
v2.1.0 (2026-01-16)
├── ✨ 新增 OCR 支持模块 (ocr_engine)
├── ✨ PDF 解析器集成 OCR 功能
├── ✨ GUI 新增 OCR 开关选项
├── 🐛 修复 PPT 图片提取硬编码问题
├── 🐛 修复 Excel 图片提取方式
├── 🐛 修复旧格式 COM 对象清理问题
├── 🔧 改进错误处理和健壮性
└── 📦 更新依赖: pytesseract>=0.3.10
```

## 🐛 已知限制

1. OCR 功能需要额外安装 Tesseract-OCR 软件
2. OCR 识别速度较慢（每页约 3-5 秒）
3. 复杂排版的扫描文档可能识别效果不佳

## 📚 相关文档

- [项目 README](../README.md)
- [GitHub Release 发布指南](../项目文档/3-部署运维/GitHub_Release_发布指南_v1.1.4.md)
