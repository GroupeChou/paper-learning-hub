from __future__ import annotations

import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

from .models import AppConfig, CandidatePaper
from .utils import ensure_dir, today_iso


def _write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def build_daily_guide(config: AppConfig, papers: list[CandidatePaper]) -> Path:
    grouped: dict[str, list[CandidatePaper]] = defaultdict(list)
    for paper in papers:
        grouped[paper.theme].append(paper)
    today = today_iso(config.timezone)
    lines = [
        "# 今日新增",
        "",
        f"- 更新时间：{today}",
        f"- 当日候选总数：{len(papers)}",
        "",
    ]
    if not papers:
        lines += ["## 今日结果", "", "- 今日未发现符合筛选条件的新论文。", ""]
    for theme, items in grouped.items():
        lines += [f"## {theme}", ""]
        for item in items:
            translated = f"[中文笔记](../papers/{item.paper_id}/index.md)" if item.zh_path else "待生成"
            lines.append(
                f"- **{item.title}** | {item.organization} | {item.publish_date} | 优先级 {item.priority} | 状态 `{item.status}` | {translated}"
            )
            lines.append(f"  - 来源：[{item.source_name}]({item.source_url})")
            lines.append(f"  - 论文：[{item.paper_url}]({item.paper_url})")
            if item.summary:
                lines.append(f"  - 摘要：{item.summary}")
        lines.append("")

    root_path = config.site.docs_dir.parent.parent / "guides" / "daily-guide.md"
    site_path = config.site.docs_dir / "guides" / "daily-guide.md"
    content = "\n".join(lines)
    _write_text(root_path, content)
    _write_text(site_path, content)
    return root_path


def build_topic_index(config: AppConfig, papers: list[CandidatePaper]) -> Path:
    grouped: dict[str, list[CandidatePaper]] = defaultdict(list)
    for paper in papers:
        grouped[paper.theme].append(paper)
    lines = ["# 专题索引", "", "按主题聚合已经进入知识库的论文。", ""]
    for theme, items in grouped.items():
        lines.append(f"## {theme}")
        lines.append("")
        for item in items:
            link = f"../papers/{item.paper_id}/index.md" if item.zh_path else item.paper_url
            label = "中文精读" if item.zh_path else "原文"
            lines.append(f"- [{item.title}]({link}) | {item.organization} | {item.publish_date} | {label}")
        lines.append("")
    path = config.site.docs_dir / "topics" / "index.md"
    _write_text(path, "\n".join(lines))
    return path


def build_paper_index(config: AppConfig, papers: list[CandidatePaper]) -> Path:
    lines = ["# 论文详情页", "", "这里汇总所有已经进入站点的论文页面。", ""]
    for paper in papers:
        if paper.zh_path:
            lines.append(f"- [{paper.title}](../papers/{paper.paper_id}/index.md) | {paper.organization} | {paper.theme}")
    path = config.site.docs_dir / "papers" / "index.md"
    _write_text(path, "\n".join(lines))
    return path


def build_home(config: AppConfig, papers: list[CandidatePaper], status_counts: dict[str, int]) -> Path:
    lines = [
        "# 论文自动研学知识库",
        "",
        "一个围绕 `深度学习时序预测` 和 `AI Agent` 的本地优先学习站点。",
        "",
        "## 当前状态",
        "",
        f"- 已收录论文：{len(papers)}",
        f"- 已翻译：{status_counts.get('translated', 0)}",
        f"- 待处理：{status_counts.get('queued', 0) + status_counts.get('discovered', 0)}",
        f"- 下载失败：{status_counts.get('failed_download', 0)}",
        f"- 翻译失败：{status_counts.get('failed_translate', 0)}",
        "",
        "## 快速入口",
        "",
        "- [今日新增](guides/daily-guide.md)",
        "- [经典必读](guides/classics.md)",
        "- [专题索引](topics/index.md)",
        "- [论文详情页](papers/index.md)",
        "",
    ]
    path = config.site.docs_dir / "index.md"
    _write_text(path, "\n".join(lines))
    return path


def copy_classics(config: AppConfig, classics_path: Path) -> Path:
    target = config.site.docs_dir / "guides" / "classics.md"
    ensure_dir(target.parent)
    shutil.copyfile(classics_path, target)
    return target


def copy_translated_papers(config: AppConfig, papers: list[CandidatePaper]) -> None:
    for paper in papers:
        if not paper.zh_path:
            continue
        source_markdown = Path(paper.zh_path)
        source_dir = source_markdown.parent
        if not source_dir.exists():
            continue
        target_dir = config.site.docs_dir / "papers" / paper.paper_id
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        markdown_target = target_dir / "paper_zh.md"
        if markdown_target.exists():
            markdown_target.rename(target_dir / "index.md")


def write_mkdocs_config(config: AppConfig) -> Path:
    content = f"""
site_name: {config.site.site_name}
site_url: {config.site.site_url}
repo_name: {config.site.repo_name}
theme:
  name: material
  language: zh
  features:
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - content.code.copy
plugins:
  - search
markdown_extensions:
  - tables
  - toc:
      permalink: true
  - admonition
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - pymdownx.arithmatex:
      generic: true
extra_javascript:
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
extra_css:
  - stylesheets/extra.css
nav:
  - 首页: index.md
  - 今日新增: guides/daily-guide.md
  - 经典必读: guides/classics.md
  - 专题索引: topics/index.md
  - 论文详情页: papers/index.md
"""
    _write_text(config.site.mkdocs_file, content)
    return config.site.mkdocs_file


def ensure_assets(config: AppConfig) -> None:
    css_path = config.site.docs_dir / "stylesheets" / "extra.css"
    _write_text(
        css_path,
        """
        .md-typeset h1, .md-typeset h2, .md-typeset h3 {
          letter-spacing: 0;
        }

        .md-typeset img {
          border: 1px solid rgba(0, 0, 0, 0.08);
          border-radius: 6px;
          max-width: 100%;
          display: block;
          margin: 1rem 0;
        }
        """,
    )


def build_site(config: AppConfig, papers: list[CandidatePaper], latest_papers: list[CandidatePaper], status_counts: dict[str, int]) -> Path:
    ensure_dir(config.site.docs_dir)
    ensure_assets(config)
    copy_translated_papers(config, papers)
    build_home(config, papers, status_counts)
    build_daily_guide(config, latest_papers)
    build_topic_index(config, papers)
    build_paper_index(config, papers)
    copy_classics(config, config.site.docs_dir.parent.parent / "guides" / "classics.md")
    return write_mkdocs_config(config)


def run_mkdocs_build(config: AppConfig) -> None:
    subprocess.run(
        ["mkdocs", "build", "-f", str(config.site.mkdocs_file), "-d", str(config.site.mkdocs_file.parent / "site_output")],
        check=True,
    )
