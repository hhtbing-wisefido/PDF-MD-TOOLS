"""
📐 PDF布局分析器
"""

from typing import List, Dict, Any
import re


def analyze_layout(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """分析PDF布局，识别标题、段落、列表等结构"""
    blocks = []
    
    for page in pages:
        text = page.get("text", "")
        page_blocks = _analyze_page(text, page.get("page_num", 0))
        blocks.extend(page_blocks)
    
    return blocks


def _analyze_page(text: str, page_num: int) -> List[Dict[str, Any]]:
    """分析单页布局"""
    blocks = []
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        block = {
            "page": page_num,
            "content": line,
            "type": _detect_block_type(line),
        }
        blocks.append(block)
    
    return blocks


def _detect_block_type(line: str) -> str:
    """检测内容块类型"""
    if re.match(r"^第[一二三四五六七八九十\d]+[章节]", line):
        return "heading1"
    
    if re.match(r"^[\d一二三四五六七八九十]+[\.、．]", line):
        if len(line) < 50:
            return "heading2"
    
    if re.match(r"^[•●○◆◇▪▫\-\*]\s", line):
        return "list_item"
    
    if re.match(r"^\d+[\.\)）]\s", line):
        return "numbered_list"
    
    return "paragraph"
