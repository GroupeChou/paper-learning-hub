from __future__ import annotations

import logging
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

from .models import AppConfig, CandidatePaper
from .utils import ensure_dir, today_iso

logger = logging.getLogger(__name__)


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
            # 判断是否为完整精读（非占位符）
            zh_file = Path(paper.zh_path)
            is_translated = zh_file.exists() and zh_file.stat().st_size > 500
            tag = "`已精读`" if is_translated else "`待精读`"
            icon = "✅ " if is_translated else ""
            lines.append(f"- {icon}**[{paper.title}](../papers/{paper.paper_id}/index.md)** | {paper.organization} | {paper.theme} | {tag}")
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
    # Only include nav entries for files that actually exist
    docs_dir = config.site.docs_dir

    def exists(path: str) -> bool:
        return (docs_dir / path).exists()

    nav_entries = []

    # Top-level pages (always available)
    nav_entries.append("  - 首页: index.md")
    if exists("guides/agent-roadmap.md"):
        nav_entries.append(f"  - 🤖 AI Agent 论文目录: guides/agent-roadmap.md")
    if exists("guides/ts-roadmap.md"):
        nav_entries.append(f"  - 📈 时序预测论文目录: guides/ts-roadmap.md")
    if exists("guides/daily-guide.md"):
        nav_entries.append(f"  - 📅 今日更新: guides/daily-guide.md")
    if exists("topics/index.md"):
        nav_entries.append(f"  - 📚 专题索引: topics/index.md")

    # All papers (dynamic)
    nav_entries.append("  - 论文详情:")
    nav_entries.append("    - papers/index.md")

    nav_str = "\n".join(nav_entries)

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
{nav_str}
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

        /* Wide layout - max-width 1600px */
        .md-grid {
          max-width: 1600px;
        }

        /* Make tables full width */
        .md-typeset table:not([class]) {
          display: table;
          width: 100%;
          table-layout: auto;
        }

        /* Topic column: no wrap */
        .md-typeset table:not([class]) td:first-child,
        .md-typeset table:not([class]) th:first-child {
          white-space: nowrap;
        }
        /* English title column: cap width */
        .md-typeset table:not([class]) td:nth-child(2) {
          max-width: 50%;
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
    update_roadmap(config, papers)
    return write_mkdocs_config(config)


def update_roadmap(config: AppConfig, papers: list[CandidatePaper]) -> None:
    """Regenerate roadmap with papers grouped by technical topic, table with Chinese/English titles."""
    now = today_iso(config.timezone)

    # Topic classification keywords
    agent_topics = {
        "智能体架构与框架": ["agent architecture", "agent framework", "autonomous agent", "agent system", "agentic", "computer use"],
        "多智能体系统": ["multi-agent", "multiagent", "cooperative", "collaboration", "swarm", "MAS"],
        "智能体安全与对齐": ["safety", "security", "jailbreak", "alignment", "adversarial", "risk", "privacy", "harm"],
        "记忆与推理": ["memory", "reasoning", "reflection", "chain-of-thought", "thinking", "self-evolution", "self-improve"],
        "代码生成与软件工程": ["code", "software", "programming", "SWE", "repository", "debug", "coding"],
        "智能体评估与基准": ["benchmark", "evaluation", "measuring", "assessment"],
        "工具使用与API": ["tool use", "tool call", "function calling", "skill", "API"],
        "检索增强生成": ["retrieval", "RAG", "semantic", "knowledge graph"],
        "大模型训练与扩展": ["training", "scaling", "pretraining", "fine-tune", "SFT", "RLHF", "RL"],
        "具身智能": ["embodied", "robot", "physical", "manipulation"],
        "大模型基础": ["LLM", "large language model", "foundation model"],
        "多模态": ["multimodal", "vision-language", "VLM", "visual"],
    }
    ts_topics = {
        "时序预测基础模型": ["foundation model", "base model", "pretrain", "pre-train"],
        "Transformer时序预测": ["transformer", "attention", "patch", "informer", "autoformer", "timesnet"],
        "长序列预测": ["long-term", "long horizon", "long range"],
        "时空预测": ["spatiotemporal", "spatio-temporal", "spatial", "temporal", "STGNN", "graph"],
        "概率预测与不确定性": ["probabilistic", "uncertainty", "distribution", "diffusion", "copula"],
        "异常检测": ["anomaly", "outlier", "detection"],
        "多变量预测": ["multivariate", "multi-variate"],
        "非平稳与领域泛化": ["non-stationary", "distribution shift", "domain adaptation", "robust", "generalization"],
        "金融气候能源应用": ["financial", "climate", "weather", "energy", "stock"],
        "深度学习基础方法": ["deep learning", "neural", "CNN", "RNN", "LSTM", "SSM", "state space"],
    }

    def classify(title: str, summary: str, theme: str) -> str:
        text = f"{title} {summary}".lower()
        topics = agent_topics if theme == "AI Agent" else ts_topics
        best, best_score = None, 0
        for topic, kws in topics.items():
            score = sum(text.count(kw.lower()) for kw in kws)
            if score > best_score:
                best, best_score = topic, score
        return best or "其他"

    roadmap_map = {
        "AI Agent": config.site.docs_dir.parent.parent / "guides" / "agent-roadmap.md",
        "时序预测": config.site.docs_dir.parent.parent / "guides" / "ts-roadmap.md",
    }

    for theme_name, target in roadmap_map.items():
        theme_papers = [p for p in papers if p.theme == theme_name and p.status == "translated" and p.zh_path]
        if not theme_papers:
            continue

        # Group by classified topic
        topic_groups: dict[str, list[CandidatePaper]] = {}
        for p in theme_papers:
            topic = classify(p.title, p.summary or "", p.theme)
            topic_groups.setdefault(topic, []).append(p)

        lines = [
            f"# {theme_name} 论文列表",
            "",
            f"> 按技术方向分类。点击论文标题跳转到详情页。",
            f"> 最后更新：{now} | 共 {len(theme_papers)} 篇论文",
            "",
            "| 主题 | 英文标题 | 中文标题 | 发布日期 | 发布机构 |",
            "|------|----------|----------|:--------:|:--------:|",
        ]

        sorted_topics = sorted(topic_groups.items(), key=lambda x: -len(x[1]))
        for topic_name, topic_papers in sorted_topics:
            topic_papers.sort(key=lambda p: p.publish_date, reverse=True)
            for i, p in enumerate(topic_papers):
                title_link = f"[{p.title}](../papers/{p.paper_id}/index.md)"
                cn_title = p.cn_title or "*待补充*"
                org = p.organization or "—"
                if i == 0:
                    row = f"| **{topic_name}** ({len(topic_papers)}) | {title_link} | {cn_title} | {p.publish_date} | {org} |"
                else:
                    row = f"| | {title_link} | {cn_title} | {p.publish_date} | {org} |"
                lines.append(row)

        content = "\n".join(lines) + "\n"
        target.write_text(content, encoding="utf-8")
        logger.info(f"Regenerated roadmap: {target.name} ({len(theme_papers)} papers, {len(topic_groups)} topics)")
        site_target = config.site.docs_dir / "guides" / target.name
        site_target.write_text(content, encoding="utf-8")


def run_mkdocs_build(config: AppConfig) -> None:
    subprocess.run(
        ["mkdocs", "build", "-f", str(config.site.mkdocs_file), "-d", str(config.site.mkdocs_file.parent / "site_output")],
        check=True,
    )
