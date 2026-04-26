from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from .models import AppConfig, CandidatePaper, ParsedDocument
from .parser import parse_document
from .utils import ensure_dir, now_iso, relative_posix, shorten_text


def ensure_workspace(config: AppConfig) -> None:
    ensure_dir(config.workbuddy.jobs_dir)
    ensure_dir(config.workbuddy.memory_dir)
    ensure_dir(config.workbuddy.skill_source_dir)
    ensure_dir(config.workbuddy.task_prompt_path.parent)


def install_skill(config: AppConfig) -> str:
    if not config.workbuddy.enabled:
        return "WorkBuddy 安装已跳过：config.yaml 中未启用 workbuddy.enabled。"

    source = config.workbuddy.skill_source_dir
    target = config.workbuddy.installed_skill_path
    ensure_dir(target.parent)
    if target.exists() or target.is_symlink():
        if target.is_symlink() and os.path.realpath(target) == str(source):
            return f"WorkBuddy 技能已就绪：{target}"
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)

    if config.workbuddy.use_symlink_install:
        target.symlink_to(source, target_is_directory=True)
        return f"WorkBuddy 技能已软链接到 {target}"

    shutil.copytree(source, target)
    return f"WorkBuddy 技能已复制到 {target}"


def _job_dir(config: AppConfig, paper: CandidatePaper) -> Path:
    return ensure_dir(config.workbuddy.jobs_dir / paper.paper_id)


def _target_markdown_path(config: AppConfig, paper: CandidatePaper) -> Path:
    return config.zh_dir / paper.paper_id / "paper_zh.md"


def _target_status_path(config: AppConfig, paper: CandidatePaper) -> Path:
    return _job_dir(config, paper) / "result.json"


def _serialize_manifest(config: AppConfig, paper: CandidatePaper, parsed: ParsedDocument, raw_path: Path) -> dict[str, object]:
    target_markdown = _target_markdown_path(config, paper)
    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "organization": paper.organization,
        "theme": paper.theme,
        "publish_date": paper.publish_date,
        "source_name": paper.source_name,
        "source_url": paper.source_url,
        "paper_url": paper.paper_url,
        "summary": paper.summary,
        "raw_path": str(raw_path),
        "target_markdown": str(target_markdown),
        "image_paths": [str((target_markdown.parent / image).resolve()) for image in parsed.image_paths],
        "parse_notes": parsed.notes,
        "chunk_count": len(parsed.chunks),
        "chunk_headings": [chunk.heading for chunk in parsed.chunks],
        "generated_at": now_iso(config.timezone),
    }


def _job_markdown(config: AppConfig, paper: CandidatePaper, parsed: ParsedDocument, raw_path: Path) -> str:
    target_markdown = _target_markdown_path(config, paper)
    job_dir = _job_dir(config, paper)
    sample_text = shorten_text(parsed.text, limit=1200)
    image_lines = "\n".join(f"- `{image}`" for image in parsed.image_paths) if parsed.image_paths else "- 无"
    note_lines = "\n".join(f"- {note}" for note in parsed.notes) if parsed.notes else "- 无"
    headings = "\n".join(f"- {chunk.heading}" for chunk in parsed.chunks[:20]) if parsed.chunks else "- 无"
    return f"""# WorkBuddy 论文精读任务

## 目标

请在当前项目中完成下面这篇论文的中文精读，并将最终结果直接写入：

- 目标文件：`{target_markdown}`
- 任务状态文件：`{job_dir / 'result.json'}`

## 论文信息

- paper_id：`{paper.paper_id}`
- 标题：{paper.title}
- 机构：{paper.organization}
- 主题：{paper.theme}
- 发布日期：{paper.publish_date}
- 来源：[{paper.source_name}]({paper.source_url})
- 原文链接：[{paper.paper_url}]({paper.paper_url})
- 原文文件：`{raw_path}`

## 输出要求

1. 输出完整 Markdown，路径固定为 `papers/zh/<paper_id>/paper_zh.md`
2. 每个章节固定包含：
   - `### 中文翻译`
   - `### 术语解释`
   - `### 图表/公式说明`
   - `### 关键 takeaway`
3. 尽量逐段、逐句解释，不确定处标注 `待复核`
4. 保留 LaTeX 公式，不删除关键图表说明
5. 如果发现图表资源，尽量在文中引用现有本地路径
6. 处理完成后，写入 `result.json`，格式如下：

```json
{{
  "paper_id": "{paper.paper_id}",
  "status": "completed",
  "target_markdown": "{target_markdown}",
  "updated_at": "{now_iso(config.timezone)}",
  "notes": "可选补充说明"
}}
```

若失败，请写：

```json
{{
  "paper_id": "{paper.paper_id}",
  "status": "failed",
  "updated_at": "{now_iso(config.timezone)}",
  "notes": "失败原因"
}}
```

## 解析上下文

- 原始摘要：{paper.summary}
- 抽取章节数：{len(parsed.chunks)}
- 章节预览：
{headings}

- 图片资源：
{image_lines}

- 解析备注：
{note_lines}

## 文本预览

```text
{sample_text}
```
"""


