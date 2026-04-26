from __future__ import annotations

import subprocess

from paper_learning_hub.config import load_config
from paper_learning_hub.git_ops import sync_git

from conftest import write_test_config


def test_git_sync_handles_missing_remote(tmp_path):
    config_path = write_test_config(tmp_path)
    config = load_config(config_path)
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")

    message = sync_git(config, tmp_path)
    assert "未配置远端" in message or "Git 已提交" in message
