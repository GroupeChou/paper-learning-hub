"""
智能图片注入 v4：按原文引用位置比例映射到翻译正文

核心思路：
1. 从 chunk 原文中提取 "Figure X" / "Table X" 的引用位置（字符偏移）
2. 计算该引用在 chunk 中的 % 位置
3. 将 % 位置等比映射到翻译 section 的正文中
4. 把图片插入到对应的 % 位置

对没有显式编号引用的图片（如 title page 的图），放在 section 开头。
"""

import re
import shutil
import sys
from pathlib import Path, PurePath
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from paper_learning_hub.parser import parse_document

PID = "2604.24715v1"
ZH_DIR = Path(f"papers/zh/{PID}")
RAW_PATH = Path(f"papers/raw/{PID}/paper.pdf")
MD_PATH = ZH_DIR / "paper_zh.md"
ASSETS_DIR = ZH_DIR / "assets"


# ── 1. 解析 PDF ──
print("=" * 60)
print(f"Step 1: Parsing {PID}")
parsed = parse_document(RAW_PATH, ZH_DIR, max_chars=5000, max_images=100)

page_to_imgs: dict[int, list[str]] = {}
for pn, paths in parsed.page_images.items():
    page_to_imgs[pn] = [PurePath(p).name for p in paths]

total_chunks = len(parsed.chunks)
print(f"  {total_chunks} chunks, {len(parsed.image_paths)} images")


# ── 2. 从 chunk 原文提取图片引用位置 ──
@dataclass
class ImageRef:
    filename: str
    fig_num: str | None      # "2" from "Figure 2"
    ref_type: str             # "figure", "table", or "unknown"
    position_ratio: float     # 在 chunk 中的 % 位置 (0.0~1.0)
    chunk_index: int
    page_nums: list[int]

fig_ref_pattern = re.compile(
    r'(?:Figure|Fig\.?)\s*(\d+(?:\.\d+)?)', re.IGNORECASE
)
tbl_ref_pattern = re.compile(
    r'(?:TABLE|Table)\s*(\d+(?:\.\d+)?)', re.IGNORECASE
)

all_image_refs: list[ImageRef] = []
chunk_image_map: dict[int, list[ImageRef]] = {}  # chunk_index → refs

for chunk in parsed.chunks:
    imgs_on_pages = []
    for p in chunk.page_refs:
        imgs_on_pages.extend(page_to_imgs.get(p, []))
    if not imgs_on_pages:
        continue
    
    chunk_text = chunk.text
    chunk_len = len(chunk_text)
    
    # 找出所有 figure/table 引用及位置
    fig_matches = list(fig_ref_pattern.finditer(chunk_text))
    tbl_matches = list(tbl_ref_pattern.finditer(chunk_text))
    
    # 构建引用列表（按位置排序）
    all_matches = []
    for m in fig_matches:
        all_matches.append((m.start(), "figure", m.group(1)))
    for m in tbl_matches:
        all_matches.append((m.start(), "table", m.group(1)))
    all_matches.sort(key=lambda x: x[0])
    
    # 为每个引用分配图片文件
    figs = [m for m in all_matches if m[1] == "figure"]
    tbls = [m for m in all_matches if m[1] == "table"]
    
    # 简单启发：图片文件按顺序分配到引用按顺序
    # 但多个图片可能对应同一个 Figure（如 Figure 2 的 5 个子图）
    refs_for_chunk = []
    pos_index = 0
    
    for img_name in imgs_on_pages:
        # 看是否有未分配的引用
        if pos_index < len(all_matches):
            pos, ref_type, ref_num = all_matches[pos_index]
            ratio = pos / chunk_len if chunk_len > 0 else 0.0
            refs_for_chunk.append(ImageRef(
                filename=img_name,
                fig_num=ref_num,
                ref_type=ref_type,
                position_ratio=ratio,
                chunk_index=chunk.index,
                page_nums=chunk.page_refs,
            ))
            # 多个图片共享同一个 Figure 编号 → 不增加 pos_index
            # Figure 2 有 5 个子图，第一个分配了 "2"，后续也分配 "2"
            # 但位置递进：后续子图的 position_ratio 逐渐增大
            next_img_idx = imgs_on_pages.index(img_name) + 1
            # 给同一 Figure 的子图分配相邻位置
            if next_img_idx < len(imgs_on_pages):
                # 同一 figure 的子图，在 figure 引用位置附近均匀分布
                spacing = 0.05  # 5% spacing between sub-figures
                refs_for_chunk[-1].position_ratio = min(ratio + (next_img_idx - 1) * spacing, 0.95)
            # 只在遇到新的 figure 号时增加 pos_index
            # 简化：每张图分配一个位置，位置沿 chunk 递增
        else:
            # 无引用 → 均匀分布
            refs_for_chunk.append(ImageRef(
                filename=img_name,
                fig_num=None,
                ref_type="unknown",
                position_ratio=min(0.1 + 0.8 * (pos_index - len(all_matches) + 1) / max(len(imgs_on_pages), 1), 0.95),
                chunk_index=chunk.index,
                page_nums=chunk.page_refs,
            ))
        pos_index += 1
    
    chunk_image_map[chunk.index] = refs_for_chunk
    all_image_refs.extend(refs_for_chunk)
    
    print(f"  Chunk {chunk.index:2d} (p{chunk.page_refs}): {len(refs_for_chunk)} images")
    for ref in refs_for_chunk:
        print(f"    {ref.filename} → \"{ref.ref_type} {ref.fig_num if ref.fig_num else '?'}\" @ {ref.position_ratio:.0%}")


# ── 3. 读取翻译正文结构 ──
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

SKIP_SECTIONS = {"摘要", "图表资源", "参考文献"}
content_sections = [s for s in section_positions if s["heading"] not in SKIP_SECTIONS]

