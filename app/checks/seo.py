from app.checks.base import FAIL, PASS, WARNING, Outcome, check


@check("SEO-01")
def has_title(ctx):
    title = (ctx.page.title() or "").strip()
    if title:
        return Outcome(PASS, f"Title found ({len(title)} characters).", title[:120])
    return Outcome(FAIL, "The page has no title.")


@check("SEO-02")
def has_meta_description(ctx):
    desc = ctx.page.evaluate(
        "(document.querySelector('meta[name=description]') || {}).content || ''").strip()
    if desc:
        return Outcome(PASS, f"Meta description found ({len(desc)} characters).", desc[:160])
    return Outcome(FAIL, "No meta description was found.")


@check("SEO-03")
def one_h1(ctx):
    count = ctx.page.eval_on_selector_all("h1", "els => els.length")
    if count == 1:
        return Outcome(PASS, "Exactly one h1 element was found.")
    if count == 0:
        return Outcome(FAIL, "No h1 element was found.")
    return Outcome(WARNING, f"{count} h1 elements were found; one is recommended.")
