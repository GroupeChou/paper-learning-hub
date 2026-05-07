"""
精准注入：对单篇论文，把图片放在正文中提到它的位置。

策略：
1. 从 chunk 原文提取 Figure/Table 编号
2. 在翻译正文中找到这些编号的提及位置（"图 X"、"表 X"、"Figure X"）
3. 把对应的图片插入到提及位置附近
4. 无提及的图片放在 section 开头
"""

import re
import shutil
import sys
from pathlib import Path, PurePath

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

page_to_imgs: dict[int, list[str]] = {}
for pn, paths in parsed.page_images.items():
    page_to_imgs[pn] = [PurePath(p).name for p in paths]

# ── 2. 读取翻译正文 ──
md_content = MD_PATH.read_text()

# ── 3. 对每个有图片的 chunk，找到发表位置 ──
print("Step 2: Finding figure/table mentions in translation\n")

# 定义在翻译中搜索 Figure/Table 提及的模式
FIG_PATTERNS = [
    r'图\s*(\d+(?:\.\d+)?)',     # 图 2, 图2
    r'Figure\s*(\d+(?:\.\d+)?)',  # Figure 2
    r'Fig\.?\s*(\d+(?:\.\d+)?)',  # Fig. 2, Fig 2
    r'表\s*(\d+(?:\.\d+)?)',      # 表 1, 表1
    r'Table\s*(\d+(?:\.\d+)?)',   # Table 1
]

def find_mentions(text: str) -> list[tuple[str, int]]:
    """在文本中找到所有图/表提及，返回 (type_number, position)"""
    mentions = []
    for pattern in FIG_PATTERNS:
        for m in re.finditer(pattern, text):
            mentions.append((m.group(0), m.start()))
    mentions.sort(key=lambda x: x[1])
    return mentions

def _is_reference_chunk(text: str) -> bool:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False
    content_lines = [l for l in lines if not re.match(r'^\[Page \d+\]', l)
                     and not l.startswith('Long-Context')]
    if not content_lines:
        return False
    first_line = content_lines[0]
    if re.match(r'^\[\d+\]', first_line):
        return True
    cite_lines = sum(1 for l in content_lines if re.match(r'^\[\d+\]', l))
    return cite_lines / len(content_lines) > 0.3

# 获取 section 位置
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

# 非内容 section（跳过）
SKIP_SECTIONS = {"摘要", "图表资源", "参考文献"}

# 找到每个 section 的 Figure/Table 提及
section_mentions = {}
for sec in section_positions:
    if sec["heading"] in SKIP_SECTIONS:
        continue
    body = md_content[sec["end"]:sec["end_pos"]]
    section_mentions[sec["heading"]] = find_mentions(body)

# 对每个有图片的 chunk，决定图片放哪里
non_ref_chunks = [c for c in parsed.chunks if not _is_reference_chunk(c.text)]
usable_chunks = len(non_ref_chunks)
content_sections = [s for s in section_positions if s["heading"] not in SKIP_SECTIONS]

def chunk_to_section(chunk_index: int) -> dict:
    """等比映射 chunk → section"""
    non_ref_seq = next((i for i, c in enumerate(non_ref_chunks) if c.index == chunk_index), 0)
    sec_idx = int(non_ref_seq * len(content_sections) / usable_chunks)
    return content_sections[sec_idx]

# ── 4. 执行插入 ──
new_content = md_content
all_insertions = []

