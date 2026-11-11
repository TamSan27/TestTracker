from app.checks.base import FAIL, PASS, Outcome, check

SIZES = [("mobile", 375, 667), ("tablet", 768, 1024), ("desktop", 1366, 768)]
DEFAULT_VIEWPORT = {"width": 1366, "height": 768}


@check("RSP-01")
def no_horizontal_scroll(ctx):
    page = ctx.page
    try:
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(300)
        data = page.evaluate("() => ({sw: document.documentElement.scrollWidth,"
                             " cw: document.documentElement.clientWidth})")
    finally:
        page.set_viewport_size(DEFAULT_VIEWPORT)
    if data["sw"] > data["cw"] + 1:
        return Outcome(FAIL, f"At 375 px the page is {data['sw']} px wide, so it scrolls sideways.")
    return Outcome(PASS, "At 375 px the page fits the screen width.")


@check("RSP-02")
def screenshots(ctx):
    page = ctx.page
    folder = ctx.run_dir / "screenshots"
    folder.mkdir(parents=True, exist_ok=True)
    names = []
    try:
        for name, width, height in SIZES:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(300)
            page.screenshot(path=str(folder / f"{name}.png"))
            names.append(f"{name}.png")
    finally:
        page.set_viewport_size(DEFAULT_VIEWPORT)
    return Outcome(PASS, f"{len(names)} screenshots saved.", "mobile 375 px, tablet 768 px, desktop 1366 px", names)
