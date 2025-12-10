"""
🧪 测试运行器

运行所有单元测试并生成报告
"""

import sys
import unittest
import time
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("📋 PDF-MD-TOOLS 测试套件")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 发现并加载测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试模块
    test_dir = Path(__file__).parent
    
    test_modules = [
        'test_extractor',
        'test_converter',
        'test_app',
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"✅ 加载测试模块: {module_name}")
        except ImportError as e:
            print(f"❌ 无法加载模块 {module_name}: {e}")
    
    print()
    print("-" * 60)
    print("🧪 运行测试...")
    print("-" * 60)
    print()
    
    # 运行测试
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    end_time = time.time()
    
    # 打印总结
    print()
    print("=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failures - errors - skipped
    
    print(f"  总计测试: {total}")
    print(f"  ✅ 通过: {passed}")
    print(f"  ❌ 失败: {failures}")
    print(f"  💥 错误: {errors}")
    print(f"  ⏭️ 跳过: {skipped}")
    print(f"  ⏱️ 耗时: {end_time - start_time:.2f} 秒")
    print()
    
    if failures > 0:
        print("❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if errors > 0:
        print("💥 出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print()
    if result.wasSuccessful():
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 存在测试失败或错误")
        return 1


def run_specific_test(test_name: str):
    """运行特定测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    try:
        if '.' in test_name:
            # 运行特定测试方法
            suite.addTest(unittest.TestLoader().loadTestsFromName(test_name))
        else:
            # 运行整个测试模块
            module = __import__(test_name)
            suite.addTests(loader.loadTestsFromModule(module))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"❌ 无法运行测试 {test_name}: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 运行特定测试
        exit_code = run_specific_test(sys.argv[1])
    else:
        # 运行所有测试
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
