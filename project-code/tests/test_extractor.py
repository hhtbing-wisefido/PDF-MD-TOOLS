"""
📖 PDF解析模块测试

测试 pdf_parser.extractor 模块的功能
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_parser.extractor import (
    _parse_text_blocks,
    _detect_block_type,
    _is_page_number,
    ExtractedImage,
    PageContent,
    PDFContent,
)


class TestPageNumberDetection(unittest.TestCase):
    """页码检测测试"""
    
    def test_pure_number_is_page_number(self):
        """纯数字应识别为页码"""
        self.assertTrue(_is_page_number("1"))
        self.assertTrue(_is_page_number("42"))
        self.assertTrue(_is_page_number("100"))
        self.assertTrue(_is_page_number("999"))
    
    def test_long_number_is_not_page_number(self):
        """超过4位数字不是页码"""
        self.assertFalse(_is_page_number("12345"))
        self.assertFalse(_is_page_number("123456"))
    
    def test_chinese_page_format(self):
        """中文页码格式"""
        self.assertTrue(_is_page_number("第1页"))
        self.assertTrue(_is_page_number("第 10 页"))
        self.assertTrue(_is_page_number("第100页"))
    
    def test_english_page_format(self):
        """英文页码格式"""
        self.assertTrue(_is_page_number("Page 1"))
        self.assertTrue(_is_page_number("page 42"))
        self.assertTrue(_is_page_number("P. 10"))
    
    def test_fraction_page_format(self):
        """分数页码格式"""
        self.assertTrue(_is_page_number("1/10"))
        self.assertTrue(_is_page_number("5 / 20"))
    
    def test_normal_text_is_not_page_number(self):
        """普通文本不应识别为页码"""
        self.assertFalse(_is_page_number("Hello World"))
        self.assertFalse(_is_page_number("第一章 简介"))
        self.assertFalse(_is_page_number("这是一段文字"))


class TestBlockTypeDetection(unittest.TestCase):
    """文本块类型检测测试"""
    
    def test_heading1_by_font_size(self):
        """通过字体大小识别一级标题"""
        result = _detect_block_type("Introduction", font_size=20, is_bold=False)
        self.assertEqual(result, "heading1")
    
    def test_heading1_by_bold_and_size(self):
        """通过粗体和字体大小识别一级标题"""
        result = _detect_block_type("Chapter 1", font_size=14, is_bold=True)
        self.assertEqual(result, "heading1")
    
    def test_heading2_by_font_size(self):
        """通过字体大小识别二级标题"""
        result = _detect_block_type("Section 1.1", font_size=15, is_bold=False)
        self.assertEqual(result, "heading2")
    
    def test_heading3_by_bold(self):
        """通过粗体识别三级标题"""
        # font_size=12 + is_bold 会被识别为heading2，需要更小字体
        result = _detect_block_type("Subsection", font_size=11, is_bold=True)
        self.assertEqual(result, "heading3")
    
    def test_long_text_is_paragraph(self):
        """长文本应识别为段落"""
        long_text = "This is a very long paragraph that contains more than 100 characters to ensure it is not mistakenly identified as a heading."
        result = _detect_block_type(long_text, font_size=18, is_bold=True)
        self.assertEqual(result, "paragraph")
    
    def test_list_item_bullet(self):
        """项目符号列表"""
        self.assertEqual(_detect_block_type("• Item 1", 12, False), "list_item")
        self.assertEqual(_detect_block_type("· Item 2", 12, False), "list_item")
        self.assertEqual(_detect_block_type("- Item 3", 12, False), "list_item")
        self.assertEqual(_detect_block_type("* Item 4", 12, False), "list_item")
    
    def test_numbered_list(self):
        """编号列表"""
        self.assertEqual(_detect_block_type("1. First item", 12, False), "numbered_list")
        self.assertEqual(_detect_block_type("2) Second item", 12, False), "numbered_list")
    
    def test_code_block(self):
        """代码块（等宽字体）"""
        result = _detect_block_type("def hello():\n    print('world')", 10, False, is_mono=True)
        self.assertEqual(result, "code_block")
    
    def test_blockquote(self):
        """引用块"""
        self.assertEqual(_detect_block_type("> This is a quote", 12, False), "blockquote")
        self.assertEqual(_detect_block_type("》引用内容", 12, False), "blockquote")
    
    def test_normal_paragraph(self):
        """普通段落"""
        result = _detect_block_type("This is normal text.", font_size=12, is_bold=False)
        self.assertEqual(result, "paragraph")


class TestTextBlockParsing(unittest.TestCase):
    """文本块解析测试"""
    
    def test_empty_dict_returns_empty_list(self):
        """空字典返回空列表"""
        result = _parse_text_blocks({})
        self.assertEqual(result, [])
    
    def test_non_text_blocks_are_filtered(self):
        """非文本块被过滤"""
        text_dict = {
            "blocks": [
                {"type": 1},  # 图片块
                {"type": 2},  # 其他类型
            ]
        }
        result = _parse_text_blocks(text_dict)
        self.assertEqual(result, [])
    
    def test_header_footer_filtered(self):
        """页眉页脚被过滤"""
        text_dict = {
            "height": 842,
            "width": 595,
            "blocks": [
                # 页眉区域（顶部5%以内）
                {
                    "type": 0,
                    "bbox": [0, 10, 100, 30],  # y=10 < 42.1
                    "lines": [{"spans": [{"text": "Header", "size": 10, "font": "Arial"}]}]
                },
                # 正文区域
                {
                    "type": 0,
                    "bbox": [0, 100, 500, 150],  # 正常位置
                    "lines": [{"spans": [{"text": "Normal content", "size": 12, "font": "Arial"}]}]
                },
                # 页脚区域（底部8%以外）
                {
                    "type": 0,
                    "bbox": [0, 800, 100, 830],  # y=830 > 775
                    "lines": [{"spans": [{"text": "Footer", "size": 10, "font": "Arial"}]}]
                },
            ]
        }
        result = _parse_text_blocks(text_dict)
        
        # 只应保留正文
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["content"], "Normal content")
    
    def test_page_number_filtered(self):
        """页码被过滤"""
        text_dict = {
            "height": 842,
            "width": 595,
            "blocks": [
                {
                    "type": 0,
                    "bbox": [0, 400, 50, 420],  # 中间位置
                    "lines": [{"spans": [{"text": "42", "size": 10, "font": "Arial"}]}]
                },
            ]
        }
        result = _parse_text_blocks(text_dict)
        
        # 页码应被过滤
        self.assertEqual(len(result), 0)
    
    def test_blocks_sorted_by_reading_order(self):
        """文本块按阅读顺序排序"""
        text_dict = {
            "height": 842,
            "width": 595,
            "blocks": [
                # 右栏
                {
                    "type": 0,
                    "bbox": [300, 100, 500, 150],
                    "lines": [{"spans": [{"text": "Right column", "size": 12, "font": "Arial"}]}]
                },
                # 左栏（应该先读）
                {
                    "type": 0,
                    "bbox": [50, 100, 250, 150],
                    "lines": [{"spans": [{"text": "Left column", "size": 12, "font": "Arial"}]}]
                },
            ]
        }
        result = _parse_text_blocks(text_dict)
        
        # 左栏应该在右栏之前
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"], "Left column")
        self.assertEqual(result[1]["content"], "Right column")


class TestDataClasses(unittest.TestCase):
    """数据类测试"""
    
    def test_extracted_image_filename(self):
        """测试图片文件名生成"""
        img = ExtractedImage(
            image_data=b"dummy",
            image_ext="png",
            page_num=1,
            image_index=2,
            width=100,
            height=200
        )
        filename = img.get_filename("document")
        self.assertEqual(filename, "document_p1_img2.png")
    
    def test_page_content_defaults(self):
        """测试页面内容默认值"""
        page = PageContent(page_num=1)
        self.assertEqual(page.page_num, 1)
        self.assertEqual(page.text_blocks, [])
        self.assertEqual(page.images, [])
        self.assertFalse(page.has_complex_graphics)
        self.assertIsNone(page.page_image)
    
    def test_pdf_content_defaults(self):
        """测试PDF内容默认值"""
        content = PDFContent()
        self.assertEqual(content.pages, [])
        self.assertEqual(content.metadata, {})
        self.assertEqual(content.total_images, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
