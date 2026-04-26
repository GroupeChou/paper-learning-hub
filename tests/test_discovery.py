from __future__ import annotations

import time
from types import SimpleNamespace

from paper_learning_hub.config import load_config
from paper_learning_hub.discovery import discover_candidates

from conftest import write_test_config


def test_discover_candidates_filters_and_scores(tmp_path, monkeypatch):
    config_path = write_test_config(tmp_path)
    config = load_config(config_path)
    entry = SimpleNamespace(
        title="OpenAI Agent Planning for Time Series Forecasting",
        summary="This paper studies agent planning and time series forecasting.",
        link="https://arxiv.org/abs/2504.12345",
        links=[{"href": "https://arxiv.org/abs/2504.12345", "type": "text/html"}],
        published_parsed=time.gmtime(),
    )

    monkeypatch.setattr("paper_learning_hub.discovery.feedparser.parse", lambda _url: SimpleNamespace(entries=[entry]))

    papers = discover_candidates(config)
    assert len(papers) == 1
    assert papers[0].theme in {"AI Agent", "深度学习时序预测"}
    assert papers[0].paper_url.endswith(".pdf")
    assert papers[0].organization == "OpenAI"
