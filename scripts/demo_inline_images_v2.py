"""
演示：对单篇论文注入内联图片 v2

策略：扫描 PDF 原文中的 section 标题，建立 page→section 映射，
然后将每页的图片嵌入到对应翻译 section 的正文中。
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from paper_learning_hub.parser import parse_document

PID = "2604.24715v1"
ZH_DIR = Path(f"papers/zh/{PID}")
RAW_PATH = Path(f"papers/raw/{PID}/paper.pdf")
MD_PATH = ZH_DIR / "paper_zh.md"
ASSETS_DIR = ZH_DIR / "assets"


# ── Step 1: PDF 全文本 → 找 section 边界 ──
print("=" * 60)
print(f"Step 1: Scanning PDF section boundaries for {PID}")

doc_text = RAW_PATH.read_bytes()
import fitz
doc = fitz.open(RAW_PATH)

# 从 PDF 提取全部文本，按页存储
page_texts = {}
for pn in range(len(doc)):
    page = doc[pn]
    page_texts[pn + 1] = page.get_text("text")

# 识别 PDF 中的 section 标题（数字 + 关键词）
# 常见的 section 模式： "1 Introduction", "2 Related Work", "3 Methodology", etc.
section_pattern = re.compile(
    r'^(\d+)\s+([A-Z][A-Za-z\s/\-&,]+?)(?=\n\n|\Z)', re.MULTILINE
)

page_section_map = {}  # page_number → section_title
for pn, text in page_texts.items():
    for m in section_pattern.finditer(text):
        sec_num = m.group(1)
        sec_title = m.group(2).strip()
        # Map common English titles to Chinese
        title_map = {
            "Introduction": "1 引言（Introduction）",
            "Related Work": "2 相关工作（Related Work）",
            "Methodology": "3 方法论（Methodology）",
            "Method": "3 方法论（Methodology）",
            "Experiments": "4 实验与结果（Experiments and Results）",
            "Experimental Results": "4 实验与结果（Experiments and Results）",
            "Experimental": "4 实验与结果（Experiments and Results）",
            "Conclusion": "5 结论（Conclusion）",
            "Discussion": "5 结论（Conclusion）",
        }
        for eng, cn in title_map.items():
            if eng.lower() in sec_title.lower():
                page_section_map[pn] = cn
                print(f"  Page {pn}: Section \"{sec_num} {sec_title}\" → \"{cn}\"")
                break

# Also check for Appendix
for pn, text in page_texts.items():
    if pn not in page_section_map:
        if re.search(r'\bAppendix\s+[A-Z]\b', text, re.IGNORECASE):
            # Find which appendix
            m = re.search(r'Appendix\s+([A-Z])', text, re.IGNORECASE)
            appendix = m.group(1) if m else "A"
            page_section_map[pn] = f"附录 {appendix}"
            print(f"  Page {pn}: Appendix → \"附录 {appendix}\"")

print(f"\n  Total pages mapped to sections: {len(page_section_map)}")


# ── Step 2: 建立 page → image 映射 ──
print("\n" + "=" * 60)
print("Step 2: Building page→image mapping")

parsed = parse_document(RAW_PATH, ZH_DIR, max_chars=5000, max_images=100)

page_to_images = {}  # page_number → [asset_rel_paths]
for page_num, img_paths in parsed.page_images.items():
    page_to_images[page_num] = [f"assets/{Path(p).name}" for p in img_paths]
    print(f"  Page {page_num}: {len(page_to_images[page_num])} image(s)")

print(f"  Total images: {len(parsed.image_paths)}")


# ── Step 3: 构建 section → images 映射 ──
print("\n" + "=" * 60)
print("Step 3: Building section→images mapping")

# 对每个有图片的 page，找到它的 section
# 如果 page 没有直接的 section 标记，用最近的前一个有 section 标记的 page
section_to_images = {}  # section_heading → [asset_rel_paths]

# Sort pages and propagate section labels
sorted_pages = sorted(page_to_images.keys())
current_section = None

for pn in sorted_pages:
    if pn in page_section_map:
        current_section = page_section_map[pn]
    
    if current_section and pn in page_to_images:
        if current_section not in section_to_images:
            section_to_images[current_section] = []
        for img in page_to_images[pn]:
            if img not in section_to_images[current_section]:
                section_to_images[current_section].append(img)

for sec, imgs in section_to_images.items():
    print(f"  {sec}: {len(imgs)} image(s)")
    for img in imgs:
        print(f"    → {img}")


# ── Step 4: 读翻译正文，找到每个 section 的位置 ──
print("\n" + "=" * 60)
print("Step 4: Finding section positions in translation")

md_content = MD_PATH.read_text()

section_positions = []
for m in re.finditer(r'^## (.+)$', md_content, re.MULTILINE):
    section_positions.append({
        "heading": m.group(1).strip(),
        "start": m.start(),
        "end": m.end(),
    })

# 确定每个 section 的范围
for i, sec in enumerate(section_positions):
    if i + 1 < len(section_positions):
        sec["end_pos"] = section_positions[i + 1]["start"]
    else:
        sec["end_pos"] = len(md_content)
    print(f"  Section \"{sec['heading']}\" @{sec['start']}-{sec['end_pos']}")


# ── Step 5: 注入图片 ──
print("\n" + "=" * 60)
print("Step 5: Injecting images")

new_content = md_content
insertions = 0

for target_section, images in section_to_images.items():
    # 找到翻译中对应的 section
    found = False
    for sec in section_positions:
        # 匹配 section heading（考虑中英文变体）
        if target_section in sec["heading"] or sec["heading"] in target_section:
            found = True
            
            # 找到 section 正文的第一行（heading 之后第一个非空行）
            body_after = md_content[sec["end"]:sec["end_pos"]]
            first_content = re.search(r'^\s*\S', body_after, re.MULTILINE)
            
            if first_content:
                insert_pos = sec["end"] + first_content.start()
                
                # 构建图片块（带说明文字）
                img_lines = []
                for img in images:
                    # 从文件名推断描述
                    img_lines.append(f'![论文原图]({img})')
                
                img_block = "\n\n" + "\n\n".join(img_lines) + "\n\n"
                
                # 检查是否已注入
                already_has = all(
                    img in new_content[max(0, insert_pos - 200):insert_pos + len(img_block) + 500]
                    for img in images
                )
                if not already_has:
                    new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
                    print(f"  ✅ Injected {len(images)} image(s) into \"{sec['heading']}\"")
                    # 调整后续 section 的位置（内容变长了）
                    offset = len(img_block)
                    for later_sec in section_positions:
                        if later_sec["start"] > insert_pos:
                            later_sec["start"] += offset
                            later_sec["end"] += offset
                            later_sec["end_pos"] += offset
                    insertions += 1
                else:
                    print(f"  ⏭️  Already injected into \"{sec['heading']}\"")
            break
    
    if not found:
        print(f"  ❌ Section \"{target_section}\" not found in translation")


# ── Step 6: 校验 ──
print("\n" + "=" * 60)
print("Step 6: Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)

# 区分 gallery 和 inline
gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    # gallery 结束于下一个 h2 之前
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    if next_h2 < 0:
        next_h2 = len(new_content)
    gallery_section = new_content[gallery_start:next_h2]
    gallery_refs = re.findall(r'!\[', gallery_section)
    in_gallery = len(gallery_refs)
else:
    in_gallery = 0

# 校验所有 asset 文件路径都存在
assets_exist = {}
for ref in final_refs:
    rel_path = ref.replace("assets/", "")
    f = ASSETS_DIR / rel_path
    assets_exist[ref] = f.exists()

all_exist = all(assets_exist.values())
broken = sum(1 for v in assets_exist.values() if not v)

print(f"  Total image refs: {len(final_refs)}")
print(f"  Gallery refs: {in_gallery}")
print(f"  Inline refs: {len(final_refs) - in_gallery}")
print(f"  Broken refs: {broken}")
print(f"  All paths valid: {'✅' if all_exist else '❌'}")

if insertions > 0:
    # Backup
    backup_path = MD_PATH.with_suffix(".md.bak")
    if not backup_path.exists():
        MD_PATH.rename(backup_path)
        print(f"\n  Backup: {backup_path.name}")
    
    MD_PATH.write_text(new_content)
    print(f"  ✅ Written to {MD_PATH}")
    print(f"\n  Visual preview of injection:")
    print(f"  {'─' * 50}")
    for sec, imgs in section_to_images.items():
        print(f"  ## {sec}")
        for img in imgs:
            print(f"    ![]({img})")
        print()
else:
    print("  No changes made")
