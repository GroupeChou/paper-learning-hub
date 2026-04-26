from __future__ import annotations

from pathlib import Path

import yaml

from .models import (
    AppConfig,
    FeedSource,
    GitSettings,
    Organization,
    SiteSettings,
    Theme,
    TranslatorSettings,
    WorkBuddySettings,
)


def _resolve_path(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return base_dir / path


def load_config(config_path: str | Path) -> AppConfig:
    config_path = Path(config_path).expanduser().resolve()
    base_dir = config_path.parent
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    organizations = [
        Organization(
            name=item["name"],
            priority=item.get("priority", 50),
            aliases=item.get("aliases", []),
            feeds=[FeedSource(name=feed["name"], url=feed["url"]) for feed in item.get("feeds", [])],
        )
        for item in raw.get("organizations", [])
    ]
    themes = [Theme(name=item["name"], keywords=item.get("keywords", [])) for item in raw.get("themes", [])]

    git_settings = GitSettings(**raw.get("git", {}))
    site_raw = raw.get("site", {})
    translator_raw = raw.get("translator", {})
    workbuddy_raw = raw.get("workbuddy", {})

    return AppConfig(
        project_name=raw["project_name"],
        timezone=raw.get("timezone", "UTC"),
        discovery_days=raw.get("discovery_days", 7),
        daily_limit=raw.get("daily_limit", 3),
        raw_dir=_resolve_path(base_dir, raw.get("raw_dir", "papers/raw")),
        zh_dir=_resolve_path(base_dir, raw.get("zh_dir", "papers/zh")),
        database_path=_resolve_path(base_dir, raw.get("database_path", "papers.db")),
        log_dir=_resolve_path(base_dir, raw.get("log_dir", "logs")),
        git=git_settings,
        site=SiteSettings(
            site_name=site_raw.get("site_name", raw["project_name"]),
            site_url=site_raw.get("site_url", ""),
            repo_name=site_raw.get("repo_name", ""),
            docs_dir=_resolve_path(base_dir, site_raw.get("docs_dir", "site/docs")),
            mkdocs_file=_resolve_path(base_dir, site_raw.get("mkdocs_file", "site/mkdocs.yml")),
        ),
        translator=TranslatorSettings(
            backend=translator_raw.get("backend", "mock"),
            base_url=translator_raw.get("base_url", "https://api.openai.com/v1"),
            model=translator_raw.get("model", "gpt-4.1-mini"),
            api_key_env=translator_raw.get("api_key_env", "OPENAI_API_KEY"),
            timeout_seconds=translator_raw.get("timeout_seconds", 120),
            chunk_chars=translator_raw.get("chunk_chars", 5000),
            max_images_per_paper=translator_raw.get("max_images_per_paper", 12),
            system_prompt=translator_raw.get("system_prompt", "").strip(),
        ),
        workbuddy=WorkBuddySettings(
            enabled=workbuddy_raw.get("enabled", False),
            jobs_dir=_resolve_path(base_dir, workbuddy_raw.get("jobs_dir", ".workbuddy/jobs")),
            daily_brief_path=_resolve_path(base_dir, workbuddy_raw.get("daily_brief_path", ".workbuddy/daily-brief.md")),
            task_prompt_path=_resolve_path(base_dir, workbuddy_raw.get("task_prompt_path", ".workbuddy/daily-task.md")),
            memory_dir=_resolve_path(base_dir, workbuddy_raw.get("memory_dir", ".workbuddy/memory")),
            skill_source_dir=_resolve_path(base_dir, workbuddy_raw.get("skill_source_dir", ".workbuddy/skills/paper-learning-hub")),
            installed_skill_path=_resolve_path(
                base_dir, workbuddy_raw.get("installed_skill_path", "~/.workbuddy/skills/paper-learning-hub")
            ),
            project_alias_path=(
                _resolve_path(base_dir, workbuddy_raw["project_alias_path"])
                if workbuddy_raw.get("project_alias_path")
                else None
            ),
            use_symlink_install=workbuddy_raw.get("use_symlink_install", True),
        ),
        themes=themes,
        organizations=organizations,
    )