for chunk in parsed.chunks:
    imgs = []
    for p in chunk.page_refs:
        imgs.extend(page_to_imgs.get(p, []))
    if not imgs:
        continue
    
    # 从 chunk 原文提取 Figure/Table 编号
    ctext = chunk.text
    fig_nums = set(re.findall(r'(?:Figure|Fig\.?)\s*(\d+(?:\.\d+)?)', ctext, re.IGNORECASE))
    tbl_nums = set(re.findall(r'(?:TABLE|Table)\s*(\d+(?:\.\d+)?)', ctext, re.IGNORECASE))
    
    section = chunk_to_section(chunk.index)
    sec_body = md_content[section["end"]:section["end_pos"]]
    sec_mentions = section_mentions.get(section["heading"], [])
    
    # 收集该 section 中所有与这些编号匹配的提及位置
    matched_positions = []
    all_nums = fig_nums | tbl_nums
    
    for mention_str, pos in sec_mentions:
        mention_num = mention_str.split()[-1] if ' ' in mention_str else mention_str[1:]
        # 注意：mention_str 如 "图 2" 或 "Figure 2"，提取数字
        nums_in_str = re.findall(r'\d+(?:\.\d+)?', mention_str)
        if nums_in_str and nums_in_str[0] in all_nums:
            # 计算实际位置（在 md_content 中）
            actual_pos = section["end"] + pos
            matched_positions.append((mention_str, actual_pos, nums_in_str[0]))
    
    if matched_positions:
        # 有匹配的提及位置 → 在提及处插入对应图片
        # 按位置排序
        matched_positions.sort(key=lambda x: x[1])
        
        # 分配图片到各提及位置（按顺序）
        images_for_mentions = _distribute_imgs_to_mentions(imgs, fig_nums, tbl_nums, matched_positions)
        
        for mention_str, pos, num, assigned_imgs in images_for_mentions:
            # 找到提及行的开头（确保插入在段落中合适的位置）
            img_block = "\n\n" + "\n\n".join(f'![图{num}](assets/{img})' for img in assigned_imgs) + "\n\n"
            
            # 在提及文本之前插入
            insert_pos = pos
            
            # 检查是否已注入
            check_region = new_content[max(0, insert_pos - 200):insert_pos + len(img_block) + 300]
            if any(img in check_region for img in assigned_imgs):
                print(f"  ⏭️  Image already near \"{mention_str}\" in \"{section['heading']}\"")
                continue
            
            new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
            all_insertions.append((section["heading"], mention_str, len(assigned_imgs)))
            print(f"  ✅ {len(assigned_imgs)} img(s) at \"{mention_str}\" in \"{section['heading']}\"")
            
            # 更新后续位置
            offset = len(img_block)
            for later_sec in section_positions:
                if later_sec["start"] > insert_pos:
                    later_sec["start"] += offset
                    later_sec["end"] += offset
                    later_sec["end_pos"] += offset
            # 更新 section_mentions 中的位置
            for m_section, mentions in section_mentions.items():
                section_mentions[m_section] = [
                    (m_str, m_pos + (offset if m_pos > insert_pos - section["end"] else 0))
                    for m_str, m_pos in mentions
                ]
    else:
        # 无匹配提及 → 放在 section 开头（每个 chunk 独立注入）
        body_slice = new_content[section["end"]:section["end_pos"]]
        m = re.search(r'^\s*\S', body_slice, re.MULTILINE)
        if m:
            insert_pos = section["end"] + m.start()
            img_block = "\n\n" + "\n\n".join(f'![论文原图](assets/{img})' for img in imgs) + "\n\n"
            
            new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
            all_insertions.append((section["heading"], "section_start", len(imgs)))
            print(f"  ✅ Chunk {chunk.index}: {len(imgs)} img(s) at section start \"{section['heading']}\"")


def _distribute_imgs_to_mentions(imgs: list[str], fig_nums: set, tbl_nums: set, matched_positions: list) -> list:
    """将图片分配到各提及位置"""
    result = []
    # 如果图片数量和提及位置匹配，一一对应
    # 否则，把所有图片放到第一个提及处
    if len(imgs) <= len(matched_positions):
        # 尝试分配
        remaining = list(imgs)
        for mention_str, pos, num in matched_positions:
            if remaining:
                result.append((mention_str, pos, num, [remaining.pop(0)]))
            else:
                break
        # 补回剩余的（按顺序）
        if remaining:
            result[-1] = (*result[-1][:3], result[-1][3] + remaining)
    else:
        # 图片多于提及 → 全放第一个提及
        mention_str, pos, num = matched_positions[0]
        result.append((mention_str, pos, num, imgs))
    return result


# ── 5. 校验 ──
print("\n" + "=" * 60)
print("Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)

# 统计 gallery
gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    gallery_section = new_content[gallery_start:next_h2] if next_h2 >= 0 else new_content[gallery_start:]
    gallery_refs_num = len(re.findall(r'!\[', gallery_section))
else:
    gallery_refs_num = 0

# 校验路径
broken = sum(1 for ref in final_refs if not (ASSETS_DIR / ref.replace("assets/", "")).exists())

print(f"  Total refs: {len(final_refs)}")
print(f"  Gallery: {gallery_refs_num}")
print(f"  Inline in body: {len(final_refs) - gallery_refs_num}")
print(f"  Broken: {broken}")
print(f"  Insertions: {len(all_insertions)}")
for section, mention, count in all_insertions:
    print(f"    \"{section}\" @ {mention}: {count} img(s)")

if all_insertions:
    bak = MD_PATH.with_suffix(".md.bak2")
    if not bak.exists():
        shutil.copy2(MD_PATH, bak)
        print(f"\n  Backup: {bak.name}")
    MD_PATH.write_text(new_content)
    print(f"  Written: {MD_PATH}")
