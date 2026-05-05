#!/usr/bin/env python3
"""
精准清除翻译正文中的英文原文段落，但保留：
- 术语表格中的英文
- 参考文献引用
- LaTeX公式
- 代码块
- 图/表标题的英文描述

仅删除：连续10+英文单词且无中文字符的行，如 "[Page 1]"、"Abstract\nModel distillation..."
"""
import re
from pathlib import Path

PROJECT = Path(__file__).parent.parent
ZH_DIR = PROJECT / "papers" / "zh"

def is_clean_english_paragraph(text: str) -> bool:
    """判断一段文本是否是需要删除的纯英文原文段落"""
    stripped = text.strip()
    if not stripped:
        return False
    # 跳过空行、纯数字行、纯标点行
    if not re.search(r'[a-zA-Z]', stripped):
        return False
    # 跳过包含中文的行（中英混合通常是术语解释等有用内容）
    if re.search(r'[\u4e00-\u9fff]', stripped):
        return False
    # 跳过参考文献行 [1] [2] 等
    if re.match(r'^\[\d+\]', stripped):
        return False
    # 跳过URL
    if stripped.startswith('http') or stripped.startswith('https'):
        return False
    # 跳过单行术语/短句（如 "Figure 1", "Table 2", "Abstract"）
    words = stripped.split()
    if len(words) < 8:  # 少于8个单词的英文行保留（可能是术语标记）
        return False
    # 跳过代码行（包含 = -> () {} ; 等）
    if re.search(r'[=(){};\[\]]', stripped):
        return False
    # 跳过以数字+点开头的列表行
    if re.match(r'^\d+\.\s', stripped):
        return False
    # 跳过Page标记
    if re.match(r'^\[Page \d+\]', stripped):
        return True  # 删除Page标记
    # 计算英文比例
    alpha = sum(1 for c in stripped if c.isalpha())
    total_alpha = sum(1 for c in stripped if c.isalpha() or c.isspace())
    if total_alpha == 0:
        return False
    ratio = alpha / (len(stripped) + 1)
    # 纯英文段落（>70%英文字母且多行）：删除
    if ratio > 0.65 and len(words) >= 10:
        return True
    return False

papers_cleaned = 0
total_lines_removed = 0

for d in sorted(ZH_DIR.iterdir()):
    md_file = d / "paper_zh.md"
    if not md_file.exists():
        continue
    
    content = md_file.read_text(encoding="utf-8")
    lines = content.split('\n')
    
    # Find body start (after gallery or after --- separator)
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 10:  # separator between header and body
            body_start = i + 1
            break
    
    if body_start == 0:
        continue
    
    # Only clean the body section
    body_lines = lines[body_start:]
    header_lines = lines[:body_start]
    
    cleaned_body = []
    removed_count = 0
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        stripped = line.strip()
        
        # Skip pure English paragraphs
        if is_clean_english_paragraph(stripped):
            removed_count += 1
            i += 1
            continue
        
        # Handle [Page N] markers
        if re.match(r'^\[Page \d+\]$', stripped):
            removed_count += 1
            i += 1
            continue
        
        # Handle consecutive English paragraphs (multi-line)
        if stripped and not re.search(r'[\u4e00-\u9fff]', stripped):
            # Check if this and the next several lines form an English paragraph
            j = i
            para_lines = []
            while j < len(body_lines):
                ls = body_lines[j].strip()
                if not ls:
                    break
                if re.search(r'[\u4e00-\u9fff]', ls):
                    break
                if re.match(r'^\[Page \d+\]$', ls):
                    j += 1
                    continue
                para_lines.append(ls)
                j += 1
            
            para_text = ' '.join(para_lines)
            words = para_text.split()
            alpha = sum(1 for c in para_text if c.isalpha())
            ratio = alpha / (len(para_text) + 1) if para_text else 0
            
            if len(words) >= 15 and ratio > 0.6:
                # Remove the entire English paragraph
                removed_count += j - i
                i = j
                continue
        
        cleaned_body.append(line)
        i += 1
    
    if removed_count > 0:
        new_content = '\n'.join(header_lines + cleaned_body)
        md_file.write_text(new_content, encoding="utf-8")
        papers_cleaned += 1
        total_lines_removed += removed_count
        new_size = md_file.stat().st_size / 1024
        print(f"  ✅ {d.name}: removed {removed_count} English line(s) → {new_size:.0f}KB")

print(f"\nDone. Cleaned {papers_cleaned} papers, removed {total_lines_removed} English lines total.")
