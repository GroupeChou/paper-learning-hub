from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from .models import AppConfig, CandidatePaper, ParsedDocument, TranslationChunk
from .parser import parse_document
from .utils import ensure_dir, relative_posix, shorten_text


def _image_to_base64(image_path: str) -> str:
    """Read an image file and return a data URI string."""
    path = Path(image_path)
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/png")
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


class TranslatorBase:
    def translate_chunk(
        self,
        paper: CandidatePaper,
        chunk_heading: str,
        chunk_text: str,
        parse_notes: list[str],
        image_data_uris: list[str] | None = None,
    ) -> TranslationChunk:
        raise NotImplementedError


class MockTranslator(TranslatorBase):
    def translate_chunk(
        self,
        paper: CandidatePaper,
        chunk_heading: str,
        chunk_text: str,
        parse_notes: list[str],
        image_data_uris: list[str] | None = None,
    ) -> TranslationChunk:
        summary = shorten_text(chunk_text, limit=500)
        content = f"""### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

{summary}

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：{"；".join(parse_notes) if parse_notes else "无"}

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。"""
        return TranslationChunk(heading=chunk_heading, content=content, needs_review=True)


class OpenAICompatibleTranslator(TranslatorBase):
    def __init__(self, settings):
        self.settings = settings
        api_key = os.environ.get(settings.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env: {settings.api_key_env}")
        self.api_key = api_key

    def translate_chunk(
        self,
        paper: CandidatePaper,
        chunk_heading: str,
        chunk_text: str,
        parse_notes: list[str],
        image_data_uris: list[str] | None = None,
    ) -> TranslationChunk:
        # Build user message content — text + optional images
        user_text = f"""
论文标题：{paper.title}
主题：{paper.theme}
机构：{paper.organization}
章节：{chunk_heading}

## 任务要求
请对以下原文片段进行**逐字逐句的中文全翻译和扩展解读**。

### 核心要求
1. **逐句翻译**：每一句话都翻译为中文，不遗漏任何句子，包括脚注和附录
2. **内容扩展**：在翻译基础上添加逻辑衔接说明、背景补充、作者意图分析
3. **图片/表格完整保留**：以下附带了本章节对应的论文原图。请仔细观察每张图片的内容（图表、截图、示意图等），在翻译到相关段落时引用并详细描述这些图片
4. **公式保留+解释**：原文中的公式可能因PDF解析而残缺，请根据上下文和你的知识**还原正确的 LaTeX 公式**，并标注`（根据上下文还原）`，然后附变量含义和直觉解释
5. **表格还原**：原文中的表格可能已丢失行列结构，请根据上下文尽可能还原为 Markdown 表格格式
6. **输出量要求**：中文字数应 ≥ 原文字数的 1.5 倍

### 输出格式（严格使用以下四个三级标题）
### 中文翻译
### 术语解释
### 图表/公式说明
### 关键 takeaway

### 解析备注（辅助理解原文结构）
{"；".join(parse_notes) if parse_notes else "无"}

## 原文片段（请逐句翻译，不要省略任何内容）
{chunk_text}
""".strip()

        # Build message content array
        content_parts: list[dict] = [{"type": "text", "text": user_text}]

        # Attach images as vision input (max 6 per chunk to avoid token blowup)
        if image_data_uris:
            for uri in image_data_uris[:6]:
                if uri:
                    content_parts.append({"type": "image_url", "image_url": {"url": uri}})

        messages = [
            {"role": "system", "content": self.settings.system_prompt},
            {"role": "user", "content": content_parts},
        ]

        response = requests.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.model,
                "temperature": 0.2,
                "messages": messages,
                "max_tokens": 16384,
            },
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        needs_review = "待复核" in content
        return TranslationChunk(heading=chunk_heading, content=content, needs_review=needs_review)


def create_translator(config: AppConfig) -> TranslatorBase:
    if config.translator.backend == "openai_compatible":
        try:
            return OpenAICompatibleTranslator(config.translator)
        except RuntimeError:
            return MockTranslator()
    return MockTranslator()


def _paper_header(paper: CandidatePaper, parsed: ParsedDocument, assets_dir: Path, zh_root: Path) -> str:
    images = ""
    if parsed.image_paths:
        lines = ["## 图表资源"]
        for image in parsed.image_paths:
            rel = relative_posix(assets_dir / Path(image).name, zh_root / paper.paper_id)
            lines.append(f"- ![]({rel})")
        images = "\n".join(lines) + "\n\n"

    parse_notes = ""
    if parsed.notes:
        parse_notes = "## 解析备注\n\n" + "\n".join(f"- {note}" for note in parsed.notes) + "\n\n"

    return f"""# {paper.title}

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-{paper.organization}">{paper.organization}</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">{paper.theme}</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">{paper.publish_date}</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[{paper.source_name}]({paper.source_url})
- **论文链接**：[{paper.paper_url}]({paper.paper_url})
- **状态**：{'待复核' if parsed.notes else '已生成'}

## 摘要

{paper.summary}

{parse_notes}{images}"""


def translate_paper(config: AppConfig, paper: CandidatePaper, raw_path: Path) -> Path:
    zh_dir = ensure_dir(config.zh_dir / paper.paper_id)
    translator = create_translator(config)
    parsed = parse_document(raw_path, zh_dir, config.translator.chunk_chars, config.translator.max_images_per_paper)
    sections = []
    needs_review = bool(parsed.notes)

    # Build a lookup: page_number -> [data URIs]
    page_image_uris: dict[int, list[str]] = {}
    for page_num, img_paths in parsed.page_images.items():
        uris = [_image_to_base64(p) for p in img_paths]
        page_image_uris[page_num] = [u for u in uris if u]

    for chunk in parsed.chunks:
        # Collect images from all pages this chunk spans
        chunk_images: list[str] = []
        seen: set[str] = set()
        for page_num in chunk.page_refs:
            for uri in page_image_uris.get(page_num, []):
                if uri not in seen:
                    chunk_images.append(uri)
                    seen.add(uri)

        translated = translator.translate_chunk(
            paper, chunk.heading, chunk.text, parsed.notes, image_data_uris=chunk_images or None
        )
        needs_review = needs_review or translated.needs_review or chunk.needs_review
        review_block = (
            "> 待复核：该片段的文本提取或翻译结果置信度偏低。\n\n"
            if translated.needs_review or chunk.needs_review
            else ""
        )
        sections.append(f"## {chunk.heading}\n\n{review_block}{translated.content.strip()}\n")

    header = _paper_header(paper, parsed, zh_dir / "assets", config.zh_dir)
    footer = "\n## 复核建议\n\n- 对关键公式、表格和实验结论做抽样核对。\n- 如已接入真实模型，可重新运行该论文以覆盖 mock 内容。\n"
    if not needs_review:
        footer = "\n## 复核建议\n\n- 当前未发现明显的解析降级信号，仍建议抽样检查图表和公式。\n"
    output_path = zh_dir / "paper_zh.md"
    output_path.write_text(header + "\n".join(sections) + footer, encoding="utf-8")
    return output_path
