"""
🔄 Markdown转换模块测试

测试 md_generator.converter 模块的功能
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_generator.converter import (
    _convert_text_block,
    _convert_list_items,
    _convert_numbered_list,
    _convert_code_block,
    _convert_blockquote,
    _convert_paragraph,
    _clean_content,
    _get_first_line,
    convert_to_markdown,
)
from pdf_parser.extractor import PDFContent, PageContent


class TestTextBlockConversion(unittest.TestCase):
    """文本块转换测试"""
    
    def test_heading1_conversion(self):
        """一级标题转换"""
        block = {"type": "heading1", "content": "Introduction"}
        result = _convert_text_block(block)
        self.assertEqual(result, "## Introduction")
    
    def test_heading2_conversion(self):
        """二级标题转换"""
        block = {"type": "heading2", "content": "Section 1.1"}
        result = _convert_text_block(block)
        self.assertEqual(result, "### Section 1.1")
    
    def test_heading3_conversion(self):
        """三级标题转换"""
        block = {"type": "heading3", "content": "Subsection"}
        result = _convert_text_block(block)
        self.assertEqual(result, "#### Subsection")
    
    def test_paragraph_conversion(self):
        """段落转换"""
        block = {"type": "paragraph", "content": "This is a paragraph."}
        result = _convert_text_block(block)
        self.assertEqual(result, "This is a paragraph.")
    
    def test_empty_content_returns_empty(self):
        """空内容返回空字符串"""
        block = {"type": "paragraph", "content": ""}
        result = _convert_text_block(block)
        self.assertEqual(result, "")
    
    def test_whitespace_only_returns_empty(self):
        """纯空白内容返回空字符串"""
        block = {"type": "paragraph", "content": "   \n\t  "}
        result = _convert_text_block(block)
        self.assertEqual(result, "")


class TestListConversion(unittest.TestCase):
    """列表转换测试"""
    
    def test_bullet_list_conversion(self):
        """项目符号列表转换"""
        content = "• Item 1\n• Item 2\n• Item 3"
        result = _convert_list_items(content)
        expected = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(result, expected)
    
    def test_various_bullet_symbols(self):
        """各种项目符号"""
        content = "· First\n- Second\n* Third\n● Fourth"
        result = _convert_list_items(content)
        lines = result.split("\n")
        for line in lines:
            self.assertTrue(line.startswith("- "))
    
    def test_numbered_list_conversion(self):
        """编号列表转换"""
        content = "1. First\n2. Second\n3. Third"
        result = _convert_numbered_list(content)
        expected = "1. First\n2. Second\n3. Third"
        self.assertEqual(result, expected)
    
    def test_numbered_list_renumbering(self):
        """编号列表重新编号"""
        content = "5. Fifth item\n10. Tenth item"
        result = _convert_numbered_list(content)
        # 应该重新从1开始编号
        self.assertTrue(result.startswith("1."))
    
    def test_empty_lines_in_list_filtered(self):
        """列表中的空行被过滤"""
        content = "• Item 1\n\n• Item 2"
        result = _convert_list_items(content)
        lines = [l for l in result.split("\n") if l.strip()]
        self.assertEqual(len(lines), 2)


class TestCodeBlockConversion(unittest.TestCase):
    """代码块转换测试"""
    
    def test_simple_code_block(self):
        """简单代码块"""
        content = "print('hello')"
        result = _convert_code_block(content)
        self.assertEqual(result, "```\nprint('hello')\n```")
    
    def test_multiline_code_block(self):
        """多行代码块"""
        content = "def hello():\n    print('world')"
        result = _convert_code_block(content)
        self.assertIn("```\n", result)
        self.assertIn("\n```", result)
        self.assertIn("def hello():", result)


class TestBlockquoteConversion(unittest.TestCase):
    """引用块转换测试"""
    
    def test_simple_blockquote(self):
        """简单引用"""
        content = "> This is a quote"
        result = _convert_blockquote(content)
        self.assertEqual(result, "> This is a quote")
    
    def test_chinese_blockquote(self):
        """中文引用符号"""
        content = "》这是引用内容"
        result = _convert_blockquote(content)
        self.assertEqual(result, "> 这是引用内容")
    
    def test_multiline_blockquote(self):
        """多行引用"""
        content = "> Line 1\n> Line 2"
        result = _convert_blockquote(content)
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)
        for line in lines:
            self.assertTrue(line.startswith("> "))


class TestParagraphConversion(unittest.TestCase):
    """段落转换测试"""
    
    def test_simple_paragraph(self):
        """简单段落"""
        content = "This is a simple paragraph."
        result = _convert_paragraph(content)
        self.assertEqual(result, content)
    
    def test_superscript_conversion(self):
        """上标转换"""
        content = "x^2 + y^2 = z^2"
        result = _convert_paragraph(content)
        self.assertIn("$^{2}$", result)
    
    def test_subscript_conversion(self):
        """下标转换"""
        content = "H_2O"
        result = _convert_paragraph(content)
        self.assertIn("$_{2}$", result)


class TestContentCleaning(unittest.TestCase):
    """内容清理测试"""
    
    def test_remove_multiple_empty_lines(self):
        """移除多余空行"""
        content = "Line 1\n\n\n\nLine 2"
        result = _clean_content(content)
        # 多个空行应该合并为一个
        self.assertNotIn("\n\n\n", result)
    
    def test_preserve_single_empty_line(self):
        """保留单个空行"""
        content = "Line 1\n\nLine 2"
        result = _clean_content(content)
        self.assertIn("\n\n", result) or self.assertIn("\n", result)
    
    def test_strip_trailing_whitespace(self):
        """去除行尾空白"""
        content = "Line 1   \nLine 2  "
        result = _clean_content(content)
        lines = result.split("\n")
        for line in lines:
            self.assertEqual(line, line.rstrip())


class TestGetFirstLine(unittest.TestCase):
    """获取第一行测试"""
    
    def test_single_line(self):
        """单行文本"""
        result = _get_first_line("Hello World")
        self.assertEqual(result, "Hello World")
    
    def test_multiple_lines(self):
        """多行文本"""
        result = _get_first_line("First Line\nSecond Line\nThird Line")
        self.assertEqual(result, "First Line")
    
    def test_empty_string(self):
        """空字符串"""
        result = _get_first_line("")
        self.assertEqual(result, "")
    
    def test_whitespace_stripped(self):
        """空白被去除"""
        result = _get_first_line("  Trimmed  \nSecond")
        self.assertEqual(result, "Trimmed")


class TestFullMarkdownConversion(unittest.TestCase):
    """完整Markdown转换测试"""
    
    def test_basic_conversion(self):
        """基本转换"""
        pdf_content = PDFContent(
            pages=[
                PageContent(
                    page_num=1,
                    text_blocks=[
                        {"type": "heading1", "content": "Title"},
                        {"type": "paragraph", "content": "Some text."},
                    ]
                )
            ],
            metadata={
                "title": "Test Document",
                "author": "Test Author",
                "page_count": 1,
            },
            total_images=0
        )
        
        pdf_path = Path("test.pdf")
        result = convert_to_markdown(pdf_content, pdf_path, "images")
        
        # 检查基本结构
        self.assertIn("# Test Document", result)
        self.assertIn("**源文件名**", result)
        self.assertIn("test.pdf", result)
        self.assertIn("## Title", result)
        self.assertIn("Some text.", result)
    
    def test_metadata_included(self):
        """元数据包含在输出中"""
        pdf_content = PDFContent(
            pages=[],
            metadata={
                "title": "My Document",
                "author": "John Doe",
                "page_count": 5,
            },
            total_images=3
        )
        
        pdf_path = Path("document.pdf")
        result = convert_to_markdown(pdf_content, pdf_path, "images")
        
        self.assertIn("John Doe", result)
        self.assertIn("5", result)
        self.assertIn("3", result)  # 图片数量


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_document_conversion(self):
        """完整文档转换"""
        pdf_content = PDFContent(
            pages=[
                PageContent(
                    page_num=1,
                    text_blocks=[
                        {"type": "heading1", "content": "Introduction"},
                        {"type": "paragraph", "content": "Welcome to this document."},
                        {"type": "list_item", "content": "• Point 1\n• Point 2"},
                    ]
                ),
                PageContent(
                    page_num=2,
                    text_blocks=[
                        {"type": "heading2", "content": "Details"},
                        {"type": "code_block", "content": "print('hello')"},
                        {"type": "blockquote", "content": "> Important note"},
                    ]
                ),
            ],
            metadata={
                "title": "Complete Document",
                "author": "Author",
                "page_count": 2,
            },
            total_images=0
        )
        
        pdf_path = Path("complete.pdf")
        result = convert_to_markdown(pdf_content, pdf_path, "images")
        
        # 检查所有元素都被转换
        self.assertIn("## Introduction", result)
        self.assertIn("Welcome to this document.", result)
        self.assertIn("- Point 1", result)
        self.assertIn("### Details", result)
        self.assertIn("```", result)
        self.assertIn("> Important note", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
