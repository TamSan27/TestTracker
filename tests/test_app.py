from fastapi.testclient import TestClient

import app.main as main
from app.main import app

client = TestClient(app)

FAKE_RESULT = {
    "browser": "Chromium test",
    "error": None,
    "results": [
        {"test_type": "SEO basics", "case_id": "SEO-01", "title": "Page has a title",
         "description": "d", "scenario": "s", "steps": "1. a\n2. b", "expected": "e",
         "actual": "=SUM(1,2)", "status": "Pass", "severity": "Medium", "duration_ms": 5,
         "evidence": "Home", "attachments": [], "executed_at": "2026-01-01T00:00:00+00:00"},
        {"test_type": "SEO basics", "case_id": "SEO-02", "title": "Meta description present",
         "description": "d", "scenario": "s", "steps": "1. a", "expected": "e",
         "actual": "none", "status": "Fail", "severity": "Low", "duration_ms": 3,
         "evidence": "", "attachments": [], "executed_at": "2026-01-01T00:00:00+00:00"},
    ],
}


def test_home_lists_catalogue():
    r = client.get("/")
    assert r.status_code == 200
    assert "Links and images" in r.text


def test_validation_errors():
    assert client.post("/run", data={"url": "https://example.com"}).status_code == 400  # no tests
    assert client.post("/run", data={"tests": ["seo"]}).status_code == 400            # no target
    r = client.post("/run", data={"url": "http://127.0.0.1:8000", "tests": ["seo"]})
    assert r.status_code == 400 and "blocked" in r.text


def test_full_flow_with_fake_runner(monkeypatch):
    monkeypatch.setattr(main, "run_tests", lambda *a, **k: FAKE_RESULT)
    r = client.post("/run", data={"url": "http://8.8.8.8", "tests": ["seo"]}, follow_redirects=False)
    assert r.status_code == 303
    page = client.get(r.headers["location"])
    assert page.status_code == 200
    assert "SEO-01" in page.text and "Pass rate" in page.text and "50%" in page.text
    run_id = r.headers["location"].rsplit("/", 1)[1]
    csv_resp = client.get(f"/runs/{run_id}/csv")
    assert csv_resp.status_code == 200
    assert "Test Case ID" in csv_resp.text
    assert "'=SUM(1,2)" in csv_resp.text  # formula text is neutralised


def test_html_upload_flow(monkeypatch):
    seen = {}

    def fake(run_id, mode, target, html, types):
        seen.update(mode=mode, target=target, html=html)
        return FAKE_RESULT

    monkeypatch.setattr(main, "run_tests", fake)
    files = {"html_file": ("page.html", b"<html><body>Hi</body></html>", "text/html")}
    r = client.post("/run", data={"tests": ["seo"]}, files=files, follow_redirects=False)
    assert r.status_code == 303
    assert seen["mode"] == "html" and "Hi" in seen["html"]


def test_unknown_run_and_screenshot_are_404():
    assert client.get("/runs/9999").status_code == 404
    assert client.get("/runs/1/screenshots/..%2Fsecret.png").status_code == 404
    assert client.get("/runs/1/screenshots/nothing.png").status_code == 404


def test_health():
    assert client.get("/health").json() == {"status": "ok"}