# 检测 reference chunk
def _is_reference_chunk(text: str) -> bool:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False
    content_lines = [l for l in lines if not re.match(r'^\[Page \d+\]', l)
                     and not l.startswith('Long-Context')]
    if not content_lines:
        return False
    if re.match(r'^\[\d+\]', content_lines[0]):
        return True
    cite_lines = sum(1 for l in content_lines if re.match(r'^\[\d+\]', l))
    return cite_lines / len(content_lines) > 0.3

non_ref_chunks = [c for c in parsed.chunks if not _is_reference_chunk(c.text)]
usable_chunks = len(non_ref_chunks)

def chunk_to_section(chunk_index: int) -> dict:
    non_ref_seq = next((i for i, c in enumerate(non_ref_chunks) if c.index == chunk_index), 0)
    sec_idx = int(non_ref_seq * len(content_sections) / usable_chunks)
    return content_sections[sec_idx]


# ── 4. 按比例位置注入图片 ──
print("\n" + "=" * 60)
print("Step 4: Injecting images at proportional positions")

new_content = md_content
insertions = 0

# 对每个有图片的 chunk，找到对应的 translation section
chunk_section_map = {}
for chunk in parsed.chunks:
    if chunk.index in chunk_image_map:
        chunk_section_map[chunk.index] = chunk_to_section(chunk.index)

# 为每个 chunk 找到 section 正文部分的字符范围（不含 heading 行）
section_body_ranges = {}
for section in section_positions:
    body = md_content[section["end"]:section["end_pos"]]
    # 找到第一个非空行
    first_content = re.search(r'\S', body)
    if first_content:
        body_start = section["end"] + first_content.start()
    else:
        body_start = section["end"]
    section_body_ranges[section["heading"]] = (body_start, section["end_pos"])

# 逐个注入
for chunk_index, section in sorted(chunk_section_map.items()):
    refs = chunk_image_map[chunk_index]
    body_start, body_end = section_body_ranges.get(section["heading"], (section["end"], section["end_pos"]))
    body_length = body_end - body_start
    
    if body_length <= 0:
        print(f"  ❌ Empty body for section \"{section['heading']}\"")
        continue
    
    for ref in refs:
        # 计算在翻译正文中的目标位置
        target_ratio = ref.position_ratio
        insert_offset = int(target_ratio * body_length)
        insert_pos = body_start + insert_offset
        
        # 关键优化：找到最近的段落边界（\n\n），避免插在段落中间
        body_segment = new_content[body_start:body_end]
        
        # 找到目标位置前后的段落边界
        rel_pos = insert_offset  # 相对 body_start 的位置
        
        # 向后找段落边界
        next_boundary = body_segment.find('\n\n', rel_pos)
        # 向前找段落边界
        prev_boundary = body_segment.rfind('\n\n', 0, rel_pos)
        
        # 选择更近的段落边界
        if prev_boundary >= 0 and next_boundary >= 0:
            if (rel_pos - prev_boundary) <= (next_boundary - rel_pos):
                insert_pos = body_start + prev_boundary + 2  # after \n\n
            else:
                insert_pos = body_start + next_boundary + 2
        elif prev_boundary >= 0:
            insert_pos = body_start + prev_boundary + 2
        elif next_boundary >= 0:
            insert_pos = body_start + next_boundary + 2
        # else: keep original position (no paragraph boundary found)
        
        alt_text = f"图{ref.fig_num}" if ref.fig_num else "论文原图"
        img_line = f'![{alt_text}](assets/{ref.filename})'
        img_block = f"\n\n{img_line}\n"
        
        # 检查是否已存在
        if ref.filename in new_content[max(0, insert_pos - 50):insert_pos + len(img_block) + 50]:
            print(f"  ⏭️  {ref.filename} already in \"{section['heading']}\"")
            continue
        
        new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
        
        # 更新所有后续位置
        offset = len(img_block)
        for sec in section_positions:
            if sec["start"] > insert_pos:
                sec["start"] += offset
                sec["end"] += offset
                sec["end_pos"] += offset
        # 更新 body ranges
        for h in section_body_ranges:
            bs, be = section_body_ranges[h]
            if bs > insert_pos:
                section_body_ranges[h] = (bs + offset, be + offset)
            elif be > insert_pos:
                section_body_ranges[h] = (bs, be + offset)
        body_start, body_end = section_body_ranges.get(section["heading"], (0, 0))
        
        insertions += 1
        fig_info = f"图{ref.fig_num}" if ref.fig_num else "无编号"
        print(f"  ✅ {ref.filename} ({fig_info}) @ {target_ratio:.0%} in \"{section['heading']}\"")


# ── 5. 校验 ──
print("\n" + "=" * 60)
print("Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)

# 校验
broken = sum(1 for ref in final_refs if not (ASSETS_DIR / ref.replace("assets/", "")).exists())

# 统计 gallery
gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    gallery_section = new_content[gallery_start:next_h2] if next_h2 >= 0 else new_content[gallery_start:]
    gallery_refs_num = len(re.findall(r'!\[', gallery_section))
else:
    gallery_refs_num = 0

print(f"  Total refs: {len(final_refs)}")
print(f"  Gallery: {gallery_refs_num}")
print(f"  Inline: {len(final_refs) - gallery_refs_num}")
print(f"  Broken: {broken}")
print(f"  Insertions: {insertions}")

if insertions > 0:
    bak = MD_PATH.with_suffix(".md.bak3")
    if not bak.exists():
        shutil.copy2(MD_PATH, bak)
        print(f"  Backup: {bak.name}")
    MD_PATH.write_text(new_content)
    print(f"  Written: {MD_PATH}")
