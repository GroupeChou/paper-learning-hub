from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import CandidatePaper
from .utils import ensure_dir


SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    publish_date TEXT NOT NULL,
    theme TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    paper_url TEXT NOT NULL,
    summary TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    raw_path TEXT,
    zh_path TEXT,
    failure_reason TEXT,
    last_seen_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
);
"""


class PaperDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        ensure_dir(db_path.parent)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert_candidate(self, paper: CandidatePaper, timestamp: str) -> None:
        existing = self.conn.execute(
            "SELECT paper_id, status, raw_path, zh_path, failure_reason, created_at FROM papers WHERE paper_id = ?",
            (paper.paper_id,),
        ).fetchone()
        created_at = existing["created_at"] if existing else timestamp
        status = existing["status"] if existing and existing["status"] not in {"failed_download", "failed_translate"} else paper.status
        raw_path = existing["raw_path"] if existing else paper.raw_path
        zh_path = existing["zh_path"] if existing else paper.zh_path
        failure_reason = existing["failure_reason"] if existing else paper.failure_reason
        self.conn.execute(
            """
            INSERT INTO papers (
                paper_id, title, organization, publish_date, theme, source_name, source_url, paper_url, summary,
                priority, status, raw_path, zh_path, failure_reason, last_seen_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(paper_id) DO UPDATE SET
                title = excluded.title,
                organization = excluded.organization,
                publish_date = excluded.publish_date,
                theme = excluded.theme,
                source_name = excluded.source_name,
                source_url = excluded.source_url,
                paper_url = excluded.paper_url,
                summary = excluded.summary,
                priority = excluded.priority,
                status = CASE
                    WHEN papers.status IN ('downloaded', 'translated', 'queued') THEN papers.status
                    WHEN papers.status = 'failed_download' AND papers.raw_path IS NOT NULL THEN 'downloaded'
                    ELSE excluded.status
                END,
                raw_path = COALESCE(papers.raw_path, excluded.raw_path),
                zh_path = COALESCE(papers.zh_path, excluded.zh_path),
                failure_reason = CASE WHEN excluded.status = 'discovered' THEN papers.failure_reason ELSE excluded.failure_reason END,
                last_seen_at = excluded.last_seen_at,
                updated_at = excluded.updated_at
            """,
            (
                paper.paper_id,
                paper.title,
                paper.organization,
                paper.publish_date,
                paper.theme,
                paper.source_name,
                paper.source_url,
                paper.paper_url,
                paper.summary,
                paper.priority,
                status,
                raw_path,
                zh_path,
                failure_reason,
                timestamp,
                created_at,
                timestamp,
            ),
        )
        self.conn.commit()

    def get_papers(self, statuses: list[str] | None = None, limit: int | None = None) -> list[CandidatePaper]:
        query = "SELECT * FROM papers"
        params: list[object] = []
        if statuses:
            placeholders = ",".join("?" for _ in statuses)
            query += f" WHERE status IN ({placeholders})"
            params.extend(statuses)
        query += " ORDER BY priority DESC, publish_date DESC, updated_at DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [CandidatePaper.from_row(row) for row in rows]

    def get_latest_by_date(self, date_prefix: str) -> list[CandidatePaper]:
        rows = self.conn.execute(
            "SELECT * FROM papers WHERE last_seen_at LIKE ? ORDER BY priority DESC, publish_date DESC",
            (f"{date_prefix}%",),
        ).fetchall()
        return [CandidatePaper.from_row(row) for row in rows]

    def set_status(
        self,
        paper_id: str,
        status: str,
        timestamp: str,
        *,
        raw_path: str | None = None,
        zh_path: str | None = None,
        failure_reason: str | None = None,
    ) -> None:
        current = self.conn.execute("SELECT raw_path, zh_path FROM papers WHERE paper_id = ?", (paper_id,)).fetchone()
        resolved_raw = raw_path if raw_path is not None else (current["raw_path"] if current else None)
        resolved_zh = zh_path if zh_path is not None else (current["zh_path"] if current else None)
        self.conn.execute(
            """
            UPDATE papers
            SET status = ?, raw_path = ?, zh_path = ?, failure_reason = ?, updated_at = ?
            WHERE paper_id = ?
            """,
            (status, resolved_raw, resolved_zh, failure_reason, timestamp, paper_id),
        )
        self.conn.commit()

    def record_run(self, step: str, status: str, message: str, timestamp: str) -> None:
        self.conn.execute(
            "INSERT INTO pipeline_runs(step, status, message, created_at) VALUES (?, ?, ?, ?)",
            (step, status, message, timestamp),
        )
        self.conn.commit()

    def counts_by_status(self) -> dict[str, int]:
        rows = self.conn.execute("SELECT status, COUNT(*) AS count FROM papers GROUP BY status").fetchall()
        return {row["status"]: row["count"] for row in rows}

