"""每日主流程：抓取 → 翻译 → 生成报告 → GitHub Pages → git 自动推送 → ima 同步。"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .blog_fetcher import (
    BLOG_SOURCES,
    BlogArticle,
    fetch_blog_articles,
    generate_chinese_summaries,
    save_articles_json,
)
from .report_builder import generate_html_report, generate_simple_report
from .ima_sync import build_ima_sync_payload, save_ima_sync_file

logger = logging.getLogger(__name__)


def translate_via_llm(title: str, content: str, api_key: str) -> str:
    """使用 OpenAI 兼容 API 翻译标题 + 摘要为中文。"""
    import requests

    model = os.environ.get("PAPERHUB_MODEL", "gpt-4.1-mini")
    base_url = os.environ.get("PAPERHUB_API_BASE", "https://api.openai.com/v1")

    prompt = f"""请将以下 AI 技术文章信息翻译为中文摘要（100字以内，简洁有力）：

标题: {title}
内容: {content[:1000]}

只输出中文摘要，不要加任何前缀说明。"""

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.3,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _git_sync_daily(repo_root: Path, date_str: str, branch: str = "main", remote: str = "origin") -> dict:
    """执行 git add → commit → push，返回操作结果摘要。"""
    result = {"committed": False, "pushed": False, "message": ""}
    try:
        # 确认是 git 仓库
        check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_root, capture_output=True, text=True,
        )
        if check.returncode != 0:
            result["message"] = "非 Git 仓库，跳过推送"
            return result

        # 确认 repo root 匹配
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if Path(top).resolve() != repo_root.resolve():
            result["message"] = f"当前项目依附于上层仓库 {top}，跳过推送"
            return result

        # git add
        subprocess.run(
            ["git", "add", "daily-reports/", "docs/"],
            cwd=repo_root, check=True,
        )

        # 检查是否有变更
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        )
        if not status.stdout.strip():
            result["message"] = "无变更，跳过 commit"
            return result

        # git commit
        commit_msg = f"auto: daily paper hub report · {date_str}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=repo_root, check=True,
        )
        result["committed"] = True
        logger.info("  ✅ Git 提交: %s", commit_msg)

        # git push
        remotes = subprocess.run(
            ["git", "remote"], cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.split()
        if remote not in remotes:
            result["message"] = f"Git 已提交，但未推送：未配置远端 {remote}"
            return result

        subprocess.run(
            ["git", "push", remote, branch],
            cwd=repo_root, check=True,
        )
        result["pushed"] = True
        result["message"] = f"已推送到 {remote}/{branch}"
        logger.info("  🚀 Git 推送成功 → %s/%s", remote, branch)

    except subprocess.CalledProcessError as e:
        result["message"] = f"Git 操作失败: {e}"
        logger.warning("  ⚠️ %s", result["message"])
    except Exception as e:
        result["message"] = f"Git 同步异常: {e}"
        logger.warning("  ⚠️ %s", result["message"])

    return result


def run_daily_pipeline(
    output_dir: Path,
    github_pages_dir: Path = None,
    sync_ima: bool = False,
    api_key: str = "",
    max_per_source: int = 5,
    auto_push: bool = True,
    repo_root: Path = None,
) -> dict:
    """执行每日完整流水线。"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    date_display = now.strftime("%Y年%m月%d日")

    result = {
        "date": date_str,
        "status": "ok",
        "total_articles": 0,
        "translated": 0,
        "report_path": "",
        "github_pushed": False,
        "github_committed": False,
        "git_message": "",
        "ima_synced": False,
        "errors": [],
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: 抓取
    logger.info("=" * 60)
    logger.info(f"Paper Hub v2.0 · 每日运行 · {date_display}")
    logger.info("=" * 60)
    logger.info("Step 1: 从 5 个博客源抓取最新文章...")
    articles = fetch_blog_articles(max_per_source=max_per_source, search_cache_dir=output_dir)
    result["total_articles"] = len(articles)

    if not articles:
        logger.warning("  ⚠️ 未抓取到任何文章，终止。")
        result["status"] = "empty"
        return result

    logger.info(f"  ✅ 共抓取 {len(articles)} 篇文章")

    # Step 2: 中文翻译
    logger.info(f"Step 2: 生成中文摘要...")
    if api_key:
        articles = generate_chinese_summaries(
            articles,
            translator_func=translate_via_llm,
            api_key=api_key,
        )
    else:
        logger.warning("  ⚠️ 未提供 API Key，跳过翻译")

    translated = sum(1 for a in articles if a.translated)
    result["translated"] = translated
    logger.info(f"  ✅ 翻译完成 ({translated}/{len(articles)})")

    # Step 3: 保存 JSON 数据
    json_path = output_dir / f"daily-{date_str}.json"
    save_articles_json(articles, json_path)
    logger.info(f"Step 3: 保存 JSON → {json_path}")

    # Step 4: 生成 HTML 报告
    html_path = output_dir / f"report-{date_str}.html"
    generate_html_report(articles, html_path)
    result["report_path"] = str(html_path)
    logger.info(f"Step 4: 生成 HTML 报告 → {html_path}")

    # Step 5: 生成 Markdown 报告（降级方案）
    md_path = output_dir / f"report-{date_str}.md"
    generate_simple_report(articles, md_path)
    logger.info(f"Step 5: 生成 MD 报告 → {md_path}")

    # Step 6: 生成 index.html 作为最新报告
    index_path = output_dir / "index.html"
    generate_html_report(articles, index_path, report_title="前沿 AI 技术日报 · 最新")
    logger.info(f"Step 6: 更新首页 → {index_path}")

    # Step 7: GitHub Pages 部署 → 日报同步到 docs/daily/，供 MkDocs workflow 打包
    if github_pages_dir:
        logger.info(f"Step 7: 同步到 GitHub Pages...")
        try:
            import shutil
            github_pages_dir = Path(github_pages_dir)
            daily_dir = github_pages_dir / "daily"
            daily_dir.mkdir(parents=True, exist_ok=True)
            # Copy report into daily/ subdirectory
            shutil.copy2(html_path, daily_dir / f"report-{date_str}.html")
            shutil.copy2(json_path, daily_dir / f"daily-{date_str}.json")
            shutil.copy2(md_path, daily_dir / f"report-{date_str}.md")
            # latest symlink
            shutil.copy2(html_path, daily_dir / "latest.html")

            # Write CNAME if needed
            cname_path = github_pages_dir / "CNAME"
            if not cname_path.exists():
                cname_path.write_text("paper.groupechou.com")

            result["github_pushed"] = True
            logger.info(f"  ✅ 同步完成 → {daily_dir}")
        except Exception as e:
            result["errors"].append(f"github: {e}")
            logger.error(f"  ❌ GitHub 同步失败: {e}")

    # Step 7.5: Git 自动提交 + 推送
    if auto_push and (repo_root or (github_pages_dir and github_pages_dir.parent)):
        _root = repo_root or (github_pages_dir.parent if github_pages_dir else output_dir.parent)
        logger.info(f"Step 7.5: Git 自动提交并推送...")
        git_result = _git_sync_daily(Path(_root), date_str)
        result["github_committed"] = git_result["committed"]
        result["github_pushed"] = git_result["pushed"]
        result["git_message"] = git_result["message"]
        if git_result["committed"] and git_result["pushed"]:
            logger.info(f"  ✅ {git_result['message']}")
        else:
            logger.info(f"  ℹ️  {git_result['message']}")

    # Step 8: ima 知识库同步
    if sync_ima:
        logger.info(f"Step 8: ima 知识库同步...")
        try:
            payload = build_ima_sync_payload(articles, str(html_path), date_str)
            ima_path = output_dir / f"ima-sync-{date_str}.json"
            save_ima_sync_file(payload, ima_path)
            result["ima_synced"] = True
            result["ima_payload"] = str(ima_path)
            logger.info(f"  ✅ ima payload 已保存 → {ima_path}")
            logger.info(f"  📌 需在 WorkBuddy 中通过 ima-mcp 完成实际上传")
        except Exception as e:
            result["errors"].append(f"ima: {e}")
            logger.error(f"  ❌ ima 同步失败: {e}")

    # Summary
    logger.info("=" * 60)
    logger.info(f"✅ 日报生成完成!")
    logger.info(f"  📊 {len(articles)} 篇文章 | 🌐 {len(set(a.org for a in articles))} 个机构")
    logger.info(f"  📝 翻译: {translated}/{len(articles)}")
    logger.info(f"  📄 HTML: {html_path}")
    logger.info(f"  📋 MD:   {md_path}")
    if github_pages_dir:
        logger.info(f"  🚀 GitHub Pages: {github_pages_dir}")
    if result["github_pushed"]:
        logger.info(f"  🔄 Git 推送: {result['git_message']}")
    logger.info("=" * 60)

    # Step 9: 保存运行结果日志
    log_path = output_dir / f".run-result-{date_str}.json"
    try:
        log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        # 同时写入 latest 方便外部读取
        latest_log = output_dir / ".run-result-latest.json"
        latest_log.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    return result


def main():
    """CLI 入口。"""
    import argparse

    parser = argparse.ArgumentParser(description="Paper Hub v2.0 - 每日前沿技术日报")
    parser.add_argument("--output", "-o", default="./daily-reports", help="输出目录")
    parser.add_argument("--max", type=int, default=5, help="每源最多文章数")
    parser.add_argument("--github-pages", help="GitHub Pages 部署目录")
    parser.add_argument("--sync-ima", action="store_true", help="启用 ima 知识库同步")
    parser.add_argument("--api-key", help="LLM API Key (或设置 PAPERHUB_API_KEY 环境变量)")
    parser.add_argument("--no-auto-push", action="store_true", help="禁用 Git 自动提交推送")
    parser.add_argument("--repo-root", help="Git 仓库根目录（默认从 github-pages 推导）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
    )

    api_key = args.api_key or os.environ.get("PAPERHUB_API_KEY", "")

    result = run_daily_pipeline(
        output_dir=Path(args.output),
        github_pages_dir=Path(args.github_pages) if args.github_pages else None,
        sync_ima=args.sync_ima,
        api_key=api_key,
        max_per_source=args.max,
        auto_push=not args.no_auto_push,
        repo_root=Path(args.repo_root) if args.repo_root else None,
    )

    if result["status"] == "error":
        sys.exit(1)

    # Print summary for WorkBuddy consumption
    print(json.dumps({
        "date": result["date"],
        "status": result["status"],
        "total": result["total_articles"],
        "translated": result["translated"],
        "report_url": result["report_path"],
        "github": result["github_pushed"],
        "ima": result["ima_synced"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
