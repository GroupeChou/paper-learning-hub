from __future__ import annotations

import logging
import re
from pathlib import Path

import fitz
import requests
from bs4 import BeautifulSoup

from .models import ParsedChunk, ParsedDocument
from .utils import chunk_paragraphs, ensure_dir

logger = logging.getLogger(__name__)

# Regex to find page markers like [Page 1], [Page 12]
_PAGE_MARKER_RE = re.compile(r"\[Page (\d+)\]")


def _parse_page_refs(text: str) -> list[int]:
    """Extract unique PDF page numbers from chunk text containing [Page N] markers."""
    pages = sorted({int(m) for m in _PAGE_MARKER_RE.findall(text)})
    return pages if pages else [1]


def _chunk_text(text: str, max_chars: int) -> list[ParsedChunk]:
    raw_chunks = chunk_paragraphs(text, max_chars=max_chars)
    parsed_chunks: list[ParsedChunk] = []
    for index, chunk in enumerate(raw_chunks, start=1):
        heading = f"Section {index}"
        first_line = chunk.splitlines()[0].strip()
        if len(first_line) < 90 and re.match(r"^([A-Z][A-Za-z0-9 .:-]+|\d+(\.\d+)*)$", first_line):
            heading = first_line
        needs_review = len(chunk) < 120 or chunk.count("\n") < 2
        page_refs = _parse_page_refs(chunk)
        parsed_chunks.append(
            ParsedChunk(
                index=index,
                heading=heading,
                text=chunk,
                page_start=page_refs[0] if page_refs else 1,
                page_end=page_refs[-1] if page_refs else 1,
                needs_review=needs_review,
                page_refs=page_refs,
            )
        )
    return parsed_chunks


def _parse_pdf(raw_path: Path, assets_dir: Path, max_chars: int, max_images: int) -> ParsedDocument:
    doc = fitz.open(raw_path)
    ensure_dir(assets_dir)
    notes: list[str] = []
    all_image_paths: list[str] = []
    page_texts: list[str] = []
    image_count = 0

    # Map page_number -> list of extracted image paths on that page
    page_images: dict[int, list[str]] = {}

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if page_text:
            page_texts.append(f"[Page {page_number}]\n{page_text}")

        page_imgs: list[str] = []
        for image_index, image in enumerate(page.get_images(full=True), start=1):
            if image_count >= max_images:
                if image_count == max_images:
                    notes.append(f"图片数量超过上限，仅保留前 {max_images} 张。")
                break
            xref = image[0]
            extracted = doc.extract_image(xref)
            ext = extracted.get("ext", "png")
            image_name = f"page-{page_number:03d}-img-{image_index:02d}.{ext}"
            image_path = assets_dir / image_name
            image_path.write_bytes(extracted["image"])
            rel_path = f"assets/{image_name}"
            all_image_paths.append(rel_path)
            page_imgs.append(str(image_path))
            image_count += 1
        if page_imgs:
            page_images[page_number] = page_imgs

    text = "\n\n".join(page_texts).strip()
    if not text:
        notes.append("PDF 文本提取结果为空，需要人工复核。")
    chunks = _chunk_text(text, max_chars=max_chars)

    # Attach page-specific images to each chunk
    for chunk in chunks:
        chunk.page_refs = _parse_page_refs(chunk.text)

    return ParsedDocument(
        source_type="pdf",
        title=raw_path.stem,
        text=text,
        chunks=chunks,
        image_paths=all_image_paths,
        notes=notes,
        page_images=page_images,  # pass through to translator
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
        page_images={},
    )


def parse_document(raw_path: Path, translated_dir: Path, max_chars: int, max_images: int) -> ParsedDocument:
    assets_dir = ensure_dir(translated_dir / "assets")
    if raw_path.suffix.lower() == ".pdf":
        return _parse_pdf(raw_path, assets_dir, max_chars, max_images)
    return _parse_html(raw_path, max_chars)


def parse_document_from_arxiv(arxiv_id: str, translated_dir: Path, max_chars: int) -> ParsedDocument:
    """Fetch paper HTML from arXiv/ar5iv and parse into a ParsedDocument.

    Tries two sources in order:
    1. https://arxiv.org/html/{arxiv_id}  — arXiv native HTML (full text, best quality)
    2. https://ar5iv.labs.arxiv.org/html/{arxiv_id} — ar5iv HTML conversion (fallback)

    Args:
        arxiv_id: arXiv paper ID (e.g. "2605.18703v1").
        translated_dir: Target directory for the translation output.
        max_chars: Max characters per chunk for text chunking.

    Returns:
        ParsedDocument with source_type="html" and extracted section text.
    """
    sources = [
        ("arXiv HTML", f"https://arxiv.org/html/{arxiv_id}"),
        ("ar5iv", f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"),
    ]
    ensure_dir(translated_dir / "assets")
    notes: list[str] = []
    html_content: str | None = None
    used_source = ""

    for source_name, url in sources:
        try:
            logger.info("Fetching paper from %s: %s", source_name, url)
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                logger.warning("%s returned %s for %s, trying next source", source_name, response.status_code, arxiv_id)
                continue
            response.encoding = "utf-8"

            # Quick check: does the page contain substantial paper content?
            text_len = len(response.text)
            soup_check = BeautifulSoup(response.text, "html.parser")
            body_text = soup_check.get_text()
            # Skip if it's just the abstract page (no full paper sections)
            if body_text.count("\n") < 30 or len(body_text) < 5000:
                logger.info("%s page too short (%d chars), may be abstract-only, trying next source", source_name, len(body_text))
                continue

            html_content = response.text
            used_source = source_name
            break
        except requests.RequestException as exc:
            logger.warning("Failed to fetch from %s: %s, trying next source", source_name, exc)
            continue

    if html_content is None:
        raise requests.RequestException(
            f"All sources failed for {arxiv_id}. "
            "The paper may be too new or temporarily unavailable."
        )

    soup = BeautifulSoup(html_content, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else arxiv_id

    # Extract text from the paper's section content
    text_parts: list[str] = []
    for tag_name in ["section", "article", "div"]:
        content = soup.find(tag_name, class_=lambda c: c and "content" in c.lower() if c else False)
        if content:
            break

    # If no specific content container found, extract from main content-bearing tags
    for tag in soup.select("h1, h2, h3, h4, h5, h6, p, li"):
        tag_text = tag.get_text(" ", strip=True)
        if not tag_text or len(tag_text) < 3:
            continue
        tag_name = tag.name
        if tag_name.startswith("h"):
            text_parts.append(f"\n## {tag_text}\n")
        else:
            text_parts.append(tag_text)

    text = "\n\n".join(text_parts).strip()
    if not text:
        notes.append(f"{used_source} 文本提取结果为空，可能需要人工处理。")

    chunks = _chunk_text(text, max_chars=max_chars)

    return ParsedDocument(
        source_type="html",
        title=title,
        text=text,
        chunks=chunks,
        image_paths=[],
        notes=notes + [f"来自 {used_source} HTML 解析，无图片/公式渲染信息。"],
        page_images={},
    )
