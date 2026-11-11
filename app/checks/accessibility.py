from app.checks.base import FAIL, PASS, SKIPPED, Outcome, check, sample

FIELDS_JS = """() => {
  const skip = ['hidden', 'submit', 'button', 'reset', 'image'];
  const fields = Array.from(document.querySelectorAll('input, select, textarea'))
    .filter(e => !skip.includes((e.getAttribute('type') || '').toLowerCase()));
  const missing = fields.filter(e =>
    !(e.labels && e.labels.length) &&
    !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby') && !e.getAttribute('title'));
  return {total: fields.length, missing: missing.map(e => e.name || e.id || e.tagName.toLowerCase())};
}"""


@check("ACC-01")
def images_have_alt(ctx):
    total = ctx.page.eval_on_selector_all("img", "els => els.length")
    if not total:
        return Outcome(SKIPPED, "No images were found.")
    missing = ctx.page.eval_on_selector_all(
        "img", "els => els.filter(i => !i.hasAttribute('alt')).map(i => i.currentSrc || i.src || '(no src)')")
    if missing:
        return Outcome(FAIL, f"{len(missing)} of {total} images have no alt attribute.", sample(missing))
    return Outcome(PASS, f"All {total} images have an alt attribute.")


@check("ACC-02")
def fields_have_labels(ctx):
    data = ctx.page.evaluate(FIELDS_JS)
    if not data["total"]:
        return Outcome(SKIPPED, "No form fields were found.")
    if data["missing"]:
        return Outcome(FAIL, f"{len(data['missing'])} of {data['total']} form fields have no label.",
                       "Fields: " + sample(data["missing"]))
    return Outcome(PASS, f"All {data['total']} form fields have a label.")


@check("ACC-03")
def page_language(ctx):
    lang = (ctx.page.evaluate("document.documentElement.getAttribute('lang')") or "").strip()
    if lang:
        return Outcome(PASS, f"The page language is '{lang}'.")
    return Outcome(FAIL, "The html tag has no lang attribute.")
