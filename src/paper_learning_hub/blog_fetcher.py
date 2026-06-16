"""每日从 5 个官方博客抓取最新文章，生成结构化数据。"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import feedparser
import requests

logger = logging.getLogger(__name__)

# ---- 5 个核心订阅源 ----
# 注：大部分官方博客不暴露 RSS，使用页面抓取或 Web Search 作为数据源。
BLOG_SOURCES = [
    {
        "org": "Anthropic",
        "name": "Anthropic Research",
        "url": "https://www.anthropic.com/research",
        "type": "webpage",
        "color": "#D97757",
        "search_query": "Anthropic research blog latest articles",
    },
    {
        "org": "OpenAI",
        "name": "OpenAI Research",
        "url": "https://openai.com/research",
        "type": "webpage",
        "color": "#000000",
        "search_query": "OpenAI research blog latest articles 2026",
    },
    {
        "org": "Google DeepMind",
        "name": "DeepMind Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "type": "rss",
        "color": "#4285F4",
    },
    {
        "org": "Meta",
        "name": "Meta AI Blog",
        "url": "https://ai.meta.com/blog/",
        "type": "webpage",
        "color": "#0668E1",
        "search_query": "Meta AI research blog latest articles 2026",
    },
    {
        "org": "DeepSeek",
        "name": "DeepSeek Blog",
        "url": "https://api.github.com/repos/deepseek-ai/DeepSeek-V3/releases",
        "type": "github_releases",
        "color": "#4F46E5",
    },
]


@dataclass
class BlogArticle:
    """一篇来自官方博客的文章"""
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

    @property
    def content_hash(self) -> str:
        return hashlib.md5(f"{self.url}{self.title}".encode()).hexdigest()[:12]


def fetch_blog_articles(max_per_source: int = 5) -> list[BlogArticle]:
    """从 5 个博客源抓取最新文章。"""
    articles: list[BlogArticle] = []
    for src in BLOG_SOURCES:
        try:
            if src["type"] == "rss":
                fetched = _fetch_rss(src, max_per_source)
            elif src["type"] == "webpage":
                fetched = _fetch_webpage(src, max_per_source)
            elif src["type"] == "github_releases":
                fetched = _fetch_github_releases_simple(src, max_per_source)
            else:
                fetched = []
            articles.extend(fetched)
            logger.info(f"  {src['org']}: {len(fetched)} 篇")
        except Exception as e:
            logger.warning(f"  {src['org']}: 抓取失败 - {e}")
    return articles


def _fetch_rss(src: dict, limit: int) -> list[BlogArticle]:
    """抓取 RSS feed。"""
    try:
        resp = requests.get(src["url"], timeout=15, headers={"User-Agent": "PaperHub/2.0"})
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception:
        # fallback: direct URL fetch
        feed = feedparser.parse(src["url"])

    articles = []
    for entry in feed.entries[:limit]:
        published = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()

        summary_en = ""
        if hasattr(entry, "summary"):
            # strip HTML tags
            import re
            summary_en = re.sub(r"<[^>]+>", "", entry.summary)[:500]

        articles.append(BlogArticle(
            id=hashlib.md5(entry.link.encode()).hexdigest()[:12],
            org=src["org"],
            org_color=src["color"],
            title=entry.title.strip(),
            url=entry.link,
            summary_en=summary_en,
            published=published,
            author=getattr(entry, "author", ""),
        ))
    return articles


def _fetch_webpage(src: dict, limit: int) -> list[BlogArticle]:
    """从网页抓取文章列表（解析 HTML 中的标题和链接）。"""
    import re

    articles = []
    url = src["url"]
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PaperHub/2.0",
            "Accept": "text/html,application/xhtml+xml",
        })
        resp.raise_for_status()
        html = resp.text

        # Extract article links using common blog patterns
        # Look for <a> tags with article-like hrefs and parent elements
        link_pattern = re.findall(
            r'<a[^>]+href="(https?://[^"]*(?:blog|research|articles)[^"]*)"[^>]*>(.*?)</a>',
            html, re.IGNORECASE | re.DOTALL
        )

        # Try structured data approach first
        article_links = re.findall(
            r'<article[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            html, re.IGNORECASE | re.DOTALL
        )

        # Fallback: find all links that look like blog posts
        if not article_links:
            article_links = re.findall(
                r'href="(https?://[^"]*(?:research|blog)[^"]*)"[^>]*>(.{10,200}?)<',
                html, re.IGNORECASE
            )

        seen = set()
        for href, title_raw in (article_links or link_pattern)[:limit]:
            title_clean = re.sub(r"<[^>]+>", "", title_raw).strip()
            if not title_clean or len(title_clean) < 10:
                continue
            if href in seen:
                continue
            seen.add(href)

            articles.append(BlogArticle(
                id=hashlib.md5(href.encode()).hexdigest()[:12],
                org=src["org"],
                org_color=src["color"],
                title=title_clean,
                url=href,
                summary_en=title_clean,
                published="",
            ))

    except Exception as e:
        logger.warning(f"  {src['org']} webpage 抓取失败: {e}")
        # 提供占位条目，后续由 WorkBuddy 通过 WebSearch 补充
        articles.append(BlogArticle(
            id=hashlib.md5(src["url"].encode()).hexdigest()[:12],
            org=src["org"],
            org_color=src["color"],
            title=f"{src['org']} - 今日文章（需通过搜索补充）",
            url=src["url"],
            summary_en=f"访问 {src['url']} 查看最新文章",
        ))

    return articles[:limit]


def _fetch_github_releases_simple(src: dict, limit: int) -> list[BlogArticle]:
    """从 GitHub Releases API 抓取 DeepSeek 最新发布。"""
    articles = []
    try:
        resp = requests.get(src["url"] + "?per_page=5", timeout=15, headers={"Accept": "application/vnd.github+json"})
        resp.raise_for_status()
        releases = resp.json()
        for rel in releases[:limit]:
            articles.append(BlogArticle(
                id=hashlib.md5((src["org"] + rel.get("tag_name", "")).encode()).hexdigest()[:12],
                org=src["org"],
                org_color=src["color"],
                title=rel.get("name", "Release"),
                url=rel.get("html_url", src["url"]),
                summary_en=(rel.get("body") or "Release notes")[:300],
                published=rel.get("published_at", ""),
            ))
    except Exception as e:
        logger.warning(f"  DeepSeek releases 抓取失败: {e}")
    return articles


def generate_chinese_summaries(
    articles: list[BlogArticle],
    translator_func=None,
    api_key: str = "",
) -> list[BlogArticle]:
    """
    为文章生成中文摘要。需要 translator_func(title, summary_en) -> zh_summary。
    如果未提供 translator，返回原文作为占位。
    """
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
    """保存文章数据为 JSON。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(a) for a in articles]
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def load_articles_json(json_path: Path) -> list[BlogArticle]:
    """从 JSON 加载文章数据。"""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return [BlogArticle(**item) for item in data]
