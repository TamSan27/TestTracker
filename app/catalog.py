"""The catalogue of test types and the test cases inside each type."""

CATALOG = [
    {
        "id": "links",
        "name": "Links and images",
        "description": "Finds broken links and images.",
        "cases": [
            {"id": "LNK-01", "title": "All links respond", "description": "Every link on the page returns a non-error status."},
            {"id": "LNK-02", "title": "All images load", "description": "Every image on the page loads successfully."},
        ],
    },
    {
        "id": "accessibility",
        "name": "Accessibility basics",
        "description": "Checks simple rules that help all users, including screen-reader users.",
        "cases": [
            {"id": "ACC-01", "title": "Images have alt text", "description": "Every image has an alt attribute."},
            {"id": "ACC-02", "title": "Form fields have labels", "description": "Every input has a label or aria-label."},
            {"id": "ACC-03", "title": "Page language is set", "description": "The html tag has a lang attribute."},
        ],
    },
    {
        "id": "seo",
        "name": "SEO basics",
        "description": "Checks what search engines look for.",
        "cases": [
            {"id": "SEO-01", "title": "Page has a title", "description": "The title tag exists and is not empty."},
            {"id": "SEO-02", "title": "Meta description present", "description": "A meta description tag exists."},
            {"id": "SEO-03", "title": "Exactly one H1", "description": "The page has one h1 heading."},
        ],
    },
    {
        "id": "spelling",
        "name": "Spelling and content",
        "description": "Checks visible text for spelling mistakes, without any outside service.",
        "cases": [
            {"id": "SPL-01", "title": "No spelling mistakes", "description": "Visible words are found in an offline dictionary."},
        ],
    },
    {
        "id": "security",
        "name": "Security headers and HTTPS",
        "description": "Checks basic security settings of the site.",
        "cases": [
            {"id": "SEC-01", "title": "Uses HTTPS", "description": "The page is served over HTTPS."},
            {"id": "SEC-02", "title": "Security headers present", "description": "Headers such as Content-Security-Policy and X-Content-Type-Options exist."},
        ],
    },
    {
        "id": "performance",
        "name": "Performance",
        "description": "Measures how fast and heavy the page is.",
        "cases": [
            {"id": "PRF-01", "title": "Page loads in time", "description": "Load time is under the allowed limit."},
            {"id": "PRF-02", "title": "Page size is reasonable", "description": "Total downloaded size is under the allowed limit."},
        ],
    },
    {
        "id": "responsive",
        "name": "Responsive layout",
        "description": "Checks the page at mobile, tablet and desktop sizes.",
        "cases": [
            {"id": "RSP-01", "title": "No sideways scrolling on mobile", "description": "At phone width the page does not scroll horizontally."},
            {"id": "RSP-02", "title": "Screenshots captured", "description": "Screenshots are saved at three screen sizes."},
        ],
    },
    {
        "id": "browser_health",
        "name": "Browser health",
        "description": "Looks for errors the browser reports while loading.",
        "cases": [
            {"id": "BRW-01", "title": "No JavaScript console errors", "description": "The browser console shows no errors."},
            {"id": "BRW-02", "title": "No failed network calls", "description": "No request fails while loading the page."},
        ],
    },
]
