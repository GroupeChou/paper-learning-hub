"""
演示：对单篇论文注入内联图片 v3

策略：按 chunks 数量在翻译 sections 之间等比分配，
将每页的图片嵌入到对应 section 的正文开头。
"""

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from paper_learning_hub.parser import parse_document

PID = "2604.24715v1"
ZH_DIR = Path(f"papers/zh/{PID}")
RAW_PATH = Path(f"papers/raw/{PID}/paper.pdf")
MD_PATH = ZH_DIR / "paper_zh.md"
ASSETS_DIR = ZH_DIR / "assets"


# ── 1. 解析 PDF，获取 chunk→page→image 映射 ──
print("=" * 60)
print(f"Step 1: Parsing {PID}")
parsed = parse_document(RAW_PATH, ZH_DIR, max_chars=5000, max_images=100)

page_to_images: dict[int, list[str]] = {}
for page_num, img_paths in parsed.page_images.items():
    page_to_images[page_num] = [f"assets/{Path(p).name}" for p in img_paths]

total_chunks = len(parsed.chunks)
print(f"  Total chunks: {total_chunks}")
print(f"  Total images: {len(parsed.image_paths)}")
for pn in sorted(page_to_images):
    print(f"  Page {pn}: {len(page_to_images[pn])} image(s) → {page_to_images[pn]}")


# ── 2. 读取翻译正文 section 结构 ──
print("\n" + "=" * 60)
print("Step 2: Reading translation sections")

md_content = MD_PATH.read_text()

section_positions = []
for m in re.finditer(r'^## (.+)$', md_content, re.MULTILINE):
    section_positions.append({
        "heading": m.group(1).strip(),
        "start": m.start(),
        "end": m.end(),
    })
for i, sec in enumerate(section_positions):
    if i + 1 < len(section_positions):
        sec["end_pos"] = section_positions[i + 1]["start"]
    else:
        sec["end_pos"] = len(md_content)

# 内容 sections（跳过 摘要=0, 图表资源=1, 参考文献=last）
non_content = {"摘要", "图表资源", "参考文献"}
content_sections = [s for s in section_positions if s["heading"] not in non_content]
print(f"  Content sections ({len(content_sections)}):")
for sec in content_sections:
    print(f"    [{section_positions.index(sec)}] {sec['heading']}")


# ── 3. 将 chunks 等比分配到 content sections ──
print("\n" + "=" * 60)
print("Step 3: Distributing chunks to sections")

chunks_per_section = total_chunks / len(content_sections)
print(f"  {total_chunks} chunks / {len(content_sections)} sections ≈ {chunks_per_section:.1f} per section")

# 检测 reference chunk：跳过 page header 后，看第一个实质内容行是否以 [数字] 开头
def _is_reference_chunk(text: str) -> bool:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False
    # 跳过 [Page N] 和论文标题行（通常是前3行）
    content_lines = [l for l in lines if not re.match(r'^\[Page \d+\]', l)
                     and not l.startswith('Long-Context')]
    if not content_lines:
        return False
    # 如果首个实质内容行以 [数字] 开头 → reference
    first_line = content_lines[0]
    if re.match(r'^\[\d+\]', first_line):
        return True
    # 或超过 30% 的行是引用格式
    cite_lines = sum(1 for l in content_lines if re.match(r'^\[\d+\]', l))
    return cite_lines / len(content_lines) > 0.3

# 只计数非 reference 的 chunk 做比例分配
non_ref_chunks = [c for c in parsed.chunks if not _is_reference_chunk(c.text)]
ref_chunks = [c for c in parsed.chunks if _is_reference_chunk(c.text)]
usable_chunks = len(non_ref_chunks)
print(f"  Non-ref chunks: {usable_chunks}, Ref chunks: {len(ref_chunks)}")

# chunk_index (1-based) → content_section index (0-based)
def chunk_to_section_idx(chunk_index: int) -> int:
    """只用非 reference chunk 做等比映射"""
    # 找到这个 chunk 在 non-ref list 中的序号
    non_ref_seq = next((i for i, c in enumerate(non_ref_chunks) if c.index == chunk_index), None)
    if non_ref_seq is None:
        return 0  # fallback
    return int(non_ref_seq * len(content_sections) / usable_chunks)

