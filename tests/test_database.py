from __future__ import annotations

from paper_learning_hub.database import PaperDatabase
from paper_learning_hub.models import CandidatePaper


def test_database_upsert_and_status(tmp_path):
    db = PaperDatabase(tmp_path / "papers.db")
    paper = CandidatePaper(
        paper_id="paper-001",
        title="Reasoning Agents for Time Series",
        organization="OpenAI",
        publish_date="2026-04-25",
        theme="AI Agent",
        source_name="OpenAI arXiv query",
        source_url="https://example.com/source",
        paper_url="https://example.com/paper.pdf",
        summary="A paper about agents.",
        priority=950,
    )
    db.upsert_candidate(paper, "2026-04-25T08:00:00+08:00")
    db.set_status(
        "paper-001",
        "translated",
        "2026-04-25T09:00:00+08:00",
        raw_path="/tmp/paper.pdf",
        zh_path="/tmp/paper_zh.md",
    )

    rows = db.get_papers()
    assert len(rows) == 1
    assert rows[0].status == "translated"
    assert rows[0].raw_path == "/tmp/paper.pdf"
    assert rows[0].zh_path == "/tmp/paper_zh.md"
    db.close()

