import csv
import io
import re
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import database
from app.catalog import CATALOG
from app.config import settings
from app.runner import run_dir_for, run_tests
from app.security import check_url, normalize_url

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Test Case Tracker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
database.init_db()

TYPE_NAMES = {t["id"]: t["name"] for t in CATALOG}
CSV_COLUMNS = ["Run ID", "Test Type", "Test Case ID", "Title", "Description", "Test Scenario",
               "Test Steps", "Expected Result", "Actual Result", "Status", "Severity",
               "Duration (ms)", "Evidence", "Executed At (UTC)"]


def render_home(request: Request, error: str | None = None, status_code: int = 200, url: str = ""):
    context = {"catalog": CATALOG, "error": error, "url": url, "runs": database.list_runs(),
              "env": settings.app_env}
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_home(request)


@app.post("/run", response_class=HTMLResponse)
def run(request: Request, url: str = Form(""), tests: list[str] = Form(default=[]),
        html_file: UploadFile | None = File(default=None)):
    url = normalize_url(url)
    has_file = html_file is not None and bool(html_file.filename)
    selected = [t for t in tests if t in TYPE_NAMES]

    if not selected:
        return render_home(request, "Select at least one test type.", 400, url)
    if has_file and url:
        return render_home(request, "Give either a URL or an HTML file, not both.", 400, url)
    if not has_file and not url:
        return render_home(request, "Enter a URL or choose an HTML file.", 400)

    html = None
    if has_file:
        data = html_file.file.read(settings.max_html_bytes + 1)
        if len(data) > settings.max_html_bytes:
            return render_home(request, "The HTML file is larger than 2 MB.", 400)
        try:
            html = data.decode("utf-8")
        except UnicodeDecodeError:
            html = data.decode("latin-1")
        mode, target = "html", html_file.filename
    else:
        allowed, reason = check_url(url)
        if not allowed:
            return render_home(request, reason, 400, url)
        mode, target = "url", url

    run_id = database.create_run(mode, target, selected)
    started = time.perf_counter()
    result = run_tests(run_id, mode, target, html, selected)
    database.save_results(run_id, result.get("results", []))
    database.finish_run(run_id, "Error" if result.get("error") else "Completed",
                        result.get("browser", ""), int((time.perf_counter() - started) * 1000),
                        result.get("error"))
    return RedirectResponse(f"/runs/{run_id}", status_code=303)


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def report(request: Request, run_id: int):
    run_row = database.get_run(run_id)
    if not run_row:
        raise HTTPException(404, "Run not found")
    results = database.get_results(run_id)
    counts = {s: sum(1 for r in results if r["status"] == s)
              for s in ("Pass", "Fail", "Warning", "Skipped", "Error")}
    executed = counts["Pass"] + counts["Fail"] + counts["Warning"]
    run_row["display_id"] = f"RUN-{run_id:04d}"
    run_row["type_names"] = [TYPE_NAMES.get(i, i) for i in run_row["test_types"].split(",")]
    context = {"run": run_row, "results": results, "counts": counts, "total": len(results),
               "pass_rate": round(100 * counts["Pass"] / executed) if executed else 0}
    return templates.TemplateResponse(request, "report.html", context)


def _safe_cell(value) -> str:
    text = "" if value is None else str(value)
    # Stops spreadsheet programs from running page-supplied text as a formula.
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@app.get("/runs/{run_id}/csv")
def download_csv(run_id: int):
    if not database.get_run(run_id):
        raise HTTPException(404, "Run not found")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for r in database.get_results(run_id):
        writer.writerow([_safe_cell(v) for v in (
            f"RUN-{run_id:04d}", r["test_type"], r["case_id"], r["title"], r["description"],
            r["scenario"], r["steps"], r["expected"], r["actual"], r["status"], r["severity"],
            r["duration_ms"], r["evidence"], r["executed_at"])])
    body = "\ufeff" + buffer.getvalue()  # BOM so Excel on Windows reads it as UTF-8
    return Response(body, media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="RUN-{run_id:04d}.csv"'})


@app.get("/runs/{run_id}/screenshots/{name}")
def screenshot(run_id: int, name: str):
    if not re.fullmatch(r"[a-z0-9_-]+\.png", name):
        raise HTTPException(404)
    path = run_dir_for(run_id) / "screenshots" / name
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


@app.get("/health")
def health():
    return {"status": "ok"}
