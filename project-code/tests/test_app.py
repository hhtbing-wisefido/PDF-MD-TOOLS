"""
📱 应用逻辑测试

测试 app.py 模块的核心逻辑（不涉及GUI）
"""

import sys
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入版本信息
from app import APP_VERSION, APP_BUILD_DATE

# 导入进程检查函数
from app import (
    check_existing_process,
    kill_existing_process,
    create_lock_file,
    remove_lock_file,
    LOCK_FILE,
)

# 导入数据类
from app import FileItem, ConversionState, ConvertStatus


class TestVersionInfo(unittest.TestCase):
    """版本信息测试"""
    
    def test_version_format(self):
        """版本号格式正确"""
        # 版本号应该是 x.y.z 格式
        parts = APP_VERSION.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())
    
    def test_build_date_format(self):
        """构建日期格式正确"""
        # 日期应该是 YYYY-MM-DD 格式
        parts = APP_BUILD_DATE.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[0]), 4)  # 年
        self.assertEqual(len(parts[1]), 2)  # 月
        self.assertEqual(len(parts[2]), 2)  # 日


class TestFileItem(unittest.TestCase):
    """FileItem数据类测试"""
    
    def test_file_item_creation(self):
        """创建FileItem"""
        item = FileItem(
            pdf_path=Path("test.pdf"),
            pdf_name="test.pdf",
            md_name="test.md",
            size=1024
        )
        self.assertEqual(item.pdf_name, "test.pdf")
        self.assertEqual(item.md_name, "test.md")
        self.assertEqual(item.size, 1024)
        self.assertEqual(item.status, ConvertStatus.PENDING)
        self.assertEqual(item.progress, 0)
    
    def test_file_item_hash(self):
        """FileItem哈希生成"""
        item = FileItem(
            pdf_path=Path("test.pdf"),
            pdf_name="test.pdf",
            md_name="test.md",
            size=1024
        )
        hash1 = item.get_hash()
        
        # 哈希应该是16字符
        self.assertEqual(len(hash1), 16)
        
        # 相同文件应该产生相同哈希
        item2 = FileItem(
            pdf_path=Path("test.pdf"),
            pdf_name="test.pdf",
            md_name="test.md",
            size=1024
        )
        hash2 = item2.get_hash()
        self.assertEqual(hash1, hash2)
    
    def test_file_item_hash_differs_by_size(self):
        """不同大小的文件哈希不同"""
        item1 = FileItem(
            pdf_path=Path("test.pdf"),
            pdf_name="test.pdf",
            md_name="test.md",
            size=1024
        )
        item2 = FileItem(
            pdf_path=Path("test.pdf"),
            pdf_name="test.pdf",
            md_name="test.md",
            size=2048
        )
        self.assertNotEqual(item1.get_hash(), item2.get_hash())


class TestConversionState(unittest.TestCase):
    """ConversionState状态管理测试"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".conversion_state.json"
    
    def tearDown(self):
        """清理临时文件"""
        if self.state_file.exists():
            self.state_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_new_state_is_empty(self):
        """新状态文件为空"""
        state = ConversionState(self.state_file)
        self.assertEqual(state.converted, {})
    
    def test_mark_converted(self):
        """标记已转换"""
        state = ConversionState(self.state_file)
        state.mark_converted("hash123", "/path/to/output.md")
        
        self.assertTrue(state.is_converted("hash123"))
        self.assertFalse(state.is_converted("other_hash"))
    
    def test_state_persistence(self):
        """状态持久化"""
        # 创建并保存状态
        state1 = ConversionState(self.state_file)
        state1.mark_converted("hash1", "/path/1.md")
        state1.mark_converted("hash2", "/path/2.md")
        
        # 重新加载状态
        state2 = ConversionState(self.state_file)
        
        self.assertTrue(state2.is_converted("hash1"))
        self.assertTrue(state2.is_converted("hash2"))
        self.assertFalse(state2.is_converted("hash3"))
    
    def test_state_file_format(self):
        """状态文件格式"""
        state = ConversionState(self.state_file)
        state.mark_converted("test_hash", "/output/test.md")
        
        # 读取文件内容
        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("test_hash", data)
        self.assertEqual(data["test_hash"], "/output/test.md")


class TestConvertStatus(unittest.TestCase):
    """ConvertStatus枚举测试"""
    
    def test_status_values(self):
        """状态值"""
        self.assertEqual(ConvertStatus.PENDING.value, "待转换")
        self.assertEqual(ConvertStatus.CONVERTING.value, "转换中")
        self.assertEqual(ConvertStatus.COMPLETED.value, "已完成")
        self.assertEqual(ConvertStatus.ERROR.value, "错误")
        self.assertEqual(ConvertStatus.SKIPPED.value, "已跳过")
    
    def test_all_statuses_exist(self):
        """所有状态都存在"""
        statuses = list(ConvertStatus)
        self.assertEqual(len(statuses), 5)


class TestLockFile(unittest.TestCase):
    """锁文件测试"""
    
    def tearDown(self):
        """清理锁文件"""
        remove_lock_file()
    
    def test_create_lock_file(self):
        """创建锁文件"""
        remove_lock_file()  # 确保干净状态
        create_lock_file()
        self.assertTrue(LOCK_FILE.exists())
    
    def test_lock_file_contains_pid(self):
        """锁文件包含进程ID"""
        remove_lock_file()
        create_lock_file()
        
        with open(LOCK_FILE, 'r') as f:
            pid = f.read().strip()
        
        self.assertEqual(pid, str(os.getpid()))
    
    def test_remove_lock_file(self):
        """删除锁文件"""
        create_lock_file()
        self.assertTrue(LOCK_FILE.exists())
        
        remove_lock_file()
        self.assertFalse(LOCK_FILE.exists())
    
    def test_remove_nonexistent_lock_file(self):
        """删除不存在的锁文件不报错"""
        remove_lock_file()  # 确保不存在
        remove_lock_file()  # 再次删除不应报错


class TestProcessCheck(unittest.TestCase):
    """进程检查测试"""
    
    def tearDown(self):
        """清理"""
        remove_lock_file()
    
    def test_no_existing_process_when_no_lock(self):
        """无锁文件时无老进程"""
        remove_lock_file()
        result = check_existing_process()
        self.assertFalse(result)
    
    def test_check_with_invalid_pid(self):
        """无效PID时返回False"""
        # 创建包含无效PID的锁文件
        with open(LOCK_FILE, 'w') as f:
            f.write("99999999")  # 不太可能存在的PID
        
        result = check_existing_process()
        # 应该返回False（进程不存在）
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
