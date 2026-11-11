"""Shared building blocks for all checks."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

PASS, FAIL, WARNING, SKIPPED, ERROR = "Pass", "Fail", "Warning", "Skipped", "Error"


@dataclass
class Outcome:
    status: str
    actual: str
    evidence: str = ""
    attachments: list = field(default_factory=list)


@dataclass
class Context:
    """Everything a check may need, collected while the page was opened."""
    mode: str                      # "url" or "html"
    target: str
    run_dir: Path
    page: Any
    response: Any = None           # main page response (url mode only)
    load_ms: int | None = None
    console_errors: list = field(default_factory=list)
    failed_requests: list = field(default_factory=list)
    bad_responses: list = field(default_factory=list)
    blocked: list = field(default_factory=list)
    finished: list = field(default_factory=list)


REGISTRY: dict[str, Callable[[Context], Outcome]] = {}


def check(case_id: str):
    """Decorator that registers a function as the automated check for a test case ID."""
    def register(fn):
        REGISTRY[case_id] = fn
        return fn
    return register


def sample(items: list, limit: int = 5) -> str:
    shown = [str(i) for i in items[:limit]]
    extra = len(items) - len(shown)
    return "; ".join(shown) + (f" (+{extra} more)" if extra > 0 else "")
