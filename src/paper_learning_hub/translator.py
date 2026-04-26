from __future__ import annotations

import os
from pathlib import Path

import requests

from .models import AppConfig, CandidatePaper, ParsedDocument, TranslationChunk
from .parser import parse_document
from .utils import ensure_dir, relative_posix, shorten_text


class TranslatorBase:
    def translate_chunk(
        self,
        paper: CandidatePaper,
        chunk_heading: str,
        chunk_text: str,
        parse_notes: list[str],
    ) -> TranslationChunk:
        raise NotImplementedError


class MockTranslator(TranslatorBase):
    def translate_chunk(
        self,
        paper: CandidatePaper,
        chunk_heading: str,
        chunk_text: str,
        parse_notes: list[str],
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
- 当前片段需要在接入真实模型后重新生成。
"""
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
    ) -> TranslationChunk:
        user_prompt = f"""
论文标题：{paper.title}
主题：{paper.theme}
机构：{paper.organization}
章节：{chunk_heading}

请基于以下原文片段输出 Markdown，严格使用下面四个三级标题：
### 中文翻译
### 术语解释
### 图表/公式说明
### 关键 takeaway

要求：
1. 用中文输出，保留必要英文术语。
2. 如果有无法确认的内容，请显式写“待复核”。
3. 不要省略公式和关键术语。
4. 结合解析备注处理图表与公式说明：{"；".join(parse_notes) if parse_notes else "无"}

原文片段：
{chunk_text}
""".strip()
        response = requests.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": self.settings.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
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

- 机构：{paper.organization}
- 主题：{paper.theme}
- 发布日期：{paper.publish_date}
- 来源：[{paper.source_name}]({paper.source_url})
- 论文链接：[{paper.paper_url}]({paper.paper_url})
- 状态：{'待复核' if parsed.notes else '已生成'}

## 摘要

{paper.summary}

{parse_notes}{images}"""


def translate_paper(config: AppConfig, paper: CandidatePaper, raw_path: Path) -> Path:
    zh_dir = ensure_dir(config.zh_dir / paper.paper_id)
    translator = create_translator(config)
    parsed = parse_document(raw_path, zh_dir, config.translator.chunk_chars, config.translator.max_images_per_paper)
    sections = []
    needs_review = bool(parsed.notes)
    for chunk in parsed.chunks:
        translated = translator.translate_chunk(paper, chunk.heading, chunk.text, parsed.notes)
        needs_review = needs_review or translated.needs_review or chunk.needs_review
        review_block = "> 待复核：该片段的文本提取或翻译结果置信度偏低。\n\n" if translated.needs_review or chunk.needs_review else ""
        sections.append(f"## {chunk.heading}\n\n{review_block}{translated.content.strip()}\n")

    header = _paper_header(paper, parsed, zh_dir / "assets", config.zh_dir)
    footer = "\n## 复核建议\n\n- 对关键公式、表格和实验结论做抽样核对。\n- 如已接入真实模型，可重新运行该论文以覆盖 mock 内容。\n"
    if not needs_review:
        footer = "\n## 复核建议\n\n- 当前未发现明显的解析降级信号，仍建议抽样检查图表和公式。\n"
    output_path = zh_dir / "paper_zh.md"
    output_path.write_text(header + "\n".join(sections) + footer, encoding="utf-8")
    return output_path

