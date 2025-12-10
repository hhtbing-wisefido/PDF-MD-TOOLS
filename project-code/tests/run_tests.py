"""
🧪 测试运行器

运行所有单元测试并生成详细报告（带进度条和明细）
"""

import sys
import unittest
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class ProgressTestResult(unittest.TestResult):
    """带进度显示的测试结果"""
    
    def __init__(self, total_tests: int):
        super().__init__()
        self.total_tests = total_tests
        self.current_test = 0
        self.test_times: Dict[str, float] = {}
        self.current_start_time = 0
        self.module_results: Dict[str, Dict] = {}
        
    def _get_progress_bar(self, width: int = 30) -> str:
        """生成进度条"""
        if self.total_tests == 0:
            return "[" + "=" * width + "]"
        
        progress = self.current_test / self.total_tests
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percent = int(progress * 100)
        return f"[{bar}] {percent}%"
    
    def _get_module_name(self, test) -> str:
        """获取测试模块名"""
        return test.__class__.__module__
    
    def _print_status(self, test, status: str, status_icon: str):
        """打印测试状态"""
        self.current_test += 1
        elapsed = time.time() - self.current_start_time
        self.test_times[str(test)] = elapsed
        
        module = self._get_module_name(test)
        if module not in self.module_results:
            self.module_results[module] = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        
        # 更新模块统计
        if status == "passed":
            self.module_results[module]["passed"] += 1
        elif status == "failed":
            self.module_results[module]["failed"] += 1
        elif status == "error":
            self.module_results[module]["errors"] += 1
        elif status == "skipped":
            self.module_results[module]["skipped"] += 1
        
        # 打印进度
        progress_bar = self._get_progress_bar()
        test_name = test._testMethodName
        test_doc = test._testMethodDoc or ""
        
        print(f"\r{progress_bar} ({self.current_test}/{self.total_tests})")
        print(f"  {status_icon} {test_name}")
        if test_doc:
            print(f"     └─ {test_doc}")
        print(f"     ⏱️  {elapsed*1000:.1f}ms")
        print()
    
    def startTest(self, test):
        super().startTest(test)
        self.current_start_time = time.time()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self._print_status(test, "passed", "✅")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._print_status(test, "failed", "❌")
    
    def addError(self, test, err):
        super().addError(test, err)
        self._print_status(test, "error", "💥")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._print_status(test, "skipped", "⏭️")


class ProgressTestRunner:
    """带进度的测试运行器"""
    
    def __init__(self):
        self.result = None
    
    def run(self, suite: unittest.TestSuite) -> ProgressTestResult:
        """运行测试套件"""
        # 计算总测试数
        total_tests = suite.countTestCases()
        
        print(f"\n📊 发现 {total_tests} 个测试用例\n")
        print("=" * 60)
        print()
        
        self.result = ProgressTestResult(total_tests)
        
        start_time = time.time()
        suite.run(self.result)
        end_time = time.time()
        
        self.result.total_time = end_time - start_time
        
        return self.result


def run_all_tests():
    """运行所有测试"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  📋 PDF-MD-TOOLS 测试套件  ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 发现并加载测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_modules = [
        'test_extractor',
        'test_converter',
        'test_app',
    ]
    
    print("📦 加载测试模块:")
    print("-" * 40)
    
    module_test_counts = {}
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            count = module_suite.countTestCases()
            module_test_counts[module_name] = count
            suite.addTests(module_suite)
            print(f"  ✅ {module_name}: {count} 个测试")
        except ImportError as e:
            print(f"  ❌ {module_name}: 加载失败 - {e}")
    
    print("-" * 40)
    print(f"  📊 总计: {suite.countTestCases()} 个测试")
    print()
    
    # 运行测试
    print("🧪 开始运行测试...")
    print("=" * 60)
    
    runner = ProgressTestRunner()
    result = runner.run(suite)
    
    # 打印模块统计
    print("=" * 60)
    print("\n📈 模块统计:")
    print("-" * 60)
    print(f"{'模块名':<25} {'通过':>8} {'失败':>8} {'错误':>8} {'跳过':>8}")
    print("-" * 60)
    
    for module, stats in result.module_results.items():
        module_short = module.replace("test_", "")
        status_icon = "✅" if stats["failed"] == 0 and stats["errors"] == 0 else "❌"
        print(f"{status_icon} {module_short:<22} {stats['passed']:>8} {stats['failed']:>8} {stats['errors']:>8} {stats['skipped']:>8}")
    
    print("-" * 60)
    
    # 打印总结
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  📊 测试结果总结  ".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failures - errors - skipped
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"║  总计测试: {total:<10}                                  ║")
    print(f"║  ✅ 通过:  {passed:<10} ({pass_rate:.1f}%)                        ║")
    print(f"║  ❌ 失败:  {failures:<10}                                  ║")
    print(f"║  💥 错误:  {errors:<10}                                  ║")
    print(f"║  ⏭️ 跳过:  {skipped:<10}                                  ║")
    print(f"║  ⏱️ 耗时:  {result.total_time:.2f} 秒                                ║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 显示失败和错误详情
    if failures > 0:
        print("❌ 失败的测试详情:")
        print("-" * 60)
        for test, traceback in result.failures:
            print(f"  🔴 {test}")
            print(f"     {traceback[:200]}...")
        print()
    
    if errors > 0:
        print("💥 出错的测试详情:")
        print("-" * 60)
        for test, traceback in result.errors:
            print(f"  🔴 {test}")
            print(f"     {traceback[:200]}...")
        print()
    
    # 最终结果
    if result.wasSuccessful():
        print("╔" + "═" * 58 + "╗")
        print("║" + "  🎉 所有测试通过！  ".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        return 0
    else:
        print("╔" + "═" * 58 + "╗")
        print("║" + "  ⚠️ 存在测试失败或错误  ".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
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
