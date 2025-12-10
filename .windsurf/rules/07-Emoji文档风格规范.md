---
trigger: always_on
description: "所有Markdown文档使用Emoji增强风格"
---

# Emoji文档风格规范

**规则类型**: 🔴 强制规则  
**适用范围**: 所有Markdown文档（.md文件）

---



## 🔴 AI创建Markdown文档前强制检查

**在创建任何.md文件之前**，AI必须检查：

 **检查1**: 文档内容是否包含emoji？
   - 标题有emoji吗（如 # 📋 标题）？
   - 重要段落有emoji标记吗？
   - 如果没有  ❌ 必须添加！

 **检查2**: Emoji使用是否合适？
   - 一级标题至少有1个emoji
   - 二级标题推荐使用emoji
   - 重要提示必须有emoji（✅❌⚠️等）

 **检查3**: 例外情况？
   - 这是代码文档吗？
   - 这是纯数据文件吗？
   - 如果不是例外  必须使用emoji

**AI必须主动添加emoji**：
`markdown
# 📋 项目文档   自动添加
## ✨ 特性       自动添加  
- ✅ 完成       自动添加
- ❌ 禁止       自动添加
`

**绝对禁止**：
- ❌ 创建纯文字md文档（除非用户明确要求）
- ❌ 标题完全没有emoji

**AI违规记录**：
- 如果创建了纯文字文档  立即编辑添加emoji

## 🎯 核心原则

### 1. 必须使用Emoji
- ✅ 所有新创建的.md文档必须使用Emoji增强风格
- ✅ 修改现有文档时添加Emoji
- ✅ 保持专业性和可读性

### 2. Visual Documentation Pattern
- 使用表情符号建立清晰的层次结构
- 通过视觉元素快速传达信息
- 降低认知负担，提升用户体验

---

## 📋 常用Emoji分类

### 状态指示符
```markdown
✅ Done / Correct / Success / Allowed
❌ Wrong / Forbidden / Error / Failed
⚠️ Warning / Caution / Attention Required
ℹ️ Information / Note
🔴 Critical / Error / Stopped
🟡 Warning / In Progress
🟢 Success / Running / Active
⭐ Important / Featured / Recommended
```

### 文件和目录图标
```markdown
📁 Directory / Folder
📄 File / Document
📋 List / Checklist / Form
📊 Statistics / Chart / Data
📦 Package / Bundle / Archive
📝 Note / Edit / Writing
📚 Documentation / Book / Guide
```

### 操作和工具图标
```markdown
🔧 Configuration / Fix / Settings
🛠️ Tools / Maintenance / Build
🚀 Launch / Deploy / Release
🔄 Update / Refresh / Sync
💾 Save / Backup / Storage
🔍 Search / Inspect / Zoom
🔗 Link / Connection / Reference
🔑 Key / Authentication / Security
```

### 提示和建议图标
```markdown
�� Tip / Idea / Suggestion
📝 Note / Comment / Documentation
🎯 Goal / Target / Focus
🔔 Notification / Alert
🎉 Celebration / Success / Achievement
👍 Thumbs Up / Good / Approved
👎 Thumbs Down / Bad / Rejected
```

### 开发和版本控制
```markdown
🐛 Bug / Issue / Problem
✨ New Feature / Enhancement
🎨 Design / Style / Format
♻️ Refactor / Rewrite
🔥 Remove Code / Delete
💥 Breaking Change / Major Update
🚧 Work in Progress / Under Construction
📌 Pin / Pinned / Fixed Version
🏷️ Tag / Release / Version
```

---

## 🎨 使用规则

### 1. 一致性（Consistency）
```markdown
✅ 正确示例：
- ✅ 完成任务A
- ✅ 完成任务B
- ❌ 禁止操作X
- ❌ 禁止操作Y

❌ 错误示例：
- ✅ 完成任务A
- 👍 完成任务B  （不一致）
- ❌ 禁止操作X
- 🚫 禁止操作Y  （不一致）
```

