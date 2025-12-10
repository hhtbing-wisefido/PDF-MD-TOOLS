"""
🎨 Markdown格式化器
"""

import re


def format_markdown(text: str) -> str:
    """格式化Markdown文本"""
    text = _normalize_whitespace(text)
    text = _fix_headings(text)
    text = _fix_lists(text)
    return text.strip()


def _normalize_whitespace(text: str) -> str:
    """规范化空白字符"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    return text


def _fix_headings(text: str) -> str:
    """修复标题格式"""
    text = re.sub(r'^(#+)([^\s#])', r'\1 \2', text, flags=re.MULTILINE)
    return text


def _fix_lists(text: str) -> str:
    """修复列表格式"""
    text = re.sub(r'^(\s*[-*+])([^\s])', r'\1 \2', text, flags=re.MULTILINE)
    return text
