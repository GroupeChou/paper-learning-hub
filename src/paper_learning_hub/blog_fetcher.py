"""每日从 5 个官方博客抓取最新文章，生成结构化数据。

数据源分层：
  - 直连层：RSS / arXiv / sitemap → 直接抓取
  - 搜索层：JS 渲染站点 → 通过 WorkBuddy WebSearch 预填 JSON 缓存
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import feedparser
import requests

logger = logging.getLogger(__name__)

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# ---- 5 个核心订阅源 ----
BLOG_SOURCES = [
    {"org": "Anthropic",  "type": "anthropic", "color": "#D97757",
     "url": "https://www.anthropic.com/research",
     "search_query": "site:anthropic.com/research latest 2026", "limit": 6},
    {"org": "OpenAI",     "type": "openai",    "color": "#000000",
     "url": "https://openai.com/research",
     "search_query": "site:openai.com/index latest 2026 research", "limit": 6},
    {"org": "Google DeepMind", "type": "rss", "color": "#4285F4",
     "url": "https://blog.google/technology/ai/rss/", "limit": 6},
    {"org": "Meta",       "type": "meta",      "color": "#0668E1",
     "url": "https://ai.meta.com/blog/",
     "search_query": "site:ai.meta.com/blog latest 2026", "limit": 6},
    {"org": "DeepSeek",   "type": "arxiv",     "color": "#4F46E5",
     "url": "https://export.arxiv.org/api/query"
            "?search_query=all:DeepSeek&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending",
     "limit": 6},
]

# 搜索层源（需要 WorkBuddy WebSearch 预填）— JS 渲染站点
SEARCH_LAYER_SOURCES = {"anthropic", "openai", "meta"}

# 搜索结果缓存文件
_SEARCH_CACHE_FILE = ".websearch-cache.json"


@dataclass
class BlogArticle:
    id: str
    org: str
    org_color: str
    title: str
    url: str
    summary_en: str
    summary_zh: str = ""
    published: str = ""
    author: str = ""
    category: str = ""
    translated: bool = False


# ============================================================
# 主入口
# ============================================================

def fetch_blog_articles(
    max_per_source: int = 5,
    search_cache_dir: Optional[Path] = None
) -> list[BlogArticle]:
    """从 5 个博客源抓取最新文章。

    对于 JS 渲染站点（Anthropic / OpenAI / Meta），优先读取
    .websearch-cache.json（由 WorkBuddy WebSearch 预填）。
    如果缓存不存在，尝试直接抓取并返回结果。
    """
    all_articles: list[BlogArticle] = []

    # 加载搜索缓存
    search_cache = _load_search_cache(search_cache_dir or Path("."))

    for src in BLOG_SOURCES:
        try:
            limit = src.get("limit", max_per_source)
            fetch_type = src["type"]

            # 搜索层源：优先使用缓存
            if fetch_type in SEARCH_LAYER_SOURCES:
                cache_articles = _use_search_cache(src, search_cache, limit)
                if cache_articles:
                    all_articles.extend(cache_articles)
                    logger.info(f"  {src['org']}: {len(cache_articles)} 篇 (来自搜索缓存)")
                    continue
                # 缓存缺失 → 尝试直连
                articles = _fetch_direct(src, fetch_type, limit)
                if articles:
                    all_articles.extend(articles)
                    logger.info(f"  {src['org']}: {len(articles)} 篇 (直连抓取)")
                else:
                    all_articles.append(_search_placeholder(src))
                    logger.info(f"  {src['org']}: 0 篇 (需 WebSearch 补充)")
            else:
                # 直连层源
                articles = _fetch_direct(src, fetch_type, limit)
                all_articles.extend(articles)
                logger.info(f"  {src['org']}: {len(articles)} 篇")

        except Exception as e:
            logger.warning(f"  {src['org']}: 抓取失败 - {e}")
            all_articles.append(_search_placeholder(src))

    return all_articles


# ============================================================
# 直连抓取（RSS / arXiv）
# ============================================================

def _fetch_direct(src: dict, fetch_type: str, limit: int) -> list[BlogArticle]:
    """直连抓取分发。"""
    if fetch_type == "rss":
        return _fetch_rss(src, limit)
    elif fetch_type == "arxiv":
        return _fetch_arxiv(src, limit)
    return []


def _fetch_rss(src: dict, limit: int) -> list[BlogArticle]:
    feed = feedparser.parse(src["url"])
    articles = []
    for entry in feed.entries[:limit]:
        published = ""
        for attr in ("published_parsed", "updated_parsed"):
            val = getattr(entry, attr, None)
            if val:
                published = datetime(*val[:6], tzinfo=timezone.utc).isoformat()
                break

        summary_en = re.sub(r"<[^>]+>", "", getattr(entry, "summary", ""))[:500]
        articles.append(BlogArticle(
            id=hashlib.md5(entry.link.encode()).hexdigest()[:12],
            org=src["org"], org_color=src["color"],
            title=re.sub(r"\s+", " ", entry.title).strip(),
            url=entry.link, summary_en=summary_en,
            published=published, author=getattr(entry, "author", ""),
        ))
    return articles


def _fetch_arxiv(src: dict, limit: int) -> list[BlogArticle]:
    feed = feedparser.parse(src["url"])
    articles = []
    for entry in feed.entries[:limit]:
        title = re.sub(r"\s+", " ", entry.get("title", "")).strip()
        url = entry.get("id", "")
        published = entry.get("published", "")
        summary_en = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:400]
        articles.append(BlogArticle(
            id=hashlib.md5(url.encode()).hexdigest()[:12],
            org=src["org"], org_color=src["color"],
            title=title, url=url, summary_en=summary_en,
            published=published,
        ))
    return articles


# ============================================================
# 搜索缓存（JS 渲染站点 → 由 WorkBuddy WebSearch 预填）
# ============================================================

def _load_search_cache(cache_dir: Path) -> dict[str, list[dict]]:
    """从 .websearch-cache.json 加载搜索结果。"""
    cache_path = cache_dir / _SEARCH_CACHE_FILE
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _use_search_cache(
    src: dict, cache: dict[str, list[dict]], limit: int
) -> list[BlogArticle]:
    """从缓存中提取指定机构的文章。"""
    org = src["org"]
    items = cache.get(org, [])
    if not items:
        return []

    articles = []
    seen = set()
    for item in items[:limit]:
        url = item.get("url", "")
        if url in seen:
            continue
        seen.add(url)

        articles.append(BlogArticle(
            id=hashlib.md5(url.encode()).hexdigest()[:12],
            org=org, org_color=src["color"],
            title=item.get("title", ""),
            url=url,
            summary_en=item.get("snippet", item.get("title", "")),
            published=item.get("published", ""),
        ))
    return articles


def _search_placeholder(src: dict) -> BlogArticle:
    """生成搜索占位条目 → 触发 WorkBuddy WebSearch。"""
    return BlogArticle(
        id=hashlib.md5(src["url"].encode()).hexdigest()[:12],
        org=src["org"], org_color=src["color"],
        title=f"🔍 {src['org']} — 搜索: {src.get('search_query', '')}",
        url=src["url"],
        summary_en=f"需要在 WorkBuddy 中执行 WebSearch: {src.get('search_query', '')}",
    )


def build_search_queries() -> list[dict]:
    """生成所有搜索层源的搜索查询（供 WorkBuddy 使用）。"""
    queries = []
    for src in BLOG_SOURCES:
        if src["type"] in SEARCH_LAYER_SOURCES:
            queries.append({
                "org": src["org"],
                "query": src.get("search_query", ""),
                "color": src["color"],
                "limit": src.get("limit", 5),
            })
    return queries


def save_search_cache(
    articles_by_org: dict[str, list[dict]], cache_dir: Path
) -> Path:
    """将搜索结果保存为 .websearch-cache.json。"""
    cache_path = cache_dir / _SEARCH_CACHE_FILE
    cache_path.write_text(
        json.dumps(articles_by_org, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return cache_path


# ============================================================
# 翻译 & 存储
# ============================================================

def generate_chinese_summaries(
    articles: list[BlogArticle],
    translator_func=None,
    api_key: str = "",
) -> list[BlogArticle]:
    for a in articles:
        if a.translated:
            continue
        if translator_func and api_key:
            try:
                zh = translator_func(a.title, a.summary_en or a.title, api_key)
                a.summary_zh = zh
                a.translated = True
            except Exception as e:
                logger.warning(f"  翻译失败 {a.title[:40]}: {e}")
                a.summary_zh = f"[翻译待补] {a.title}"
        else:
            a.summary_zh = f"[待翻译] {a.title}"
    return articles


def save_articles_json(articles: list[BlogArticle], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(a) for a in articles]
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def load_articles_json(json_path: Path) -> list[BlogArticle]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return [BlogArticle(**item) for item in data]