# 🔍 验证映射
chunk_section_map = {}  # chunk_index → section_heading
for chunk in parsed.chunks:
    sec_idx = chunk_to_section_idx(chunk.index)
    sec_heading = content_sections[sec_idx]["heading"]
    chunk_section_map[chunk.index] = sec_heading
    
has_imgs = [c for c in parsed.chunks 
            if any(p in page_to_images for p in c.page_refs)]
for c in has_imgs:
    print(f"  Chunk {c.index:2d} (p{c.page_refs}) → \"{chunk_section_map[c.index]}\"")


# ── 4. 构建 section→images 映射 ──
print("\n" + "=" * 60)
print("Step 4: Building section→images mapping")

section_images = {}  # heading → [asset_paths]
for chunk in parsed.chunks:
    images_for_chunk = []
    for p in chunk.page_refs:
        if p in page_to_images:
            for img in page_to_images[p]:
                if img not in images_for_chunk:
                    images_for_chunk.append(img)
    
    if images_for_chunk:
        sec_heading = chunk_section_map[chunk.index]
        if sec_heading not in section_images:
            section_images[sec_heading] = []
        for img in images_for_chunk:
            if img not in section_images[sec_heading]:
                section_images[sec_heading].append(img)

for sec, imgs in section_images.items():
    print(f"  \"{sec}\" → {len(imgs)} image(s)")
    for img in imgs:
        print(f"    {img}")


# ── 5. 注入到翻译正文 ──
print("\n" + "=" * 60)
print("Step 5: Injecting images")

new_content = md_content
insertions = 0

for target_section, images in section_images.items():
    for sec in section_positions:
        # 匹配 section（用包含关系判断中英文变体）
        if target_section in sec["heading"] or sec["heading"] in target_section:
            # 在 section heading 后第一个非空行处插入
            body_slice = md_content[sec["end"]:sec["end_pos"]]
            m = re.search(r'^\s*\S', body_slice, re.MULTILINE)
            if not m:
                break
            
            insert_pos = sec["end"] + m.start()
            
            # 构建图片 markdown 块
            img_block = "\n\n" + "\n\n".join(
                f'![论文原图]({img})' for img in images
            ) + "\n\n"
            
            # 去重检查
            check_region = new_content[max(0, insert_pos - 200):insert_pos + len(img_block) + 500]
            already = sum(1 for img in images if img in check_region)
            if already >= len(images):
                print(f"  ⏭️  Already injected in \"{sec['heading']}\"")
                break
            
            # 注入
            new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
            print(f"  ✅ {len(images)} image(s) → \"{sec['heading']}\"")
            
            # 更新位置偏移
            offset = len(img_block)
            for later_sec in section_positions:
                if later_sec["start"] > insert_pos:
                    later_sec["start"] += offset
                    later_sec["end"] += offset
                    later_sec["end_pos"] += offset
            insertions += 1
            break


# ── 6. 校验 ──
print("\n" + "=" * 60)
print("Step 6: Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)

# 统计 gallery 和 inline
gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    if next_h2 < 0:
        next_h2 = len(new_content)
    gallery_refs = len(re.findall(r'!\[', new_content[gallery_start:next_h2]))
else:
    gallery_refs = 0

# 校验 asset 路径
broken = sum(1 for ref in final_refs 
             if not (ASSETS_DIR / ref.replace("assets/", "")).exists())
all_exist = broken == 0

print(f"  Total image refs: {len(final_refs)}")
print(f"  Gallery section:  {gallery_refs}")
print(f"  Inline in body:   {len(final_refs) - gallery_refs}")
print(f"  Broken refs:      {broken}")
print(f"  All paths valid:  {'✅' if all_exist else '❌'}")

if insertions > 0:
    # 备份
    bak = MD_PATH.with_suffix(".md.bak")
    if not bak.exists():
        shutil.copy2(MD_PATH, bak)
        print(f"\n  Backup saved: {bak.name}")
    
    MD_PATH.write_text(new_content)
    print(f"  Written: {MD_PATH}")
    print(f"  Injections: {insertions}")
else:
    print("  No changes made")
