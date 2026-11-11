from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_lists_catalogue():
    r = client.get("/")
    assert r.status_code == 200
    assert "Test Case Tracker" in r.text
    assert "Links and images" in r.text


def test_run_echoes_selection():
    r = client.post("/run", data={"url": "https://example.com", "tests": ["seo"]})
    assert r.status_code == 200
    assert "https://example.com" in r.text


def test_health():
    assert client.get("/health").json() == {"status": "ok"}
