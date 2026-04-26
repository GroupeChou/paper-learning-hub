from __future__ import annotations

from pathlib import Path

import yaml


def write_test_config(project_root: Path, *, backend: str = "mock") -> Path:
    config = {
        "project_name": "test-hub",
        "timezone": "Asia/Shanghai",
        "discovery_days": 14,
        "daily_limit": 2,
        "raw_dir": "papers/raw",
        "zh_dir": "papers/zh",
        "database_path": "papers.db",
        "log_dir": "logs",
        "git": {
            "auto_commit": True,
            "auto_push": True,
            "branch": "main",
            "remote_name": "origin",
            "commit_prefix": "auto: test",
        },
        "site": {
            "site_name": "Test Hub",
            "site_url": "",
            "repo_name": "",
            "docs_dir": "site/docs",
            "mkdocs_file": "site/mkdocs.yml",
        },
        "translator": {
            "backend": backend,
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4.1-mini",
            "api_key_env": "OPENAI_API_KEY",
            "timeout_seconds": 30,
            "chunk_chars": 600,
            "max_images_per_paper": 3,
            "system_prompt": "test prompt",
        },
        "workbuddy": {
            "enabled": True,
            "jobs_dir": ".workbuddy/jobs",
            "daily_brief_path": ".workbuddy/daily-brief.md",
            "task_prompt_path": ".workbuddy/daily-task.md",
            "memory_dir": ".workbuddy/memory",
            "skill_source_dir": ".workbuddy/skills/paper-learning-hub",
            "installed_skill_path": str(project_root / ".wb-installed" / "paper-learning-hub"),
            "use_symlink_install": True,
        },
        "themes": [
            {"name": "AI Agent", "keywords": ["agent", "tool use", "planning"]},
            {"name": "深度学习时序预测", "keywords": ["time series", "forecasting"]},
        ],
        "organizations": [
            {
                "name": "OpenAI",
                "priority": 95,
                "aliases": ["openai"],
                "feeds": [
                    {
                        "name": "OpenAI arXiv query",
                        "url": "http://export.arxiv.org/api/query?search_query=all:%22OpenAI%22",
                    }
                ],
            }
        ],
    }
    path = project_root / "config.yaml"
    path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path
