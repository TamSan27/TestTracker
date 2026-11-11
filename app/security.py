"""Safety guard: stops the app from being tricked into visiting internal addresses (SSRF)."""
import ipaddress
import socket
from functools import lru_cache
from urllib.parse import urlparse

from app.config import settings


def normalize_url(raw: str) -> str:
    raw = (raw or "").strip()
    if raw and "://" not in raw:
        raw = "https://" + raw
    return raw


@lru_cache(maxsize=512)
def _host_is_public(host: str, port: int) -> bool:
    infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            return False
    return True


def check_url(url: str) -> tuple[bool, str]:
    """Return (allowed, reason). Only public http/https addresses are allowed."""
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError:
        return False, "The URL is not valid."
    if parsed.scheme not in ("http", "https"):
        return False, "Only http:// and https:// URLs are allowed."
    host = parsed.hostname
    if not host:
        return False, "The URL has no host name."
    if settings.allow_private_urls:
        return True, ""
    port = port or (443 if parsed.scheme == "https" else 80)
    try:
        public = _host_is_public(host, port)
    except socket.gaierror:
        return False, f"Could not find the host name '{host}'."
    if not public:
        return False, "Private, local and internal addresses are blocked for safety."
    return True, ""
