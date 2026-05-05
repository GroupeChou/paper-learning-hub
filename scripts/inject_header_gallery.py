#!/usr/bin/env python3
"""
批量修复所有已翻译论文：注入 _paper_header() 生成的完整头部（含图表资源画廊）
同时保留原有的翻译内容（移除旧头部）。
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.parser import parse_document
from paper_learning_hub.translator import _paper_header

PROJECT = Path(__file__).parent.parent
ZH_DIR = PROJECT / "papers" / "zh"
RAW_DIR = PROJECT / "papers" / "raw"

paper_dirs = sorted(ZH_DIR.iterdir())
fix_count = 0

for d in paper_dirs:
    pid = d.name
    md_file = d / "paper_zh.md"
    if not md_file.exists():
        continue
    
    # Find PDF
    raw_pdf = RAW_DIR / pid / "paper.pdf"
    if not raw_pdf.exists():
        alt = list(RAW_DIR.glob(f"{pid}/*.pdf"))
        raw_pdf = alt[0] if alt else None
    if not raw_pdf or not raw_pdf.exists():
        print(f"  SKIP {pid}: no PDF")
        continue
    
    # Read current content
    current = md_file.read_text(encoding="utf-8")
    
    # Parse document and generate header
    try:
        parsed = parse_document(raw_pdf, d, max_chars=4000, max_images=100)
        
        # Get title from paper if available
        title_display = parsed.title if parsed.title else pid
        
        dummy = CandidatePaper(
            paper_id=pid, title=title_display, organization="", publish_date="",
            theme="", source_name="", source_url="", paper_url="", summary="",
            priority=0,
        )
        header = _paper_header(dummy, parsed, d / "assets", ZH_DIR)
        
        has_gallery = "## 图表资源" in header
        n_images = len(parsed.image_paths)
        
        # Check if header already has gallery
        if "## 图表资源" in current:
            print(f"  SKIP {pid}: gallery already exists ({n_images} images)")
            continue
        
        # Find where to inject header: after "---" separator or after metadata
        # Strategy: replace everything before "## 中文翻译" or before the first chunk heading
        
        # Look for the first chunk heading pattern
        chunk_starters = [
            "## Section ", "## 逐块精读", "## 中文翻译", "### 中文翻译",
            "## 块", "---\n\n## ",
        ]
        
        insert_pos = -1
        for marker in chunk_starters:
            pos = current.find(marker)
            if pos > 0:
                insert_pos = pos
                break
        
        if insert_pos < 0:
            # Try to find first ### after abstract
            match = re.search(r'^#{2,3}\s', current, re.MULTILINE)
            if match:
                insert_pos = match.start()
        
        if insert_pos < 0:
            print(f"  ⚠️ {pid}: cannot find insertion point, prepending")
            new_content = header + "\n\n---\n\n" + current
        else:
            # Remove old header content up to insert_pos
            # But keep the title line and meta if they exist
            old_header = current[:insert_pos]
            body = current[insert_pos:]
            
            # Check if old header has a useful summary
            summary_match = re.search(r'## 摘要\n\n(.+?)(?=\n\n##|\n\n---|\n\n$)', old_header, re.DOTALL)
            old_summary = summary_match.group(1).strip() if summary_match else None
            
            if old_summary:
                # Inject old summary into header's summary placeholder
                header_with_summary = re.sub(
                    r'(## 摘要\n\n)(.+?)(?=\n\n##|\n\n$)', 
                    lambda m: m.group(1) + old_summary + "\n",
                    header, count=1, flags=re.DOTALL
                )
                new_content = header_with_summary + "\n\n---\n\n" + body
            else:
                new_content = header + "\n\n---\n\n" + body
        
        md_file.write_text(new_content, encoding="utf-8")
        new_size = md_file.stat().st_size
        fix_count += 1
        gallery_status = "gallery" if has_gallery else "no_images"
        print(f"  ✅ {pid}: injected header ({n_images} images, {gallery_status}) → {new_size/1024:.0f}KB")
        
    except Exception as e:
        import traceback
        print(f"  ❌ {pid}: {e}")
        traceback.print_exc()

print(f"\nTotal fixed: {fix_count}")
