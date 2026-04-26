from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import CandidatePaper
from .utils import ensure_dir


class DownloadError(RuntimeError):
    pass


def _normalize_arxiv_pdf(url: str) -> str:
    if "arxiv.org/abs/" in url and not url.endswith(".pdf"):
        return url.replace("/abs/", "/pdf/") + ".pdf"
    return url


def _best_document_link(page_url: str, html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    page_host = urlparse(page_url).netloc
    pdf_candidates: list[str] = []
    arxiv_candidates: list[str] = []
    for anchor in soup.select("a[href]"):
        href = urljoin(page_url, anchor["href"])
        if href.endswith(".pdf"):
            if urlparse(href).netloc == page_host:
                return href, "pdf"
            pdf_candidates.append(href)
        if "arxiv.org/abs/" in href or "arxiv.org/pdf/" in href:
            arxiv_candidates.append(_normalize_arxiv_pdf(href))
    if pdf_candidates:
        return pdf_candidates[0], "pdf"
    if arxiv_candidates:
        return arxiv_candidates[0], "pdf"
    return page_url, "html"


def resolve_download_target(candidate: CandidatePaper, timeout: int = 30) -> tuple[str, str]:
    paper_url = _normalize_arxiv_pdf(candidate.paper_url)
    if paper_url.endswith(".pdf"):
        return paper_url, "pdf"
    response = requests.get(paper_url, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type:
        return paper_url, "pdf"
    return _best_document_link(paper_url, response.text)


def download_paper(candidate: CandidatePaper, raw_root: Path, timeout: int = 60) -> Path:
    paper_dir = ensure_dir(raw_root / candidate.paper_id)
    target_url, target_type = resolve_download_target(candidate, timeout=timeout)
    suffix = ".pdf" if target_type == "pdf" else ".html"
    output_path = paper_dir / f"paper{suffix}"
    if output_path.exists():
        return output_path

    response = requests.get(target_url, timeout=timeout)
    response.raise_for_status()
    if target_type == "pdf":
        output_path.write_bytes(response.content)
    else:
        output_path.write_text(response.text, encoding="utf-8")
    if output_path.stat().st_size == 0:
        raise DownloadError(f"Downloaded file is empty for {candidate.paper_id}")
    return output_path

