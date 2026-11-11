import re

from app.checks.base import ERROR, PASS, SKIPPED, WARNING, Outcome, check

WORD = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)?")


@check("SPL-01")
def spelling(ctx):
    lang = (ctx.page.evaluate("document.documentElement.getAttribute('lang') || 'en'") or "en").lower()
    if not lang.startswith("en"):
        return Outcome(SKIPPED, f"Page language is '{lang}'. Only English is supported.")
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return Outcome(ERROR, "pyspellchecker is not installed. Run: pip install -r requirements.txt")

    text = ctx.page.evaluate("document.body ? document.body.innerText : ''")
    candidates = set()
    for raw in WORD.findall(text):
        word = re.split(r"['\u2019]", raw)[0]
        # Only plain lowercase words of 4+ letters: skips brand names, acronyms and short words.
        if len(word) >= 4 and word == word.lower():
            candidates.add(word)
    if not candidates:
        return Outcome(SKIPPED, "No words were available to check.")
    unknown = sorted(SpellChecker().unknown(candidates))
    if unknown:
        return Outcome(
            WARNING,
            f"{len(unknown)} possible misspelling(s) among {len(candidates)} unique words. Review manually.",
            ", ".join(unknown[:15]),
        )
    return Outcome(PASS, f"No unknown words among {len(candidates)} unique words.")
