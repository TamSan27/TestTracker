from app.checks.base import ERROR, FAIL, PASS, REGISTRY, SKIPPED, WARNING, Context, Outcome  # noqa: F401

# Importing these modules registers their checks in REGISTRY.
from app.checks import (  # noqa: F401,E402
    accessibility,
    browser_health,
    links,
    performance,
    responsive,
    security_headers,
    seo,
    spelling,
)
