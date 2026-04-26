from __future__ import annotations

import subprocess
from pathlib import Path

from .models import AppConfig


def sync_git(config: AppConfig, repo_root: Path) -> str:
    git_settings = config.git
    try:
        inside_repo = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if inside_repo.returncode != 0:
            return "Git 同步已跳过：当前目录不是 Git 仓库。"

        top_level = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if Path(top_level).resolve() != repo_root.resolve():
            return f"Git 同步已跳过：当前项目依附于上层仓库 `{top_level}`，请先为本项目单独配置 Git 仓库。"
    except subprocess.CalledProcessError as exc:
        return f"Git 同步已跳过：无法确认仓库状态（{exc}）。"

    if not git_settings.auto_commit:
        return "Git 同步已跳过：config.yaml 中未启用 auto_commit。"

    try:
        subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
        status = subprocess.run(["git", "status", "--short"], cwd=repo_root, capture_output=True, text=True, check=True)
        if not status.stdout.strip():
            return "Git 同步已跳过：没有新的变更需要提交。"

        subprocess.run(
            ["git", "commit", "-m", f"{git_settings.commit_prefix}: update paper hub content"],
            cwd=repo_root,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        return f"Git 自动提交失败：{exc}"

    if not git_settings.auto_push:
        return "Git 已提交，本次未执行 push。"

    remote_name = git_settings.remote_name
    remotes = subprocess.run(["git", "remote"], cwd=repo_root, capture_output=True, text=True, check=True).stdout.split()
    if remote_name not in remotes:
        return f"Git 已提交，但未推送：未配置远端 `{remote_name}`。"

    try:
        subprocess.run(["git", "push", remote_name, git_settings.branch], cwd=repo_root, check=True)
        return f"Git 已提交并推送到 {remote_name}/{git_settings.branch}。"
    except subprocess.CalledProcessError as exc:
        return f"Git 已提交，但推送失败：{exc}"
