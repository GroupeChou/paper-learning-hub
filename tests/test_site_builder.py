from __future__ import annotations

from pathlib import Path

from paper_learning_hub.config import load_config
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.site_builder import build_site

from conftest import write_test_config


def test_site_builder_generates_docs(tmp_path):
    config_path = write_test_config(tmp_path)
    config = load_config(config_path)
    paper_dir = config.zh_dir / "paper-001"
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "paper_zh.md").write_text("# Paper 001\n\n内容", encoding="utf-8")
    guides_dir = tmp_path / "guides"
    guides_dir.mkdir(parents=True, exist_ok=True)
    (guides_dir / "classics.md").write_text("# 经典必读\n", encoding="utf-8")

    paper = CandidatePaper(
        paper_id="paper-001",
        title="Paper 001",
        organization="OpenAI",
        publish_date="2026-04-25",
        theme="AI Agent",
        source_name="feed",
        source_url="https://example.com/feed",
        paper_url="https://example.com/paper.pdf",
        summary="summary",
        priority=1,
        status="translated",
        zh_path=str(paper_dir / "paper_zh.md"),
    )

    mkdocs_file = build_site(config, [paper], [paper], {"translated": 1})
    assert mkdocs_file.exists()
    assert (config.site.docs_dir / "index.md").exists()
    assert (config.site.docs_dir / "guides" / "daily-guide.md").exists()
    assert (config.site.docs_dir / "papers" / "paper-001" / "index.md").exists()
