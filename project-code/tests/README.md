# 📋 测试套件

## 运行测试

```bash
# 在project-code目录下运行
python -m pytest tests/ -v

# 或使用测试运行器
python tests/run_tests.py
```

## 测试文件

| 文件 | 说明 |
|------|------|
| `test_extractor.py` | PDF解析模块测试 |
| `test_converter.py` | Markdown转换模块测试 |
| `test_app.py` | 应用逻辑测试 |

## 测试覆盖

- ✅ 文本块解析
- ✅ 标题层级识别
- ✅ 列表检测
- ✅ 代码块检测
- ✅ 引用块检测
- ✅ 页眉页脚去噪
- ✅ 页码过滤
- ✅ 多栏排序
- ✅ Markdown转换
- ✅ 元数据提取
