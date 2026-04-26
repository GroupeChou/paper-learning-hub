from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def now_iso(timezone_name: str = "UTC") -> str:
    return datetime.now(ZoneInfo(timezone_name)).replace(microsecond=0).isoformat()


def today_iso(timezone_name: str = "UTC") -> str:
    return datetime.now(ZoneInfo(timezone_name)).date().isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "paper"


def sha1_text(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def shorten_text(value: str, limit: int = 240) -> str:
    clean = " ".join(value.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def chunk_paragraphs(text: str, max_chars: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return []
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for paragraph in paragraphs:
        addition = len(paragraph) + (2 if current else 0)
        if current and current_length + addition > max_chars:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_length = len(paragraph)
        else:
            current.append(paragraph)
            current_length += addition
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def relative_posix(path: Path, start: Path) -> str:
    return Path(os.path.relpath(path, start)).as_posix()
