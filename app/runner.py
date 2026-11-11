"""Starts the worker process for one run and returns its results."""
import json
import subprocess
import sys

from app.catalog import CATALOG
from app.config import BASE_DIR, settings


def run_dir_for(run_id: int):
    return settings.reports_dir / f"RUN-{run_id:04d}"


def run_tests(run_id: int, mode: str, target: str, html: str | None, type_ids: list[str]) -> dict:
    run_dir = run_dir_for(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": mode, "target": target, "html": html,
        "types": [t["id"] for t in CATALOG if t["id"] in type_ids],
        "run_dir": str(run_dir),
    }
    in_path, out_path = run_dir / "input.json", run_dir / "output.json"
    in_path.write_text(json.dumps(payload), encoding="utf-8")
    out_path.unlink(missing_ok=True)

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "app.worker", str(in_path), str(out_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=settings.run_timeout, cwd=BASE_DIR,
        )
    except subprocess.TimeoutExpired:
        return {"browser": "", "results": [],
                "error": f"The run was stopped after {settings.run_timeout} seconds."}

    if not out_path.exists():
        tail = (proc.stderr or "").strip().splitlines()[-3:]
        return {"browser": "", "results": [],
                "error": "The test worker stopped unexpectedly. " + " | ".join(tail)}
    return json.loads(out_path.read_text(encoding="utf-8"))
