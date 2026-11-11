from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.catalog import CATALOG
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Test Case Tracker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    context = {"catalog": CATALOG, "selection": None, "env": settings.app_env}
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/run", response_class=HTMLResponse)
def run(request: Request, url: str = Form(...), tests: list[str] = Form(default=[])):
    # Step A only echoes the selection back. Step B will actually run the tests.
    selection = {
        "url": url.strip(),
        "tests": [t for t in CATALOG if t["id"] in tests],
    }
    context = {"catalog": CATALOG, "selection": selection, "env": settings.app_env}
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/health")
def health():
    return {"status": "ok"}
