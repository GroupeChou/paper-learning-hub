"""ima 知识库同步模块 — 将每日报告和文章同步到 ima 知识库。"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .blog_fetcher import BlogArticle

logger = logging.getLogger(__name__)


def build_ima_sync_payload(
    articles: list[BlogArticle],
    report_path: str,
    date_str: str,
) -> dict:
    """构建 ima 知识库同步的 payload 数据。"""
    # 构建 Markdown 格式的知识条目
    entries = [f"# 前沿 AI 技术日报 · {date_str}\n"]

    from collections import defaultdict
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.org].append(a)

    for org, org_articles in grouped.items():
        entries.append(f"## {org}")
        for a in org_articles:
            zh = a.summary_zh or a.summary_en or ""
            entries.append(f"- **[{a.title}]({a.url})**")
            entries.append(f"  {zh[:200]}")
            entries.append("")
        entries.append("")

    knowledge_content = "\n".join(entries)

    return {
        "title": f"AI技术日报-{date_str}",
        "content": knowledge_content,
        "source": "paper-learning-hub v2.0",
        "report_url": report_path,
        "article_count": len(articles),
        "org_count": len(grouped),
    }


def save_ima_sync_file(payload: dict, output_path: Path) -> Path:
    """保存 ima 同步文件到本地。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
