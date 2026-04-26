from __future__ import annotations

from paper_learning_hub.config import load_config
from paper_learning_hub.models import CandidatePaper
from paper_learning_hub.translator import translate_paper

from conftest import write_test_config


def test_mock_translator_creates_markdown(tmp_path):
    config_path = write_test_config(tmp_path, backend="mock")
    config = load_config(config_path)
    raw_dir = config.raw_dir / "paper-001"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "paper.html"
    raw_path.write_text(
        """
        <html>
          <head><title>Paper 001</title></head>
          <body>
            <h1>Paper 001</h1>
            <p>This is an agent planning paper.</p>
            <p>It also discusses tool use and forecasting signals.</p>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    paper = CandidatePaper(
        paper_id="paper-001",
        title="Paper 001",
        organization="OpenAI",
        publish_date="2026-04-25",
        theme="AI Agent",
        source_name="feed",
        source_url="https://example.com/feed",
        paper_url="https://example.com/paper.html",
        summary="summary",
        priority=10,
    )
    output = translate_paper(config, paper, raw_path)
    content = output.read_text(encoding="utf-8")
    assert output.exists()
    assert "### 中文翻译" in content
    assert "待复核" in content
