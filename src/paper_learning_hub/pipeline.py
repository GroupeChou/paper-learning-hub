from __future__ import annotations

import logging
from pathlib import Path

from .config import load_config
from .database import PaperDatabase
from .discovery import discover_candidates
from .downloader import download_paper
from .git_ops import sync_git
from .models import CandidatePaper, PipelineResult
from .site_builder import build_site, run_mkdocs_build
from .translator import translate_paper
from .utils import ensure_dir, now_iso, today_iso
from .workbuddy import ensure_workspace, install_skill, prepare_jobs, sync_completed_jobs, write_daily_brief, write_task_prompt


def setup_logging(log_dir: Path) -> None:
    ensure_dir(log_dir)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


class Pipeline:
    def __init__(self, config_path: Path):
        self.config_path = config_path.resolve()
        self.root = self.config_path.parent
        self.config = load_config(self.config_path)
        setup_logging(self.config.log_dir)
        ensure_dir(self.config.raw_dir)
        ensure_dir(self.config.zh_dir)
        ensure_dir(self.config.site.docs_dir)
        if self.config.workbuddy.enabled:
            ensure_workspace(self.config)
        self.db = PaperDatabase(self.config.database_path)

    def close(self) -> None:
        self.db.close()

    def discover(self) -> int:
        discovered = discover_candidates(self.config)
        timestamp = now_iso(self.config.timezone)
        for paper in discovered:
            self.db.upsert_candidate(paper, timestamp)
        self.db.record_run("discover", "ok", f"discovered={len(discovered)}", timestamp)
        logging.info("Discovered %s candidate papers", len(discovered))
        return len(discovered)

    def _download_candidates(self, papers: list[CandidatePaper], result: PipelineResult) -> None:
        timestamp = now_iso(self.config.timezone)
        for paper in papers:
            if paper.raw_path:
                continue
            try:
                raw_path = download_paper(paper, self.config.raw_dir)
                self.db.set_status(paper.paper_id, "downloaded", timestamp, raw_path=str(raw_path))
                result.downloaded += 1
                logging.info("Downloaded %s", paper.title)
            except Exception as exc:  # noqa: BLE001
                result.failed += 1
                self.db.set_status(paper.paper_id, "failed_download", timestamp, failure_reason=str(exc))
                logging.exception("Failed to download %s", paper.title)

    def _translate_top(self, papers: list[CandidatePaper], result: PipelineResult) -> None:
        timestamp = now_iso(self.config.timezone)
        top_papers = papers[: self.config.daily_limit]
        queued_papers = papers[self.config.daily_limit :]
        for paper in queued_papers:
            self.db.set_status(paper.paper_id, "queued", timestamp)
            result.queued += 1

        for paper in top_papers:
            try:
                raw_path = Path(paper.raw_path) if paper.raw_path else None
                if raw_path is None or not raw_path.exists():
                    raw_path = download_paper(paper, self.config.raw_dir)
                    self.db.set_status(paper.paper_id, "downloaded", timestamp, raw_path=str(raw_path))
                zh_path = translate_paper(self.config, paper, raw_path)
                self.db.set_status(paper.paper_id, "translated", timestamp, raw_path=str(raw_path), zh_path=str(zh_path))
                result.translated += 1
                logging.info("Translated %s", paper.title)
            except Exception as exc:  # noqa: BLE001
                result.failed += 1
                self.db.set_status(paper.paper_id, "failed_translate", timestamp, failure_reason=str(exc))
                logging.exception("Failed to translate %s", paper.title)

    def _refresh_status_views(self) -> tuple[list[CandidatePaper], list[CandidatePaper], dict[str, int]]:
        all_papers = self.db.get_papers()
        latest_papers = self.db.get_latest_by_date(today_iso(self.config.timezone))
        status_counts = self.db.counts_by_status()
        return all_papers, latest_papers, status_counts

    def sync_workbuddy_results(self, result: PipelineResult | None = None) -> int:
        timestamp = now_iso(self.config.timezone)
        pending = self.db.get_papers(statuses=["workbuddy_pending", "failed_translate", "queued", "downloaded"])
        synced = 0
        for paper, zh_path, failure_reason in sync_completed_jobs(self.config, pending):
            if zh_path:
                self.db.set_status(paper.paper_id, "translated", timestamp, zh_path=zh_path)
                synced += 1
                if result is not None:
                    result.translated += 1
            elif failure_reason:
                self.db.set_status(paper.paper_id, "failed_translate", timestamp, failure_reason=failure_reason)
                if result is not None:
                    result.failed += 1
        if synced:
            self.db.record_run("workbuddy-sync", "ok", f"synced={synced}", timestamp)
            logging.info("Synced %s translated papers from WorkBuddy outputs", synced)
        return synced

    def prepare_workbuddy(self, result: PipelineResult) -> int:
        timestamp = now_iso(self.config.timezone)
        candidates = self.db.get_papers(statuses=["downloaded", "discovered", "queued", "failed_translate", "workbuddy_pending"])
        top_papers = candidates[: self.config.daily_limit]
        queued_papers = candidates[self.config.daily_limit :]

        for paper in queued_papers:
            self.db.set_status(paper.paper_id, "queued", timestamp)
            result.queued += 1

        prepared = prepare_jobs(self.config, top_papers)
        for paper in prepared:
            self.db.set_status(paper.paper_id, "workbuddy_pending", timestamp, raw_path=paper.raw_path)
            result.queued += 1

        write_daily_brief(self.config, prepared, queued_papers)
        write_task_prompt(self.config)
        self.db.record_run("workbuddy-prepare", "ok", f"prepared={len(prepared)}", timestamp)
        logging.info("Prepared %s WorkBuddy paper jobs", len(prepared))
        return len(prepared)

    def build_site(self) -> None:
        if self.config.workbuddy.enabled:
            self.sync_workbuddy_results()
        all_papers, latest_papers, status_counts = self._refresh_status_views()
        build_site(self.config, all_papers, latest_papers, status_counts)
        run_mkdocs_build(self.config)
        self.db.record_run("site", "ok", "site build complete", now_iso(self.config.timezone))

    def run(
        self,
        *,
        discover_only: bool = False,
        build_only: bool = False,
        prepare_workbuddy_only: bool = False,
        sync_workbuddy_only: bool = False,
        install_workbuddy_skill_only: bool = False,
    ) -> PipelineResult:
        result = PipelineResult()
        if install_workbuddy_skill_only:
            result.git_message = install_skill(self.config)
            return result

        if sync_workbuddy_only:
            self.sync_workbuddy_results(result)
            return result

        if build_only:
            self.build_site()
            result.site_built = True
            result.git_message = sync_git(self.config, self.root)
            return result

        result.discovered = self.discover()
        if discover_only:
            return result

        pending = self.db.get_papers(statuses=["discovered", "queued", "failed_download", "failed_translate"])
        self._download_candidates(pending, result)
        self.sync_workbuddy_results(result)

        if self.config.workbuddy.enabled or prepare_workbuddy_only:
            self.prepare_workbuddy(result)
        else:
            refreshed = self.db.get_papers(statuses=["downloaded", "discovered", "queued", "failed_translate"])
            self._translate_top(refreshed, result)

        # --prepare-workbuddy 模式只准备任务，不构建站点
        if not prepare_workbuddy_only:
            self.build_site()
            result.site_built = True
            result.git_message = sync_git(self.config, self.root)
        return result
