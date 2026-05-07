"""
演示：对单篇论文注入内联图片

策略：
1. 重新解析 PDF，获取 chunk→page→image 映射
2. 对翻译正文中的每个 section，判断它对应哪些 PDF 页面
3. 将图片嵌入到对应 section 的正文中（首次提及图片描述的位置之后）
"""

import re
import sys
from pathlib import Path

# 加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from paper_learning_hub.parser import parse_document

PID = "2604.24715v1"
ZH_DIR = Path(f"papers/zh/{PID}")
RAW_PATH = Path(f"papers/raw/{PID}/paper.pdf")
MD_PATH = ZH_DIR / "paper_zh.md"
ASSETS_DIR = ZH_DIR / "assets"

# ── Step 1: 重新解析 PDF ──
print("=" * 60)
print(f"Step 1: Re-parsing {PID}")
parsed = parse_document(RAW_PATH, ZH_DIR, max_chars=5000, max_images=100)

# 建立 page→assets 文件名映射
page_to_assets: dict[int, list[str]] = {}
for page_num, img_paths in parsed.page_images.items():
    page_to_assets[page_num] = [Path(p).name for p in img_paths]

print(f"  Chunks: {len(parsed.chunks)}")
print(f"  Images: {len(parsed.image_paths)}")
print(f"  Pages with images: {sorted(page_to_assets.keys())}")

# ── Step 2: 构建 chunk→section 映射 ──
# 每个 chunk 有 heading（来自 PDF 原文）和 page_refs
# 翻译正文中的 section 是 ## X. 格式
# 我们用 chunk 的 PDF 原文 heading 去匹配翻译中对应的 section

md_content = MD_PATH.read_text()

# 获取翻译中所有 section 的位置（按出现顺序）
section_positions = []
for m in re.finditer(r'^## ([^#].+)$', md_content, re.MULTILINE):
    section_positions.append({
        "heading": m.group(1).strip(),
        "start": m.start(),
        "end": m.end(),
    })

# 确定每个 section 在文件中的范围（section N 到 section N+1）
for i, sec in enumerate(section_positions):
    if i + 1 < len(section_positions):
        sec["end_pos"] = section_positions[i + 1]["start"]
    else:
        sec["end_pos"] = len(md_content)

print(f"\n  Translation sections ({len(section_positions)}):")
for sec in section_positions:
    print(f"    {sec['heading']}")

# ── Step 3: 为每个有图片的 page 找到对应的 section ──
# 方法：chunk 有 page_refs 和原文 heading，我们找翻译中内容最匹配的 section

# 对每个 chunk，拿到它的 page_refs 和原文 heading 的前几个词
chunk_section_map = []  # (chunk_index, page_refs, images_to_embed, target_section_heading)
for chunk in parsed.chunks:
    images_for_chunk = []
    for p in chunk.page_refs:
        if p in page_to_assets:
            for img_name in page_to_assets[p]:
                rel = f"assets/{img_name}"
                if rel not in images_for_chunk:
                    images_for_chunk.append(rel)
    
    if images_for_chunk:
        # 去掉 chunk 原文 heading 里的数字前缀
        raw_heading = chunk.heading.strip()
        # 尝试匹配翻译 section（按顺序）
        # 用 chunk 的 index 在翻译 sections 中找对应位置
        # 第一个有图片的 chunk (index=1) → 第一个非摘要非画廊的 section
        chunk_section_map.append({
            "chunk_index": chunk.index,
            "pages": chunk.page_refs,
            "images": images_for_chunk,
            "raw_heading": raw_heading,
        })

print(f"\n  Chunks with images to embed: {len(chunk_section_map)}")
for item in chunk_section_map:
    print(f"    Chunk {item['chunk_index']} (pages {item['pages']}): {item['images']}")

# ── Step 4: 确定每个有图片的 chunk 对应翻译中的哪个 section ──
# 策略：翻译 sections 按顺序对应 chunks（但一个翻译 section 可能含多个 chunk）
# 更精确的方法：对每个翻译 section，看它的内容里提到了哪些 page numbers

# 为每个翻译 section 提取其包含的原文文本片段（通过 [Page N] 标记推断）
# 简单方法：看翻译 section 覆盖了哪些 chunk 的范围

# 16 chunks → 9 sections，大致映射
# Chunks 1-2 → Introduction + Related Work (section index 2, 3)
# Chunks 3-8 → Methodology (section index 4)
# Chunks 9-13 → Experiments (section index 5)
# Chunks 14-15 → Conclusion (section index 6)
# Chunk 16 → Appendix A (section index 7)

# 更精确：查看每个 chunk 的原文 heading，找匹配的翻译 section
# 翻译 sections (跳过 摘要 和 图表资源):
SECTION_HEADINGS = [
    "1 引言（Introduction）",
    "2 相关工作（Related Work）", 
    "3 方法论（Methodology）",
    "4 实验与结果（Experiments and Results）",
    "5 结论（Conclusion）",
    "附录 A",
    "参考文献",
]

