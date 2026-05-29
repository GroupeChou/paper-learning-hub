from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from html import unescape
from typing import Iterable
from urllib.parse import urlparse

import feedparser

from .models import AppConfig, CandidatePaper, FeedSource, MajorOrg, Organization, Theme
from .utils import now_iso, sha1_text, shorten_text


ARXIV_ID_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([^/?#]+)")


def _extract_entry_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            return datetime(*parsed[:6])
    return None


def _pick_theme(themes: Iterable[Theme], text: str) -> tuple[str | None, int]:
    lowered = text.lower()
    best_name = None
    best_score = 0
    for theme in themes:
        score = sum(lowered.count(keyword.lower()) for keyword in theme.keywords)
        if score > best_score:
            best_name = theme.name
            best_score = score
    return best_name, best_score


def _extract_paper_link(entry, source_url: str) -> str:
    links = getattr(entry, "links", []) or []
    for link in links:
        href = link.get("href", "")
        if href.endswith(".pdf") or "application/pdf" in link.get("type", ""):
            return href
    href = getattr(entry, "link", "") or source_url
    if "arxiv.org/abs/" in href:
        return href.replace("/abs/", "/pdf/") + ".pdf" if not href.endswith(".pdf") else href
    return href


def _paper_id(link: str, title: str, publish_date: str) -> str:
    match = ARXIV_ID_RE.search(link)
    if match:
        return match.group(1).replace(".pdf", "")
    parsed = urlparse(link)
    if parsed.netloc and parsed.path:
        stable = f"{parsed.netloc}{parsed.path}"
        return sha1_text(stable)[:16]
    return sha1_text(f"{title}|{publish_date}")[:16]


def _priority(org: Organization, theme_score: int, publish_date: str) -> int:
    recency_bonus = 0
    if publish_date:
        age_days = (datetime.now(timezone.utc).date() - datetime.fromisoformat(publish_date).date()).days
        recency_bonus = max(0, 14 - age_days)
    return org.priority * 10 + theme_score * 5 + recency_bonus


def _check_major_org(entry, major_orgs: list[MajorOrg], title: str, summary: str) -> str | None:
    """Check if paper authors belong to a major organization.

    Examines author affiliations from the feed entry. If no affiliation data is available,
    falls back to matching org keywords against the title+abstract.

    Returns:
        Matched major org name, or None if no match found.
    """
    # 1. Check author affiliations from entry data
    authors = getattr(entry, "authors", []) or []
    for author in authors:
        author_name = author.get("name", "")
        author_text = f"{author_name}"
        # arXiv API may include affiliation in author name field like "Author Name (Affiliation)"
        for major_org in major_orgs:
            for keyword in major_org.keywords:
                if keyword.lower() in author_text.lower():
                    return major_org.name

    # 2. Fallback: check title+abstract for org keywords
    combined = f"{title} {summary}"
    for major_org in major_orgs:
        for keyword in major_org.keywords:
            if keyword.lower() in combined.lower():
                return major_org.name

    return None


def discover_candidates(config: AppConfig) -> list[CandidatePaper]:
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=config.discovery_days)
    discovered: dict[str, CandidatePaper] = {}
    seen_at = now_iso(config.timezone)

    for organization in config.organizations:
        for feed in organization.feeds:
            parsed = feedparser.parse(feed.url)
            for entry in parsed.entries:
                entry_date = _extract_entry_date(entry)
                if entry_date and entry_date < cutoff:
                    continue

                title = unescape(getattr(entry, "title", "")).strip()
                summary = shorten_text(unescape(getattr(entry, "summary", "")).replace("<p>", " ").replace("</p>", " "))
                combined = f"{title}\n{summary}"
                theme_name, theme_score = _pick_theme(config.themes, combined)
                if not theme_name:
                    continue

                # 大厂过滤：只保留来自大厂的论文
                matched_org = _check_major_org(entry, config.major_orgs, title, summary)
                if not matched_org:
                    continue

                publish_date = (entry_date.date().isoformat() if entry_date else seen_at[:10])
                source_url = getattr(entry, "link", "") or feed.url
                paper_url = _extract_paper_link(entry, feed.url)
                paper_id = _paper_id(paper_url, title, publish_date)
                candidate = CandidatePaper(
                    paper_id=paper_id,
                    title=title or paper_id,
                    organization=matched_org,  # 使用匹配到的大厂名称
                    publish_date=publish_date,
                    theme=theme_name,
                    source_name=feed.name,
                    source_url=source_url,
                    paper_url=paper_url,
                    summary=summary,
                    priority=_priority(organization, theme_score, publish_date),
                    status="discovered",
                    last_seen_at=seen_at,
                )
                existing = discovered.get(candidate.paper_id)
                if not existing or candidate.priority > existing.priority:
                    discovered[candidate.paper_id] = candidate
    return sorted(discovered.values(), key=lambda item: (item.priority, item.publish_date), reverse=True)
