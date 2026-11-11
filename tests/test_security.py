from app.security import check_url, normalize_url


def test_normalize_adds_https():
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("  http://a.b ") == "http://a.b"


def test_blocks_private_and_local_addresses():
    for url in ("http://127.0.0.1", "http://localhost:8000", "http://10.0.0.5",
                "http://192.168.1.1", "http://169.254.169.254/latest/meta-data", "http://[::1]/"):
        assert check_url(url)[0] is False, url


def test_blocks_other_schemes():
    assert check_url("file:///etc/passwd")[0] is False
    assert check_url("ftp://example.com")[0] is False


def test_allows_public_ip():
    assert check_url("http://8.8.8.8")[0] is True