def prepare_jobs(config: AppConfig, papers: list[CandidatePaper]) -> list[CandidatePaper]:
    prepared: list[CandidatePaper] = []
    top_papers = papers[: config.daily_limit]
    for paper in top_papers:
        raw_path = Path(paper.raw_path) if paper.raw_path else None
        if raw_path is None or not raw_path.exists():
            continue
        target_dir = config.zh_dir / paper.paper_id
        parsed = parse_document(raw_path, target_dir, config.translator.chunk_chars, config.translator.max_images_per_paper)
        job_dir = _job_dir(config, paper)
        manifest = _serialize_manifest(config, paper, parsed, raw_path)
        (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (job_dir / "job.md").write_text(_job_markdown(config, paper, parsed, raw_path), encoding="utf-8")
        prepared.append(paper)
    return prepared


def write_daily_brief(config: AppConfig, prepared: list[CandidatePaper], queued: list[CandidatePaper]) -> Path:
    lines = [
        "# WorkBuddy 每日论文任务",
        "",
        "请在 WorkBuddy 中打开当前项目并使用 `paper-learning-hub` 技能执行本日任务。",
        "",
        "## 推荐执行顺序",
        "",
        f"1. 运行 `cd {config.workbuddy.skill_source_dir.parent.parent.parent} && ./run_daily.sh --prepare-workbuddy`",
        "2. 按下面的待处理论文列表逐篇完成中文精读，直接写入目标 Markdown",
        f"3. 全部完成后运行 `cd {config.workbuddy.skill_source_dir.parent.parent.parent} && ./run_daily.sh --build-only`",
        "4. 检查 Git 自动提交/推送结果，如失败则根据日志修复远端配置",
        "",
        "## 本日深度处理论文",
        "",
    ]
    if prepared:
        for paper in prepared:
            lines.append(f"- `{paper.paper_id}` | {paper.title} | {paper.organization} | {paper.theme}")
            lines.append(f"  - 任务文件：`{relative_posix(_job_dir(config, paper) / 'job.md', config.workbuddy.daily_brief_path.parent)}`")
            lines.append(f"  - 输出文件：`{relative_posix(_target_markdown_path(config, paper), config.workbuddy.daily_brief_path.parent)}`")
    else:
        lines.append("- 今日没有可交给 WorkBuddy 深度处理的论文。")
    lines += ["", "## 队列中的其余论文", ""]
    if queued:
        for paper in queued:
            lines.append(f"- `{paper.paper_id}` | {paper.title} | {paper.organization} | 状态 `{paper.status}`")
    else:
        lines.append("- 无")
    config.workbuddy.daily_brief_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return config.workbuddy.daily_brief_path


def write_task_prompt(config: AppConfig) -> Path:
    project_root = config.workbuddy.skill_source_dir.parent.parent.parent
    content = f"""请在 WorkBuddy 中使用 `paper-learning-hub` 技能完成这个项目的每日自动研学任务。

项目目录：`{project_root}`

固定流程：
1. 运行 `./run_daily.sh --prepare-workbuddy`
2. 打开 `.workbuddy/daily-brief.md`
3. 逐篇处理 `.workbuddy/jobs/<paper_id>/job.md`
4. 将精读结果写入 `papers/zh/<paper_id>/paper_zh.md`
5. 写入对应 `result.json`
6. 运行 `./run_daily.sh --build-only`
7. 确认 Git 自动提交和推送状态
"""
    config.workbuddy.task_prompt_path.write_text(content, encoding="utf-8")
    return config.workbuddy.task_prompt_path


def sync_completed_jobs(config: AppConfig, papers: list[CandidatePaper]) -> list[tuple[CandidatePaper, str, str | None]]:
    updates: list[tuple[CandidatePaper, str, str | None]] = []
    for paper in papers:
        target_markdown = _target_markdown_path(config, paper)
        result_path = _target_status_path(config, paper)
        if target_markdown.exists():
            updates.append((paper, str(target_markdown), None))
            continue
        if result_path.exists():
            try:
                payload = json.loads(result_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if payload.get("status") == "failed":
                updates.append((paper, "", payload.get("notes") or "WorkBuddy 任务失败"))
    return updates
