"""
精准图片注入 v5：三阶段匹配策略 + 删除画廊

三阶段：
1. 精确匹配：翻译正文中的 "图 X" / "Figure X" → 在提及处插入
2. 语义匹配：用图片所在 chunk 原文的主题词在 section 中找到最匹配段落
3. 比例位置（fallback）：按 % 位置插入

同时从翻译正文中删除 ## 图表资源 画廊区。
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


# ── 2. 从 chunk 原文提取 Figure/Table 引用 ──
@dataclass
class ImageRef:
    filename: str
    fig_num: str | None
    ref_type: str     # "figure", "table", "unknown"
    position_ratio: float
    chunk_index: int
    page_nums: list[int]
    chunk_context: str = ""

fig_ref_pattern = re.compile(r'(?:Figure|Fig\.?)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)
tbl_ref_pattern = re.compile(r'(?:TABLE|Table)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)

all_image_refs: list[ImageRef] = []
chunk_image_map: dict[int, list[ImageRef]] = {}

for chunk in parsed.chunks:
    imgs_on_pages = []
    for p in chunk.page_refs:
        imgs_on_pages.extend(page_to_imgs.get(p, []))
    if not imgs_on_pages:
        continue

    chunk_text = chunk.text
    chunk_len = len(chunk_text)

    fig_matches = list(fig_ref_pattern.finditer(chunk_text))
    tbl_matches = list(tbl_ref_pattern.finditer(chunk_text))

    all_matches = []
    for m in fig_matches:
        all_matches.append((m.start(), "figure", m.group(1)))
    for m in tbl_matches:
        all_matches.append((m.start(), "table", m.group(1)))
    all_matches.sort(key=lambda x: x[0])

    refs_for_chunk = []
    for idx, img_name in enumerate(imgs_on_pages):
        fig_num = None
        ref_type = "unknown"
        ratio = min(0.1 + 0.8 * idx / max(len(imgs_on_pages), 1), 0.95)

        if idx < len(all_matches):
            pos, rtype, rnum = all_matches[idx]
            fig_num = rnum
            ref_type = rtype
            ratio = pos / chunk_len if chunk_len > 0 else 0.0
        else:
            ratio = min(0.1 + 0.8 * idx / max(len(imgs_on_pages), 1), 0.95)

        # 图片附近的原文上下文
        ctx_start = max(0, int(ratio * chunk_len) - 80)
        ctx_end = min(chunk_len, int(ratio * chunk_len) + 80)
        context = chunk_text[ctx_start:ctx_end].strip()[:150]
        context = re.sub(r'\[Page \d+\]', '', context).strip()

        refs_for_chunk.append(ImageRef(
            filename=img_name, fig_num=fig_num, ref_type=ref_type,
            position_ratio=ratio, chunk_index=chunk.index,
            page_nums=chunk.page_refs, chunk_context=context,
        ))

    chunk_image_map[chunk.index] = refs_for_chunk
    all_image_refs.extend(refs_for_chunk)

    for ref in refs_for_chunk:
        ftype = f"{ref.ref_type} {ref.fig_num}" if ref.fig_num else "unmatched"
        print(f"  Chk{chunk.index:2d} p{ref.page_nums}: {ref.filename} → \"{ftype}\" @ {ref.position_ratio:.0%}")


# ── 3. 翻译正文结构解析 ──
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
    if not lines:
        return False
    cl = [l for l in lines if not re.match(r'^\[Page \d+\]', l) and not l.startswith('Long-Context')]
    if not cl:
        return False
    if re.match(r'^\[\d+\]', cl[0]):
        return True
    return sum(1 for l in cl if re.match(r'^\[\d+\]', l)) / len(cl) > 0.3


non_ref_chunks = [c for c in parsed.chunks if not _is_reference_chunk(c.text)]
usable_chunks = len(non_ref_chunks)


def chunk_to_section(chunk_index: int) -> dict:
    nrs = next((i for i, c in enumerate(non_ref_chunks) if c.index == chunk_index), 0)
    return content_sections[min(int(nrs * len(content_sections) / usable_chunks), len(content_sections) - 1)]


# ── 4. 三阶段匹配注入 + 删除画廊 ──
print("\n" + "=" * 60)
print("Step 4: Three-stage injection")

new_content = md_content
stage1_count = 0
stage2_count = 0
stage3_count = 0

section_bodies = {}
for sec in section_positions:
    body = new_content[sec["end"]:sec["end_pos"]]
    m = re.search(r'\S', body)
    bs = sec["end"] + m.start() if m else sec["end"]
    section_bodies[sec["heading"]] = {"start": bs, "end": sec["end_pos"]}


def update_offsets(insert_pos: int, offset: int):
    for s in section_positions:
        if s["start"] > insert_pos:
            s["start"] += offset
            s["end"] += offset
            s["end_pos"] += offset
    for h in section_bodies:
        bi = section_bodies[h]
        if bi["start"] > insert_pos:
            bi["start"] += offset
        if bi["end"] > insert_pos:
            bi["end"] += offset


def nearest_para_boundary(text: str, rel_pos: int) -> int:
    """找到最近的段落边界（\\n\\n）"""
    nb = text.find('\n\n', rel_pos)
    pb = text.rfind('\n\n', 0, rel_pos)
    if pb >= 0 and nb >= 0:
        return pb if (rel_pos - pb) <= (nb - rel_pos) else nb
    elif pb >= 0:
        return pb
    elif nb >= 0:
        return nb
    return rel_pos


for chunk in parsed.chunks:
    if chunk.index not in chunk_image_map:
        continue

    refs = chunk_image_map[chunk.index]
    section = chunk_to_section(chunk.index)
    body_info = section_bodies.get(section["heading"])
    if not body_info:
        continue

    body_start = body_info["start"]
    body_end = body_info["end"]
    body_text = new_content[body_start:body_end]

    for ref in refs:
        inserted = False

        # ═══ Stage 1: 精确 Figure/Table 编号匹配 ═══
        if ref.fig_num:
            search_patterns = [
                (rf'图\s*{ref.fig_num}\b', False),
                (rf'Figure\s*{ref.fig_num}\b', False),
                (rf'Fig\.?\s*{ref.fig_num}\b', False),
                (rf'表\s*{ref.fig_num}\b', False),
                (rf'Table\s*{ref.fig_num}\b', False),
            ]
            for pattern, _ in search_patterns:
                sec_text = new_content[section["end"]:section["end_pos"]]
                m = re.search(pattern, sec_text, re.IGNORECASE)
                if m:
                    insert_pos = section["end"] + m.start()
                    alt = f"图{ref.fig_num}" if ref.ref_type == "figure" else f"表{ref.fig_num}"
                    img_block = f"\n\n![{alt}](assets/{ref.filename})\n"
                    new_content = new_content[:insert_pos] + img_block + new_content[insert_pos:]
                    update_offsets(insert_pos, len(img_block))
                    body_start = body_info["start"]
                    body_end = body_info["end"]
                    body_text = new_content[body_start:body_end]
                    stage1_count += 1
                    inserted = True
                    print(f"  ✅ Stage1: {ref.filename} → \"{pattern}\" in \"{section['heading']}\"")
                    break

        if inserted:
            continue

        # ═══ Stage 2: 上下文语义匹配 ═══
        ctx = ref.chunk_context.strip()
        if len(ctx) > 20:
            # 提取有意义的短语（大写字母开头的词组）
            keywords = re.findall(r'[A-Z][a-zA-Z]+(?:\s+[a-z]+){1,3}', ctx)
            keywords = [k for k in keywords if len(k) > 5][:5]

            if keywords:
                best_pos = None
                best_score = 0
                for kw in keywords:
                    pos = body_text.find(kw)
                    if pos >= 0:
                        target_ratio = ref.position_ratio
                        score = 10 - abs(pos - int(target_ratio * len(body_text))) / max(len(body_text), 1) * 10
                        if score > best_score:
                            best_score = score
                            best_pos = body_start + pos

                if best_pos and best_score > 5:
                    rel = best_pos - body_start
                    bp = body_start + nearest_para_boundary(body_text, rel) + 2
                    img_block = f"\n\n![论文原图](assets/{ref.filename})\n"
                    new_content = new_content[:bp] + img_block + new_content[bp:]
                    update_offsets(bp, len(img_block))
                    body_start = body_info["start"]
                    body_end = body_info["end"]
                    body_text = new_content[body_start:body_end]
                    stage2_count += 1
                    inserted = True
                    print(f"  ✅ Stage2: {ref.filename} → \"{keywords[0]}\" in \"{section['heading']}\"")
                    continue

        if inserted:
            continue

        # ═══ Stage 3: 比例位置（fallback） ═══
        target_offset = int(ref.position_ratio * len(body_text))
        bp = body_start + nearest_para_boundary(body_text, target_offset) + 2
        alt = f"图{ref.fig_num}" if ref.fig_num else "论文原图"
        img_block = f"\n\n![{alt}](assets/{ref.filename})\n"
        new_content = new_content[:bp] + img_block + new_content[bp:]
        update_offsets(bp, len(img_block))
        body_start = body_info["start"]
        body_end = body_info["end"]
        body_text = new_content[body_start:body_end]
        stage3_count += 1
        print(f"  ✅ Stage3: {ref.filename} @ {ref.position_ratio:.0%} in \"{section['heading']}\"")


# ── 5. 删除 ## 图表资源 画廊 ──
print("\n" + "=" * 60)
print("Step 5: Removing gallery section")

gallery_start = new_content.find("## 图表资源")
if gallery_start >= 0:
    next_h2 = new_content.find("\n## ", gallery_start + 1)
    if next_h2 < 0:
        next_h2 = len(new_content)
    new_content = new_content[:gallery_start] + new_content[next_h2:]
    print("  ✅ Gallery section removed")
else:
    print("  ⏭️  No gallery section found")

# ── 6. 校验 ──
print("\n" + "=" * 60)
print("Verification")

final_refs = re.findall(r'!\[.*?\]\((.*?)\)', new_content)
broken = sum(1 for ref in final_refs if not (ASSETS_DIR / ref.replace("assets/", "")).exists())
has_gallery = "## 图表资源" in new_content

print(f"  Total refs: {len(final_refs)}")
print(f"  Broken: {broken}  All valid: {'✅' if broken == 0 else '❌'}")
print(f"  Has gallery: {'❌' if has_gallery else '✅ Removed'}")
print(f"  Stage1 (exact figure#): {stage1_count}")
print(f"  Stage2 (semantic):      {stage2_count}")
print(f"  Stage3 (proportional):  {stage3_count}")
print(f"  Total:                  {stage1_count + stage2_count + stage3_count}")

if stage1_count + stage2_count + stage3_count > 0:
    bak = MD_PATH.with_suffix(".md.bak5")
    if not bak.exists():
        shutil.copy2(MD_PATH, bak)
        print(f"  Backup: {bak.name}")
    MD_PATH.write_text(new_content)
    print(f"  Written: {MD_PATH}")
