"""Stores runs and results in a single SQLite file."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    mode TEXT NOT NULL,
    target TEXT NOT NULL,
    test_types TEXT NOT NULL,
    status TEXT NOT NULL,
    browser TEXT DEFAULT '',
    duration_ms INTEGER DEFAULT 0,
    error TEXT
);
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    test_type TEXT, case_id TEXT, title TEXT, description TEXT,
    scenario TEXT, steps TEXT, expected TEXT, actual TEXT,
    status TEXT, severity TEXT, duration_ms INTEGER,
    evidence TEXT, attachments TEXT, executed_at TEXT
);
"""


@contextmanager
def connect():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def create_run(mode: str, target: str, test_types: list[str]) -> int:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO runs (created_at, mode, target, test_types, status) VALUES (?,?,?,?,?)",
            (now, mode, target, ",".join(test_types), "Running"),
        )
        return cur.lastrowid


def finish_run(run_id: int, status: str, browser: str, duration_ms: int, error: str | None) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE runs SET status=?, browser=?, duration_ms=?, error=? WHERE id=?",
            (status, browser, duration_ms, error, run_id),
        )


def save_results(run_id: int, rows: list[dict]) -> None:
    with connect() as conn:
        conn.executemany(
            "INSERT INTO results (run_id, test_type, case_id, title, description, scenario, steps,"
            " expected, actual, status, severity, duration_ms, evidence, attachments, executed_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    run_id, r["test_type"], r["case_id"], r["title"], r["description"], r["scenario"],
                    r["steps"], r["expected"], r["actual"], r["status"], r["severity"],
                    r["duration_ms"], r.get("evidence", ""), ",".join(r.get("attachments", [])),
                    r["executed_at"],
                )
                for r in rows
            ],
        )


def get_run(run_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_results(run_id: int) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM results WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["attachments"] = [a for a in (item["attachments"] or "").split(",") if a]
        out.append(item)
    return out


def list_runs(limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]
