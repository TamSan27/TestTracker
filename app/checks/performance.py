from app.checks.base import FAIL, PASS, SKIPPED, WARNING, Outcome, check


@check("PRF-01")
def load_time(ctx):
    if ctx.mode != "url" or ctx.load_ms is None:
        return Outcome(SKIPPED, "Not applicable to an uploaded HTML file.")
    seconds = ctx.load_ms / 1000
    status = PASS if seconds < 3 else WARNING if seconds < 6 else FAIL
    return Outcome(status, f"The page loaded in {seconds:.2f} seconds.")


@check("PRF-02")
def page_size(ctx):
    if ctx.mode != "url":
        return Outcome(SKIPPED, "Not applicable to an uploaded HTML file.")
    total = 0
    for request in ctx.finished:
        try:
            sizes = request.sizes()
            total += sizes["responseBodySize"] + sizes["responseHeadersSize"]
        except Exception:
            pass
    mb = total / (1024 * 1024)
    status = PASS if mb < 3 else WARNING if mb < 6 else FAIL
    return Outcome(status, f"Downloaded {mb:.2f} MB in {len(ctx.finished)} requests.")
