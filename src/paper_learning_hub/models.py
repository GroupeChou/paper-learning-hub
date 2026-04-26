from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeedSource:
    name: str
    url: str


@dataclass(slots=True)
class Organization:
    name: str
    priority: int
    aliases: list[str] = field(default_factory=list)
    feeds: list[FeedSource] = field(default_factory=list)


@dataclass(slots=True)
class Theme:
    name: str
    keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GitSettings:
    auto_commit: bool = False
    auto_push: bool = False
    branch: str = "main"
    remote_name: str = "origin"
    commit_prefix: str = "auto: paper hub"


@dataclass(slots=True)
class SiteSettings:
    site_name: str
    site_url: str
    repo_name: str
    docs_dir: Path
    mkdocs_file: Path


@dataclass(slots=True)
class TranslatorSettings:
    backend: str
    base_url: str
    model: str
    api_key_env: str
    timeout_seconds: int
    chunk_chars: int
    max_images_per_paper: int
    system_prompt: str


@dataclass(slots=True)
class WorkBuddySettings:
    enabled: bool
    jobs_dir: Path
    daily_brief_path: Path
    task_prompt_path: Path
    memory_dir: Path
    skill_source_dir: Path
    installed_skill_path: Path
    project_alias_path: Path | None = None
    use_symlink_install: bool = True


@dataclass(slots=True)
class AppConfig:
    project_name: str
    timezone: str
    discovery_days: int
    daily_limit: int
    raw_dir: Path
    zh_dir: Path
    database_path: Path
    log_dir: Path
    git: GitSettings
    site: SiteSettings
    translator: TranslatorSettings
    workbuddy: WorkBuddySettings
    themes: list[Theme]
    organizations: list[Organization]


@dataclass(slots=True)
class CandidatePaper:
    paper_id: str
    title: str
    organization: str
    publish_date: str
    theme: str
    source_name: str
    source_url: str
    paper_url: str
    summary: str
    priority: int
    status: str = "discovered"
    raw_path: str | None = None
    zh_path: str | None = None
    failure_reason: str | None = None
    last_seen_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_row(cls, row: Any) -> "CandidatePaper":
        return cls(
            paper_id=row["paper_id"],
            title=row["title"],
            organization=row["organization"],
            publish_date=row["publish_date"],
            theme=row["theme"],
            source_name=row["source_name"],
            source_url=row["source_url"],
            paper_url=row["paper_url"],
            summary=row["summary"],
            priority=row["priority"],
            status=row["status"],
            raw_path=row["raw_path"],
            zh_path=row["zh_path"],
            failure_reason=row["failure_reason"],
            last_seen_at=row["last_seen_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass(slots=True)
class ParsedChunk:
    index: int
    heading: str
    text: str
    page_start: int
    page_end: int
    needs_review: bool = False


@dataclass(slots=True)
class ParsedDocument:
    source_type: str
    title: str
    text: str
    chunks: list[ParsedChunk]
    image_paths: list[str]
    notes: list[str]


@dataclass(slots=True)
class TranslationChunk:
    heading: str
    content: str
    needs_review: bool = False


@dataclass(slots=True)
class PipelineResult:
    discovered: int = 0
    downloaded: int = 0
    translated: int = 0
    queued: int = 0
    failed: int = 0
    site_built: bool = False
    git_message: str = ""