### 2. 克制性（Restraint）
```markdown
✅ 适度使用：
## 📋 配置说明
- ✅ 设置环境变量
- 修改配置文件
- ⚠️ 注意权限设置

❌ 过度使用：
## 📋 配置说明 🎯
- ✅ 设置环境变量 🔧
- 📝 修改配置文件 📝
- ⚠️ 注意权限设置 🔒
```

### 3. 语义化（Semantic）
```markdown
✅ 语义明确：
- 📁 目录结构
- 🔧 配置文件
- 💾 备份数据

❌ 语义模糊：
- 🎈 目录结构  （气球与目录无关）
- 🍕 配置文件  （披萨与配置无关）
```

### 4. 可访问性（Accessibility）
```markdown
✅ 良好实践：
❌ **禁止**: 不要在根目录创建临时文件
（即使看不到emoji，也能理解内容）

❌ 不好实践：
❌（单独使用emoji，没有文字说明）
```

---

## 📝 标题层级使用频率

| 位置 | 频率 | 示例 |
|------|------|------|
| 一级标题 | 可选 | # 📚 项目文档 |
| 二级标题 | 推荐 | ## 🚀 快速开始 |
| 三级标题 | 适度 | ### 💡 最佳实践 |
| 段落开头 | 克制 | ⚠️ **重要**: ... |
| 列表项 | 适度 | - ✅ 完成安装 |
| 代码块 | 不用 | 代码中不使用emoji |

---

## 🎯 不同文档类型建议

### README.md（推荐 Moderate 风格）
```markdown
# 📦 Project Name

## ✨ 特性
- 🚀 快速启动
- 🔒 安全可靠
- 📚 完整文档

## 🚀 快速开始
...

## 📚 文档
...
```

### 规范文档（推荐 Heavy 风格）
```markdown
# 📋 代码规范

## ✅ 应该做的事
- ✅ 使用有意义的变量名
- ✅ 添加必要的注释

## ❌ 不应该做的事
- ❌ 使用全局变量
- ❌ 忽略错误处理

## ⚠️ 注意事项
- ⚠️ 性能敏感的代码需要基准测试
```

### API文档（推荐 Minimal 风格）
```markdown
# API 文档

## 📋 接口列表

### GET /api/users
✅ 成功响应
❌ 错误响应
```

---

## ✅ 检查清单

文档创建/修改时必须检查：

- [ ] 📋 标题层级是否使用了合适的emoji？
- [ ] ✅ 状态指示符是否一致？
- [ ] �� 目录结构是否清晰？
- [ ] 💡 重要提示是否醒目？
- [ ] ⚠️ 警告信息是否突出？
- [ ] 🎨 整体风格是否统一？
- [ ] 📚 即使不显示emoji是否仍可理解？
- [ ] 🌐 跨平台兼容性是否良好？

---

## 🚀 快速参考

### 常用组合
```markdown
# 状态
✅ ❌ ⚠️ ℹ️ ⭐

# 文件
📁 📄 📋 📊 📦

# 操作
🔧 🛠️ 🚀 🔄 💾

# 提示
💡 📝 🎯 🔔 🎉

# 开发
🐛 ✨ 🎨 ♻️ 🔥
```

---

## 💡 AI执行要求

### 创建新文档时
1. ✅ 自动使用Emoji增强风格
2. ✅ 为标题选择合适的emoji
3. ✅ 为重要信息添加视觉标记
4. ✅ 保持风格一致性

### 修改现有文档时
1. ✅ 如果文档没有emoji，主动添加
2. ✅ 保持与现有风格一致
3. ✅ 不过度使用，保持克制

### 不要做的事
1. ❌ 不在代码块中使用emoji
2. ❌ 不使用语义不明的emoji
3. ❌ 不过度装饰每个词
4. ❌ 不忽略可访问性

---

**参考资源**：
- Gitmoji: https://gitmoji.dev/
- Emojipedia: https://emojipedia.org/

**AI必须主动遵守此风格规范，无需等待提醒！** 🎯