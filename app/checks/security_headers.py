from app.checks.base import ERROR, FAIL, PASS, SKIPPED, WARNING, Outcome, check


@check("SEC-01")
def uses_https(ctx):
    if ctx.mode != "url":
        return Outcome(SKIPPED, "Not applicable to an uploaded HTML file.")
    final = ctx.page.url
    if final.startswith("https://"):
        return Outcome(PASS, "The page is served over HTTPS.", final)
    return Outcome(FAIL, "The page is not served over HTTPS.", final)


@check("SEC-02")
def security_headers(ctx):
    if ctx.mode != "url":
        return Outcome(SKIPPED, "Not applicable to an uploaded HTML file.")
    if ctx.response is None:
        return Outcome(ERROR, "No main response was recorded.")
    headers = {k.lower(): v for k, v in ctx.response.headers.items()}
    csp = headers.get("content-security-policy", "")
    required = {
        "Content-Security-Policy": bool(csp),
        "X-Content-Type-Options": "x-content-type-options" in headers,
        "Referrer-Policy": "referrer-policy" in headers,
        "Clickjacking protection (X-Frame-Options or CSP frame-ancestors)":
            "x-frame-options" in headers or "frame-ancestors" in csp,
    }
    if ctx.page.url.startswith("https://"):
        required["Strict-Transport-Security"] = "strict-transport-security" in headers
    missing = [name for name, present in required.items() if not present]
    if not missing:
        return Outcome(PASS, "All checked security headers are present.")
    status = WARNING if len(missing) <= 2 else FAIL
    return Outcome(status, f"{len(missing)} of {len(required)} security headers are missing.",
                   "Missing: " + "; ".join(missing))
