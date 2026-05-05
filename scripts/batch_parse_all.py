#!/usr/bin/env python3
"""
批量解析所有已翻译论文的PDF，提取chunks+图片到assets/
并生成每篇论文的翻译工作清单
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from paper_learning_hub.parser import parse_document
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.translator import _paper_header

PROJECT = Path(__file__).parent.parent
ZH_DIR = PROJECT / "papers" / "zh"
RAW_DIR = PROJECT / "papers" / "raw"

paper_dirs = sorted(ZH_DIR.iterdir())
print(f"Total paper dirs: {len(paper_dirs)}")

results = []
for d in paper_dirs:
    pid = d.name
    raw_pdf = RAW_DIR / pid / "paper.pdf"
    if not raw_pdf.exists():
        alt_pdfs = list(RAW_DIR.glob(f"{pid}/*.pdf"))
        raw_pdf = alt_pdfs[0] if alt_pdfs else None
    if not raw_pdf or not raw_pdf.exists():
        print(f"  SKIP {pid}: no PDF found")
        results.append({"pid": pid, "error": "no_pdf"})
        continue

    zh_dir = ZH_DIR / pid
    try:
        print(f"  Parsing {pid} ({raw_pdf.name})...")
        parsed = parse_document(raw_pdf, zh_dir, max_chars=4000, max_images=100)

        assets_dir = zh_dir / "assets"
        asset_files = sorted(assets_dir.iterdir()) if assets_dir.exists() else []
        
        # Generate proper header with image gallery
        dummy_paper = CandidatePaper(
            paper_id=pid, title=pid, organization="", publish_date="",
            theme="", source_name="", source_url="", paper_url="", summary="",
            priority=0,
        )
        header = _paper_header(dummy_paper, parsed, zh_dir / "assets", ZH_DIR)
        has_gallery = "## 图表资源" in header

        # Save chunks info
        chunks_info = []
        for c in parsed.chunks:
            chunks_info.append({
                "index": c.index,
                "heading": c.heading,
                "page_refs": c.page_refs,
                "char_count": len(c.text),
                "text_preview": c.text[:200],
                "needs_review": c.needs_review,
            })

        info = {
            "pid": pid,
            "n_chunks": len(parsed.chunks),
            "n_images_extracted": len(parsed.image_paths),
            "n_asset_files": len(asset_files),
            "asset_files": [f.name for f in asset_files],
            "has_gallery_in_header": has_gallery,
            "chunks": chunks_info,
            "image_paths": parsed.image_paths[:10],  # first 10
            "parse_notes": parsed.notes,
        }
        results.append(info)
        print(f"  ✅ {pid}: {len(parsed.chunks)} chunks, {len(parsed.image_paths)} images, {len(asset_files)} asset files, gallery={has_gallery}")
    except Exception as e:
        import traceback
        print(f"  ❌ {pid}: {e}")
        traceback.print_exc()
        results.append({"pid": pid, "error": str(e)})

output_path = PROJECT / ".workbuddy" / "parsed_all_papers.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

ok = [r for r in results if "error" not in r]
fail = [r for r in results if "error" in r]
print(f"\nSaved to {output_path}")
print(f"Summary: OK={len(ok)}, Fail={len(fail)}")
