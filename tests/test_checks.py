from pathlib import Path
from types import SimpleNamespace

from app.catalog import CATALOG
from app.checks import REGISTRY, Context
from app.worker import run_checks


class FakePage:
    url = "https://shop.test/"

    def title(self):
        return "Shop"

    def evaluate(self, js):
        return "en" if "lang" in js else ""

    def eval_on_selector_all(self, selector, js):
        return 1 if selector == "h1" else []


def make_ctx(headers, load_ms=1200):
    response = SimpleNamespace(headers=headers)
    return Context(mode="url", target="https://shop.test/", run_dir=Path("."), page=FakePage(),
                   response=response, load_ms=load_ms)


def test_every_catalog_case_has_a_check():
    ids = {c["id"] for t in CATALOG for c in t["cases"]}
    assert ids <= set(REGISTRY), ids - set(REGISTRY)


def test_every_case_has_all_report_fields():
    for t in CATALOG:
        for c in t["cases"]:
            for key in ("id", "title", "description", "scenario", "steps", "expected", "severity"):
                assert c[key], (c["id"], key)


def test_security_headers_status_levels():
    full = {"content-security-policy": "default-src 'self'", "x-content-type-options": "nosniff",
            "referrer-policy": "no-referrer", "x-frame-options": "DENY",
            "strict-transport-security": "max-age=1"}
    assert REGISTRY["SEC-02"](make_ctx(full)).status == "Pass"
    two_missing = {k: v for k, v in full.items() if k not in ("referrer-policy", "x-frame-options")}
    assert REGISTRY["SEC-02"](make_ctx(two_missing)).status == "Warning"
    assert REGISTRY["SEC-02"](make_ctx({})).status == "Fail"


def test_performance_thresholds():
    assert REGISTRY["PRF-01"](make_ctx({}, 1200)).status == "Pass"
    assert REGISTRY["PRF-01"](make_ctx({}, 4000)).status == "Warning"
    assert REGISTRY["PRF-01"](make_ctx({}, 9000)).status == "Fail"


def test_seo_checks_with_fake_page():
    ctx = make_ctx({})
    assert REGISTRY["SEO-01"](ctx).status == "Pass"
    assert REGISTRY["SEO-03"](ctx).status == "Pass"


def test_run_checks_builds_complete_rows_and_survives_crashes():
    selected = [t for t in CATALOG if t["id"] in ("seo", "security", "performance")]
    rows = run_checks(selected, make_ctx({}))
    assert len(rows) == sum(len(t["cases"]) for t in selected)
    # SEO-02 calls evaluate() on the fake page and gets '' back -> Fail, not a crash
    assert {r["case_id"]: r["status"] for r in rows}["SEO-02"] == "Fail"
    for r in rows:
        assert r["status"] in ("Pass", "Fail", "Warning", "Skipped", "Error")
        assert r["executed_at"] and r["expected"] and r["scenario"]
