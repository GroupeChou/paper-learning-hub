#!/usr/bin/env python3
"""
批量翻译格式清理：不重新翻译，只做格式调整。
对已有的 paper_zh.md 进行：
1. 移除所有英文原文段落（但保留英文学术术语、文献引用）
2. 确保 _paper_header() 画廊区正确
3. 移除翻译正文中的 ![]() 引用（改为文本引用）
4. 确保每chunk格式正确
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.parser import parse_document
from paper_learning_hub.translator import _paper_header
from paper_learning_hub.utils import relative_posix

PROJECT = Path(__file__).parent.parent
ZH_DIR = PROJECT / "papers" / "zh"
RAW_DIR = PROJECT / "papers" / "raw"

def is_english_text(text: str) -> bool:
    """判断一段文本是否主要是英文（论文原文段落）"""
    if not text.strip():
        return False
    # 跳过纯数字/标点/特殊字符行
    if re.match(r'^[\d\s\-–—|:;,./()\[\]{}""''《》（）]+$', text):
        return False
    # 简短短语不处理（如 "Figure 1"、"Introduction"）
    if len(text.strip()) < 30:
        return False
    # 跳过参考文献行（包含[1][2]等）
    if re.match(r'^\[\d+\]', text.strip()):
        return False
    # 跳过已有中文的行（中英文混合的大多是术语解释等）
    if re.search(r'[\u4e00-\u9fff]', text):
        return False
    # 跳过无字母行
    if not re.search(r'[a-zA-Z]', text):
        return False
    # 计算英文字符比例
    alpha_count = sum(1 for c in text if c.isalpha())
    total_chars = len(text.strip())
    if total_chars == 0:
        return False
    ratio = alpha_count / total_chars
    return ratio > 0.6  # >60%英文字母 => 英文段落

def clean_paper(pid: str) -> dict:
    md_file = ZH_DIR / pid / "paper_zh.md"
    assets_dir = ZH_DIR / pid / "assets"
    
    if not md_file.exists():
        return {"pid": pid, "status": "no_md"}
    
    # 读取当前内容
    content = md_file.read_text(encoding="utf-8")
    original_size = len(content)
    n_assets = len(list(assets_dir.iterdir())) if assets_dir.exists() else 0
    has_gallery = "## 图表资源" in content
    
    changes = []
    
    # Step 1: 生成正确的 header（含画廊）
    raw_pdf = RAW_DIR / pid / "paper.pdf"
    if not raw_pdf.exists():
        alt = list(RAW_DIR.glob(f"{pid}/*.pdf"))
        raw_pdf = alt[0] if alt else None
    
    if raw_pdf and raw_pdf.exists():
        try:
            parsed = parse_document(raw_pdf, ZH_DIR / pid, max_chars=5000, max_images=100)
            
            if parsed.image_paths or True:  # always generate header
                dummy = CandidatePaper(
                    paper_id=pid, title="", organization="", publish_date="",
                    theme="", source_name="", source_url="", paper_url="", summary="",
                    priority=0,
                )
                new_header = _paper_header(dummy, parsed, ZH_DIR / pid / "assets", ZH_DIR)
                
                # Replace old header with new one (keep the translation body)
                # Find the first content section after the header
                section_markers = [
                    "## Section ", "## 逐块精读", "### 中文翻译", 
                    "---\n\n## ", "## 一、", "## 1.",
                ]
                
                body_start = len(content)
                for marker in section_markers:
                    pos = content.find(marker)
                    if pos > 50:  # must be after the header
                        body_start = pos
                        break
                
                if body_start > 50:
                    old_header = content[:body_start]
                    body = content[body_start:]
                    
                    # Extract old summary if exists
                    summary_match = re.search(r'## 摘要\n\n(.+?)(?=\n\n##|\n\n---|\n\n$)', old_header, re.DOTALL)
                    if summary_match:
                        old_summary = summary_match.group(1).strip()
                        # Inject into new header
                        new_header = re.sub(
                            r'(## 摘要\n\n).*?(?=\n\n##|\n\n$|\Z)',
                            lambda m: m.group(1) + old_summary + "\n",
                            new_header, count=1, flags=re.DOTALL
                        )
                    
                    # Replace old header with new
                    content = new_header + "\n\n---\n\n" + body
                    changes.append("header_regenerated")
        except Exception as e:
            changes.append(f"header_error: {e}")
    
    # Step 2: Remove English original text paragraphs from the body
    # Only process the body (after the gallery section)
    gallery_end = content.find("## 图表资源")
    if gallery_end > 0:
        # Find end of gallery
        next_section = content.find("\n## ", gallery_end + 10)
        if next_section > 0:
            body_section = content[next_section:]
        else:
            body_section = content
    else:
        body_section = content
    
    # Check for English paragraphs (within ### 中文翻译 sections)
    # Split into sections
    sections = re.split(r'(?=^#{1,3} )', body_section, flags=re.MULTILINE)
    cleaned_sections = []
    en_removed = 0
    
    for sec in sections:
        if sec.startswith("### 中文翻译") or sec.startswith("#### 中文"):
            lines = sec.split('\n')
            cleaned_lines = []
            in_code_block = False
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    cleaned_lines.append(line)
                    continue
                if in_code_block:
                    cleaned_lines.append(line)
                    continue
                # Check if line is pure English paragraph
                stripped = line.strip()
                if is_english_text(stripped):
                    en_removed += 1
                    continue
                cleaned_lines.append(line)
            cleaned_sections.append('\n'.join(cleaned_lines))
        else:
            cleaned_sections.append(sec)
    
    content = content[:gallery_end] + ''.join(cleaned_sections) if gallery_end > 0 else ''.join(cleaned_sections)
    if en_removed > 0:
        changes.append(f"removed_{en_removed}_english_paragraphs")
    
    # Step 3: Remove broken ![] references in body (keep gallery ones)
    if has_gallery:
        gallery_section = content[content.find("## 图表资源"):]
        gallery_end_pos = gallery_section.find("\n## ", 10)
        if gallery_end_pos > 0:
            gallery_only = gallery_section[:gallery_end_pos]
            body_part = content[content.find("## 图表资源") + gallery_end_pos:]
            
            # Remove all ![]() from body
            body_part = re.sub(r'!\[.*?\]\(.*?\)', '', body_part)
            
            content = content[:content.find("## 图表资源")] + gallery_only + "\n\n" + body_part
            changes.append("body_imgs_removed")
    
    # Step 4: Write back
    if len(content) != original_size or changes:
        md_file.write_text(content, encoding="utf-8")
        new_size = len(content)
        return {
            "pid": pid,
            "status": "ok",
            "changes": changes,
            "size_kb": new_size / 1024,
            "delta_kb": (new_size - original_size) / 1024,
        }
    else:
        return {"pid": pid, "status": "no_changes"}


# Process all papers
paper_dirs = sorted(ZH_DIR.iterdir())
results = []
for d in paper_dirs:
    pid = d.name
    if not (d / "paper_zh.md").exists():
        continue
    result = clean_paper(pid)
    results.append(result)
    if result["status"] == "ok":
        print(f"  ✅ {pid}: {', '.join(result['changes'])} ({result['size_kb']:.0f}KB, Δ{result['delta_kb']:+.0f}KB)")
    elif result["status"] == "no_changes":
        print(f"  — {pid}: no changes needed")

print(f"\nDone. Processed {len(results)} papers.")
ok = [r for r in results if r["status"] == "ok"]
no = [r for r in results if r["status"] == "no_changes"]
print(f"Modified: {len(ok)}, Unchanged: {len(no)}")
