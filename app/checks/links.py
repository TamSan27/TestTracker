from urllib.parse import urldefrag, urljoin

from app.checks.base import FAIL, PASS, SKIPPED, WARNING, Outcome, check, sample
from app.security import check_url

MAX_LINKS = 30


@check("LNK-01")
def links_respond(ctx):
    hrefs = ctx.page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    base = ctx.page.url if ctx.mode == "url" else None
    urls = []
    for href in hrefs:
        href = (href or "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urldefrag(urljoin(base, href) if base else href)[0]
        if full.startswith(("http://", "https://")) and full not in urls:
            urls.append(full)
    if not urls:
        return Outcome(SKIPPED, "No checkable http(s) links were found.")

    hard, soft, unchecked = [], [], []
    for url in urls[:MAX_LINKS]:
        allowed, _ = check_url(url)
        if not allowed:
            unchecked.append(url)
            continue
        try:
            status = ctx.page.request.get(url, timeout=8000, max_redirects=0).status
        except Exception as exc:  # timeout, DNS failure, etc.
            soft.append(f"{url} (no response: {type(exc).__name__})")
            continue
        if status in (404, 410) or status >= 500:
            hard.append(f"{url} -> {status}")
        elif status >= 400:
            soft.append(f"{url} -> {status}")

    actual = (f"Checked {len(urls[:MAX_LINKS]) - len(unchecked)} of {len(urls)} unique links: "
              f"{len(hard)} broken, {len(soft)} could not be verified.")
    if unchecked:
        actual += f" {len(unchecked)} skipped (private/internal address)."
    problems = hard + soft
    status = FAIL if hard else WARNING if soft else PASS
    return Outcome(status, actual, sample(problems))


@check("LNK-02")
def images_load(ctx):
    total = ctx.page.eval_on_selector_all("img", "els => els.length")
    if not total:
        return Outcome(SKIPPED, "No images were found.")
    broken = ctx.page.eval_on_selector_all(
        "img",
        "els => els.filter(i => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src)"
        " && !/\\.svg($|\\?)/i.test(i.currentSrc || i.src) && !(i.currentSrc || i.src).startsWith('data:image/svg'))"
        ".map(i => i.currentSrc || i.src)",
    )
    if broken:
        return Outcome(FAIL, f"{len(broken)} of {total} images failed to load.", sample(broken))
    return Outcome(PASS, f"All {total} images loaded.")