# 简单启发式：看翻译 section 的位置和 chunk 的位置是否有重叠
# 用 chunk 的文本片段去匹配翻译 section 中的文本
def find_section_for_chunk(chunk_text: str, sections: list) -> str | None:
    """在翻译 sections 中找与 chunk_text 最匹配的 section。"""
    # 取 chunk_text 的前 100 个非空白字符
    chunk_head = chunk_text.strip()[:100].lower()
    # 取 chunk_text 末尾 100 字符
    chunk_tail = chunk_text.strip()[-100:].lower()
    
    best_section = None
    best_score = 0
    
    for sec in sections:
        h = sec["heading"]
        if h in ("摘要", "图表资源", "参考文献"):
            continue
        # 取该 section 的正文内容
        body = md_content[sec["end"]:sec["end_pos"]].lower()
        
        # 打分：chunk 头/尾出现在 section 正文中的比例
        score = 0
        if chunk_head[:50] in body:
            score += 3
        if chunk_tail[:50] in body:
            score += 2
        
        if score > best_score:
            best_score = score
            best_section = sec
    
    return best_section["heading"] if best_section else None


# 简化方案：根据 chunk index 和 section 顺序直接映射
# 翻译正文中 sections 的索引（跳过摘要@0, 图表资源@1）
# 2:1引言, 3:2相关工作, 4:3方法论, 5:4实验, 6:5结论, 7:附录A

SECTION_INDEX_MAP = {
    # section_index_in_translation → chunk_range (1-indexed)
    2: (1, 2),   # 引言 → chunks 1-2
    3: (2, 3),   # 相关工作 → chunks 2-3
    4: (4, 8),   # 方法论 → chunks 4-8
    5: (9, 13),  # 实验 → chunks 9-13
    6: (14, 15), # 结论 → chunks 14-15
    7: (16, 16), # 附录 → chunk 16
}

def find_section_for_chunk_simple(chunk_index: int, section_positions: list) -> str:
    """Find which translation section contains a given chunk."""
    for sec_idx, (tgt_sec_idx, (start_chunk, end_chunk)) in enumerate(SECTION_INDEX_MAP.items()):
        if start_chunk <= chunk_index <= end_chunk:
            return section_positions[tgt_sec_idx]["heading"]
    return "附录 A"  # fallback

# ── Step 5: 执行注入 ──
print(f"\n" + "=" * 60)
print("Step 5: Injecting images into sections")
print("=" * 60)

new_content = md_content
insertions = 0

for item in chunk_section_map:
    target_heading = find_section_for_chunk_simple(item["chunk_index"], section_positions)
    
    # 找到翻译中这个 heading 的位置
    for sec in section_positions:
        if sec["heading"] == target_heading:
            # 在该 section 的 heading 行之后插入图片
            # 找到 section 内容开始的位置（heading 行之后第一个空行后的非空行）
            sec_body_start = sec["end"]  # right after `## X. YYY`
            
            # 在 section 开头之后找第一个非空行，在它前面插入图片
            body_after = md_content[sec_body_start:sec["start"] + 500]
            # 跳过空行，找第一个非空行
            first_non_empty = None
            for m2 in re.finditer(r'^\s*\S', body_after, re.MULTILINE):
                first_non_empty = m2.start()
                break
            
            if first_non_empty is not None:
                insert_pos = sec_body_start + first_non_empty
                # 构建图片 markdown
                img_block = "\n" + "\n".join(f'![Page {item["pages"]} figure]({img})' for img in item["images"]) + "\n\n"
                
                # 检查是否已经注入了这些图片
                already_has = any(img in new_content[insert_pos:insert_pos+300] for img in item["images"])
                if not already_has:
                    new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
                    print(f"  ✅ Injected {len(item['images'])} image(s) into ## {target_heading}")
                    for img in item["images"]:
                        print(f"     → {img}")
                    insertions += 1
                else:
                    print(f"  ⏭️  Images already in ## {target_heading}, skipping")
            break
    else:
        print(f"  ❌ Could not find section: {target_heading}")

if insertions > 0:
    # Backup original
    backup_path = MD_PATH.with_suffix(".md.bak")
    if not backup_path.exists():
        MD_PATH.rename(backup_path)
        print(f"\n  Backup saved: {backup_path.name}")
    
    # Write new content
    MD_PATH.write_text(new_content)
    print(f"\n  Written {MD_PATH}")
    
    # Verify
    final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)
    # Count refs NOT in gallery section
    gallery_start = new_content.find("## 图表资源")
    gallery_end = new_content.find("## ", gallery_start + 1)
    in_gallery = len(re.findall(r'!\[', new_content[gallery_start:gallery_end])) if gallery_start >= 0 else 0
    total_refs = len(final_refs)
    inline_refs = total_refs - in_gallery
    print(f"\n  Verification:")
    print(f"    Gallery refs: {in_gallery}")
    print(f"    Inline refs: {inline_refs}")
    print(f"    Total refs: {total_refs}")
else:
    print("  No insertions needed")
