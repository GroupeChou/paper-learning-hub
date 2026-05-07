"""
精准图片注入 v6：Caption 语义匹配 + 删除画廊

策略：
1. 从 chunk 原文提取 Figure/Table caption 文本
2. 用 caption 中的关键词在翻译 section 正文中搜索
3. 找到最匹配的段落，在段落边界处插入图片
4. 删除 ## 图表资源 画廊
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

print(f"  {len(parsed.chunks)} chunks, {len(parsed.image_paths)} images")


# ── 2. 提取 caption 和关键词 ──
@dataclass
class ImageInfo:
    filename: str
    fig_num: str | None
    caption: str
    keywords: list[str]    # 从 caption 提取的关键词
    chunk_index: int
    page_nums: list[int]

fig_cap_pattern = re.compile(
    r'(Figure\s+\d+[\.:]\s*[^\n]{10,200})', re.IGNORECASE | re.DOTALL
)
tbl_cap_pattern = re.compile(
    r'(Table\s+\d+[\.:]\s*[^\n]{10,200})', re.IGNORECASE | re.DOTALL
)

all_images: list[ImageInfo] = []

for chunk in parsed.chunks:
    imgs_on_pages = []
    for p in chunk.page_refs:
        imgs_on_pages.extend(page_to_imgs.get(p, []))
    if not imgs_on_pages:
        continue

    text = chunk.text
    # 清理 [Page N] 标记
    clean_text = re.sub(r'\[Page \d+\]\n*', '', text)

    # 提取 captions
    captions = []
    for m in fig_cap_pattern.finditer(clean_text):
        captions.append(("figure", m.group(1).strip()))
    for m in tbl_cap_pattern.finditer(clean_text):
        captions.append(("table", m.group(1).strip()))

    for idx, img_name in enumerate(imgs_on_pages):
        fig_num = None
        caption = ""
        keywords = []

        if idx < len(captions):
            rtype, cap = captions[idx]
            m = re.search(r'(\d+)', cap)
            if m:
                fig_num = m.group(1)
            caption = cap[:120]
            # 提取关键词：去掉 Figure/Table 前缀，取重要名词短语
            kw_text = re.sub(r'^(Figure|Table)\s+\d+[\.:]\s*', '', caption, flags=re.IGNORECASE)
            # 提取至少 4 个字符的英文单词
            keywords = list(set(re.findall(r'[A-Za-z][a-z]{3,}(?:\s+[A-Za-z][a-z]{2,}){0,2}', kw_text)))
            # 加入关键缩写词
            for abbr in re.findall(r'\b[A-Z]{2,}\b', kw_text):
                keywords.append(abbr)
            keywords = [k for k in keywords if len(k) >= 4][:8]
        else:
            # 无 caption：尝试从 chunk 文本提取数字
            nums = re.findall(r'(?:Figure|Fig\.?)\s*(\d+)', clean_text[:500], re.IGNORECASE)
            if nums:
                fig_num = nums[0]

        # 从 chunk 开头提取论文主题词（前 100 字符）
        if not keywords:
            ctx = clean_text.strip()[:100]
            keywords = list(set(re.findall(r'[A-Z][a-z]{2,}(?:\s+[a-z]{2,}){0,2}', ctx)))
            keywords = [k for k in keywords if len(k) >= 5][:5]

        info = ImageInfo(
            filename=img_name, fig_num=fig_num,
            caption=caption, keywords=keywords,
            chunk_index=chunk.index, page_nums=chunk.page_refs,
        )
        all_images.append(info)
        caption_preview = caption[:60] if caption else "(no caption)"
        print(f"  {img_name}: \"{caption_preview}\" kw={keywords[:3]}")


# ── 3. 翻译正文结构 ──
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


def _is_reference_chunk(text: str) -> bool:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines: return False
    cl = [l for l in lines if not re.match(r'^\[Page \d+\]', l) and not l.startswith('Long-Context')]
    if not cl: return False
    if re.match(r'^\[\d+\]', cl[0]): return True
    return sum(1 for l in cl if re.match(r'^\[\d+\]', l)) / len(cl) > 0.3


non_ref_chunks = [c for c in parsed.chunks if not _is_reference_chunk(c.text)]
usable_chunks = len(non_ref_chunks)


def chunk_to_section(chunk_index: int) -> dict:
    nrs = next((i for i, c in enumerate(non_ref_chunks) if c.index == chunk_index), 0)
    return content_sections[min(int(nrs * len(content_sections) / usable_chunks), len(content_sections) - 1)]


# ── 4. Caption 语义匹配注入 ──
print("\n" + "=" * 60)
print("Step 4: Caption-based semantic matching")

new_content = md_content
cap_match_count = 0
fallback_count = 0


def update_offsets(insert_pos: int, offset: int):
    for s in section_positions:
        if s["start"] > insert_pos:
            s["start"] += offset
            s["end"] += offset
            s["end_pos"] += offset


def nearest_para_boundary(text: str, rel_pos: int) -> int:
    nb = text.find('\n\n', rel_pos)
    pb = text.rfind('\n\n', 0, rel_pos)
    if pb >= 0 and nb >= 0:
        return pb if (rel_pos - pb) <= (nb - rel_pos) else nb
    elif pb >= 0: return pb
    elif nb >= 0: return nb
    return rel_pos


for img_info in all_images:
    section = chunk_to_section(img_info.chunk_index)
    sec_body = new_content[section["end"]:section["end_pos"]]
    body_len = len(sec_body)

    # 用关键词在 section 正文中搜索
    best_pos = None
    best_score = 0
    
    for kw in img_info.keywords:
        # 多个匹配位置，选最相关的一个
        for m in re.finditer(re.escape(kw), sec_body, re.IGNORECASE):
            pos = m.start()
            # 得分公式：短关键词权重较低，位置越早越好
            score = len(kw) * 2 - abs(pos - body_len * 0.3) / body_len * 10
            if score > best_score:
                best_score = score
                best_pos = pos

    if best_pos and best_score > 3:
        # 在匹配位置处的段落边界插入
        bp = nearest_para_boundary(sec_body, best_pos)
        insert_pos = section["end"] + bp + 2
        cap_match_count += 1
        alt = f"图{img_info.fig_num}" if img_info.fig_num else "论文原图"
        img_block = f"\n\n![{alt}](assets/{img_info.filename})\n"
        new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
        update_offsets(insert_pos, len(img_block))
        print(f"  ✅ Caption match: {img_info.filename} in \"{section['heading']}\" (kw=\"{img_info.keywords[0]}\")")
    else:
        # Fallback: 放在 section 开头
        ms = re.search(r'\S', sec_body)
        if ms:
            insert_pos = section["end"] + ms.start()
            fallback_count += 1
            alt = f"图{img_info.fig_num}" if img_info.fig_num else "论文原图"
            img_block = f"\n\n![{alt}](assets/{img_info.filename})\n"
            new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
            update_offsets(insert_pos, len(img_block))
            print(f"  ⚠️ Fallback: {img_info.filename} in \"{section['heading']}\"")


# ── 5. 删除画廊 ──
print("\n" + "=" * 60)
print("Step 5: Removing gallery section")

gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    if next_h2 < 0: next_h2 = len(new_content)
    new_content = new_content[:gallery_start] + new_content[next_h2:]
    print("  ✅ Gallery removed")
else:
    print("  ⏭️  No gallery")


# ── 6. 校验 ──
print("\n" + "=" * 60)
print("Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)
broken = sum(1 for ref in final_refs if not (ASSETS_DIR / ref.replace("assets/", "")).exists())
has_gallery = "## 图表资源" in new_content

# 按 section 统计
section_stats = {}
for s in section_positions:
    sec = new_content[s["start"]:s["end_pos"]]
    n = len(re.findall(r'!\[', sec))
    if n > 0:
        section_stats[s["heading"]] = n

print(f"  Total refs: {len(final_refs)}")
print(f"  Broken: {broken}  All valid: {'✅' if broken == 0 else '❌'}")
print(f"  Gallery: {'❌' if has_gallery else '✅ Removed'}")
print(f"  Caption matches: {cap_match_count}")
print(f"  Fallbacks: {fallback_count}")
for s, n in section_stats.items():
    print(f"    ## {s}: {n} images")

if cap_match_count + fallback_count > 0:
    bak = MD_PATH.with_suffix(".md.bak6")
    if not bak.exists():
        shutil.copy2(MD_PATH, bak)
        print(f"  Backup: {bak.name}")
    MD_PATH.write_text(new_content)
    print(f"  Written: {MD_PATH}")
