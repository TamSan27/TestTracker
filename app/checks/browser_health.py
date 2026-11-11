from app.checks.base import FAIL, PASS, Outcome, check, sample


@check("BRW-01")
def console_errors(ctx):
    if ctx.console_errors:
        return Outcome(FAIL, f"{len(ctx.console_errors)} console error(s) were reported.", sample(ctx.console_errors, 3))
    return Outcome(PASS, "No console errors were reported.")


@check("BRW-02")
def failed_requests(ctx):
    problems = ctx.failed_requests + ctx.bad_responses
    note = f" {len(ctx.blocked)} request(s) were blocked by the safety guard." if ctx.blocked else ""
    if problems:
        return Outcome(FAIL, f"{len(problems)} request(s) failed or returned an error status.{note}", sample(problems, 4))
    return Outcome(PASS, "No failed network calls." + note)
