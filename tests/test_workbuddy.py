from __future__ import annotations

import json

from paper_learning_hub.config import load_config
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.workbuddy import install_skill, prepare_jobs, sync_completed_jobs, write_daily_brief, write_task_prompt

from conftest import write_test_config


def test_workbuddy_job_preparation_and_sync(tmp_path):
    config_path = write_test_config(tmp_path)
    config = load_config(config_path)

    raw_dir = config.raw_dir / "paper-001"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "paper.html"
    raw_path.write_text(
        """
        <html>
          <head><title>Agent Paper</title></head>
          <body>
            <h1>Agent Paper</h1>
            <p>This paper studies agent planning and time series reasoning.</p>
            <p>It includes tools, memory, and reflection.</p>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    paper = CandidatePaper(
        paper_id="paper-001",
        title="Agent Paper",
        organization="OpenAI",
        publish_date="2026-04-25",
        theme="AI Agent",
        source_name="feed",
        source_url="https://example.com/feed",
        paper_url="https://example.com/paper.html",
        summary="summary",
        priority=10,
        raw_path=str(raw_path),
    )
    prepared = prepare_jobs(config, [paper])
    assert len(prepared) == 1
    assert (config.workbuddy.jobs_dir / "paper-001" / "job.md").exists()
    assert (config.workbuddy.jobs_dir / "paper-001" / "manifest.json").exists()

    target_markdown = config.zh_dir / "paper-001" / "paper_zh.md"
    target_markdown.parent.mkdir(parents=True, exist_ok=True)
    target_markdown.write_text("# Agent Paper\n\n已完成", encoding="utf-8")

    synced = sync_completed_jobs(config, [paper])
    assert synced[0][1].endswith("paper_zh.md")


def test_workbuddy_install_and_brief_files(tmp_path):
    config_path = write_test_config(tmp_path)
    config = load_config(config_path)
    config.workbuddy.skill_source_dir.mkdir(parents=True, exist_ok=True)
    (config.workbuddy.skill_source_dir / "SKILL.md").write_text("# skill", encoding="utf-8")

    message = install_skill(config)
    assert "WorkBuddy 技能" in message
    assert config.workbuddy.installed_skill_path.exists()

    paper = CandidatePaper(
        paper_id="paper-002",
        title="Forecast Paper",
        organization="OpenAI",
        publish_date="2026-04-25",
        theme="深度学习时序预测",
        source_name="feed",
        source_url="https://example.com/feed",
        paper_url="https://example.com/paper.pdf",
        summary="summary",
        priority=10,
    )
    brief = write_daily_brief(config, [paper], [])
    prompt = write_task_prompt(config)
    assert brief.exists()
    assert prompt.exists()

