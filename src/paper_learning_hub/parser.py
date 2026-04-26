from __future__ import annotations

import re
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

from .models import ParsedChunk, ParsedDocument
from .utils import chunk_paragraphs, ensure_dir


def _chunk_text(text: str, max_chars: int) -> list[ParsedChunk]:
    raw_chunks = chunk_paragraphs(text, max_chars=max_chars)
    parsed_chunks: list[ParsedChunk] = []
    for index, chunk in enumerate(raw_chunks, start=1):
        heading = f"Section {index}"
        first_line = chunk.splitlines()[0].strip()
        if len(first_line) < 90 and re.match(r"^([A-Z][A-Za-z0-9 .:-]+|\d+(\.\d+)*)$", first_line):
            heading = first_line
        needs_review = len(chunk) < 120 or chunk.count("\n") < 2
        parsed_chunks.append(
            ParsedChunk(index=index, heading=heading, text=chunk, page_start=index, page_end=index, needs_review=needs_review)
        )
    return parsed_chunks


def _parse_pdf(raw_path: Path, assets_dir: Path, max_chars: int, max_images: int) -> ParsedDocument:
    doc = fitz.open(raw_path)
    ensure_dir(assets_dir)
    notes: list[str] = []
    image_paths: list[str] = []
    page_texts: list[str] = []
    image_count = 0

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if page_text:
            page_texts.append(f"[Page {page_number}]\n{page_text}")
        for image_index, image in enumerate(page.get_images(full=True), start=1):
            if image_count >= max_images:
                notes.append(f"图片数量超过上限，仅保留前 {max_images} 张。")
                break
            xref = image[0]
            extracted = doc.extract_image(xref)
            ext = extracted.get("ext", "png")
            image_name = f"page-{page_number:03d}-img-{image_index:02d}.{ext}"
            image_path = assets_dir / image_name
            image_path.write_bytes(extracted["image"])
            image_paths.append(f"assets/{image_name}")
            image_count += 1

    text = "\n\n".join(page_texts).strip()
    if not text:
        notes.append("PDF 文本提取结果为空，需要人工复核。")
    return ParsedDocument(
        source_type="pdf",
        title=raw_path.stem,
        text=text,
        chunks=_chunk_text(text, max_chars=max_chars),
        image_paths=image_paths,
        notes=notes,
    )


def _parse_html(raw_path: Path, max_chars: int) -> ParsedDocument:
    html = raw_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else raw_path.stem
    text = "\n\n".join(element.get_text(" ", strip=True) for element in soup.select("p, h1, h2, h3, li"))
    return ParsedDocument(
        source_type="html",
        title=title,
        text=text,
        chunks=_chunk_text(text, max_chars=max_chars),
        image_paths=[],
        notes=["HTML 模式暂不下载远端图片，仅保留文本结构。"],
    )


def parse_document(raw_path: Path, translated_dir: Path, max_chars: int, max_images: int) -> ParsedDocument:
    assets_dir = ensure_dir(translated_dir / "assets")
    if raw_path.suffix.lower() == ".pdf":
        return _parse_pdf(raw_path, assets_dir, max_chars, max_images)
    return _parse_html(raw_path, max_chars)

