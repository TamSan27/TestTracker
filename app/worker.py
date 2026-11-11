"""Runs ONE test run inside its own process: python -m app.worker input.json output.json

Playwright runs here, separate from the web server. This keeps the web app responsive
and avoids a known Windows problem between uvicorn and Playwright.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from app.catalog import CATALOG
from app.checks import REGISTRY, Context, Outcome
from app.security import check_url

VIEWPORT = {"width": 1366, "height": 768}
ALLOWED_SCHEMES = ("http", "https", "data", "blob", "about")
SCROLL_JS = """async () => {
  for (let i = 0; i < 30; i++) {
    window.scrollBy(0, 600);
    await new Promise(r => setTimeout(r, 100));
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight) break;
  }
  window.scrollTo(0, 0);
}"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row(test_type: dict, case: dict, outcome: Outcome, duration_ms: int) -> dict:
    return {
        "test_type": test_type["name"], "case_id": case["id"], "title": case["title"],
        "description": case["description"], "scenario": case["scenario"], "steps": case["steps"],
        "expected": case["expected"], "actual": outcome.actual, "status": outcome.status,
        "severity": case["severity"], "duration_ms": duration_ms, "evidence": outcome.evidence,
        "attachments": outcome.attachments, "executed_at": _now(),
    }


def run_checks(selected: list[dict], ctx: Context) -> list[dict]:
    rows = []
    for test_type in selected:
        for case in test_type["cases"]:
            fn = REGISTRY.get(case["id"])
            start = time.perf_counter()
            try:
                outcome = fn(ctx) if fn else Outcome("Skipped", "No automated check exists for this case yet.")
            except Exception as exc:  # one broken check must not stop the others
                outcome = Outcome("Error", f"The check crashed: {type(exc).__name__}: {exc}")
            rows.append(_row(test_type, case, outcome, int((time.perf_counter() - start) * 1000)))
    return rows


def _error_rows(selected: list[dict], message: str) -> list[dict]:
    return [_row(t, c, Outcome("Error", message), 0) for t in selected for c in t["cases"]]


def main(in_path: str, out_path: str) -> None:
    payload = json.loads(Path(in_path).read_text(encoding="utf-8"))
    selected = [t for t in CATALOG if t["id"] in payload["types"]]
    output = {"browser": "", "error": None, "results": []}

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            output["browser"] = f"Chromium {browser.version}"
            context = browser.new_context(viewport=VIEWPORT)
            page = context.new_page()
            ctx = Context(mode=payload["mode"], target=payload["target"],
                          run_dir=Path(payload["run_dir"]), page=page)

            def guard(route):
                url = route.request.url
                scheme = url.split(":", 1)[0].lower()
                if scheme not in ALLOWED_SCHEMES:
                    route.abort()
                    return
                if scheme in ("http", "https") and not check_url(url)[0]:
                    ctx.blocked.append(url)
                    route.abort()
                    return
                route.continue_()

            context.route("**/*", guard)
            page.on("console", lambda m: ctx.console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: ctx.console_errors.append(f"Uncaught: {e}"))
            page.on("requestfailed", lambda r: ctx.failed_requests.append(f"{r.url} ({r.failure})"))
            page.on("requestfinished", lambda r: ctx.finished.append(r))
            page.on("response", lambda r: ctx.bad_responses.append(f"{r.status} {r.url}") if r.status >= 400 else None)

            try:
                if payload["mode"] == "url":
                    start = time.perf_counter()
                    ctx.response = page.goto(payload["target"], wait_until="load", timeout=30000)
                    ctx.load_ms = int((time.perf_counter() - start) * 1000)
                else:
                    page.set_content(payload["html"], wait_until="load", timeout=30000)
                page.evaluate(SCROLL_JS)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
            except Exception as exc:
                output["error"] = f"Could not open the page: {type(exc).__name__}: {str(exc).splitlines()[0]}"
                output["results"] = _error_rows(selected, output["error"])
            else:
                output["results"] = run_checks(selected, ctx)
            browser.close()
    except Exception as exc:
        output["error"] = f"{type(exc).__name__}: {exc}"
        if not output["results"]:
            output["results"] = _error_rows(selected, output["error"])

    Path(out_path).write_text(json.dumps(output), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
