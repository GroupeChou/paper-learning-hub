#!/usr/bin/env python3
"""
简单直接：在有资产的论文的 ## 摘要 之后注入 ## 图表资源 画廊区。
不替换标题，不碰正文，只加画廊。
"""
import re
from pathlib import Path

PROJECT = Path(__file__).parent.parent
ZH_DIR = PROJECT / "papers" / "zh"

for d in sorted(ZH_DIR.iterdir()):
    md_file = d / "paper_zh.md"
    assets_dir = d / "assets"
    
    if not md_file.exists():
        continue
    if not assets_dir.exists():
        continue
    
    asset_files = sorted(assets_dir.iterdir())
    if not asset_files:
        continue
    
    content = md_file.read_text(encoding="utf-8")
    
    # Already has gallery?
    if "## 图表资源" in content:
        continue
    
    # Build gallery
    gallery_lines = ["## 图表资源\n"]
    for af in asset_files:
        gallery_lines.append(f"- ![](assets/{af.name})")
    gallery = "\n".join(gallery_lines) + "\n\n"
    
    # Find insertion point: after ## 摘要 section
    m = re.search(r'(## 摘要\n\n.*?)(?=\n## |\n---|\n\n---|\Z)', content, re.DOTALL)
    if m:
        after_summary = m.end()
        content = content[:after_summary] + "\n" + gallery + content[after_summary:]
    else:
        # Fallback: after first # title
        m2 = re.search(r'^# .*?\n\n', content, re.MULTILINE)
        if m2:
            after_title = m2.end()
            content = content[:after_title] + gallery + content[after_title:]
        else:
            content = gallery + content
    
    md_file.write_text(content, encoding="utf-8")
    print(f"  ✅ {d.name}: injected gallery ({len(asset_files)} images)")

print("\nDone!")
