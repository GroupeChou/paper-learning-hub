#!/usr/bin/env python3
"""
精确修复：为有资产但无画廊的文章注入图表资源画廊
并清理编造的图片引用
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

# Papers to fix: have assets but no gallery, or have broken refs
fix_targets = [
    "2604.14858v1",  # 2 assets, no gallery
    "2604.15725v1",  # 19 assets, no gallery 
    "2604.19144v1",  # 7 assets, no gallery
    "2604.21003v1",  # 2 assets, no gallery
    "2604.24512v1",  # 8 assets, no gallery
    "2604.26102v1",  # 2 assets, no gallery
    "2604.12102v2",  # 0 assets, has broken ref
    "2604.17111v1",  # 0 assets, has broken refs
    "2604.18234v1",  # 0 assets, has broken ref
    "2604.23449v1",  # 0 assets, has broken ref
    "2604.20090v1",  # has gallery + 8 extra broken refs
]

for pid in fix_targets:
    md_file = ZH_DIR / pid / "paper_zh.md"
    assets_dir = ZH_DIR / pid / "assets"
    
    if not md_file.exists():
        print(f"  SKIP {pid}: no md file")
        continue
    
    current = md_file.read_text(encoding="utf-8")
    n_assets = len(list(assets_dir.iterdir())) if assets_dir.exists() else 0
    has_gallery = "## 图表资源" in current
    
    # Count existing ![] refs
    existing_refs = re.findall(r'!\[.*?\]\((.*?)\)', current)
    valid_local_refs = []
    broken_local_refs = []
    for ref in existing_refs:
        if ref.startswith('assets/'):
            fpath = ZH_DIR / pid / ref
            if fpath.exists():
                valid_local_refs.append(ref)
            else:
                broken_local_refs.append(ref)
    
    # Step 1: Generate gallery section if assets exist
    gallery_section = ""
    if n_assets > 0 and not has_gallery:
        # Find the actual asset files
        asset_files = sorted(assets_dir.iterdir())
        lines = ["## 图表资源\n"]
        for af in asset_files:
            rel = f"assets/{af.name}"
            lines.append(f"- ![]({rel})")
        gallery_section = "\n".join(lines) + "\n\n"
        print(f"  📷 {pid}: {n_assets} assets → gallery generated")
    
    # Step 2: Remove broken hallucinated refs
    new_content = current
    if broken_local_refs:
        for ref in broken_local_refs:
            # Remove the entire ![]() line (including following optional caption line)
            pattern = re.escape(f"![]{ref}") + r'\n[^\n]*'
            new_content = re.sub(pattern, '', new_content)
        print(f"  🗑️ {pid}: removed {len(broken_local_refs)} broken ref(s): {broken_local_refs}")
    
    # Step 3: Inject gallery section after ## 摘要
    if gallery_section:
        # Find ## 摘要 section end
        m = re.search(r'(## 摘要\n\n.*?)(?=\n## |\n\n---|\n\n$|\Z)', new_content, re.DOTALL)
        if m:
            after_summary = m.end()
            new_content = new_content[:after_summary] + "\n\n" + gallery_section + new_content[after_summary:]
        else:
            # Fallback: insert after first heading
            m2 = re.search(r'^# .*?\n\n', new_content, re.MULTILINE)
            if m2:
                after_title = m2.end()
                new_content = new_content[:after_title] + gallery_section + new_content[after_title:]
            else:
                new_content = gallery_section + "\n" + new_content
    
    # Step 4: Write back
    if new_content != current:
        md_file.write_text(new_content, encoding="utf-8")
        print(f"  ✅ {pid}: written ({len(new_content)/1024:.0f}KB)")
    else:
        print(f"  — {pid}: no changes needed")

print("\nDone! Checking results:")
for pid in fix_targets:
    md_file = ZH_DIR / pid / "paper_zh.md"
    if not md_file.exists():
        continue
    content = md_file.read_text(encoding="utf-8")
    has_g = "## 图表资源" in content
    refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
    broken = [r for r in refs if r.startswith('assets/') and not (ZH_DIR / pid / r).exists()]
    n_assets = len(list((ZH_DIR / pid / "assets").iterdir())) if (ZH_DIR / pid / "assets").exists() else 0
    flag = "✅" if (has_g and n_assets > 0) or (n_assets == 0 and len(broken) == 0) else "⚠️"
    print(f"  {flag} {pid}: gallery={has_g}, refs={len(refs)}, broken={len(broken)}, assets={n_assets}")
