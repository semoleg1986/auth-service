from __future__ import annotations

import ipaddress
import json
import os
import threading
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

from src.application.dtos import GeoLocation

_DEFAULT_TIMEOUT_SECONDS = 2
_DEFAULT_CACHE_TTL_SECONDS = 900
_DEFAULT_PROVIDER_TEMPLATE = "https://ipwho.is/{ip}"

_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, tuple[float, GeoLocation]] = {}


class IpWhoIsGeoLookup:
    def lookup_by_ip(self, ip_address: str | None) -> GeoLocation:
        return lookup_geo_by_ip(ip_address)


def lookup_geo_by_ip(ip_address: str | None) -> GeoLocation:
    if not _env_bool("AUTH_GEO_LOOKUP_ENABLED", default=False):
        return GeoLocation()
    if not ip_address:
        return GeoLocation()

    normalized_ip = _normalize_ip(ip_address)
    if normalized_ip is None:
        return GeoLocation()
    if not _is_public_ip(normalized_ip):
        return GeoLocation()

    cache_ttl = _env_int(
        "AUTH_GEO_LOOKUP_CACHE_TTL_SECONDS",
        default=_DEFAULT_CACHE_TTL_SECONDS,
    )
    now = time.monotonic()

    with _CACHE_LOCK:
        cached = _CACHE.get(normalized_ip)
        if cached is not None and cached[0] > now:
            return cached[1]

    resolved = _fetch_geo_from_provider(normalized_ip)
    with _CACHE_LOCK:
        _CACHE[normalized_ip] = (now + cache_ttl, resolved)
    return resolved


def _fetch_geo_from_provider(ip_address: str) -> GeoLocation:
    timeout_seconds = _env_int(
        "AUTH_GEO_LOOKUP_TIMEOUT_SECONDS",
        default=_DEFAULT_TIMEOUT_SECONDS,
    )
    provider_template = (
        os.getenv(
            "AUTH_GEO_LOOKUP_URL_TEMPLATE",
            _DEFAULT_PROVIDER_TEMPLATE,
        ).strip()
        or _DEFAULT_PROVIDER_TEMPLATE
    )
    url = provider_template.replace("{ip}", quote(ip_address))

    try:
        with urlopen(url, timeout=timeout_seconds) as response:
            payload = response.read()
    except (TimeoutError, URLError, OSError):
        return GeoLocation()

    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return GeoLocation()
    if not isinstance(decoded, dict):
        return GeoLocation()

    success = decoded.get("success")
    if success is False:
        return GeoLocation()

    city = _clean(decoded.get("city"))
    region = _clean(decoded.get("region")) or _clean(decoded.get("region_name"))
    country = (
        _clean(decoded.get("country_name"))
        or _clean(decoded.get("country"))
        or _clean(decoded.get("countryName"))
    )
    display = _build_display(city=city, region=region, country=country)
    return GeoLocation(city=city, region=region, country=country, display=display)


def _normalize_ip(value: str) -> str | None:
    candidate = value.strip()
    if not candidate:
        return None
    if "," in candidate:
        candidate = candidate.split(",", 1)[0].strip()
    if candidate.startswith("[") and "]" in candidate:
        candidate = candidate[1 : candidate.index("]")]
    return candidate or None


def _is_public_ip(value: str) -> bool:
    try:
        addr = ipaddress.ip_address(value)
    except ValueError:
        return False
    return addr.is_global


def _clean(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _build_display(
    *, city: str | None, region: str | None, country: str | None
) -> str | None:
    parts = [value for value in (city, region, country) if value]
    if not parts:
        return None
    return ", ".join(parts)


def _env_int(name: str, *, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, value)


def _env_bool(name: str, *, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}
