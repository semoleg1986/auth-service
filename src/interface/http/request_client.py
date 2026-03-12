from __future__ import annotations

from fastapi import Request

from src.application.dtos import GeoLocation

_USER_AGENT_MAX_LEN = 512
_GEO_VALUE_MAX_LEN = 128
_GEO_DISPLAY_MAX_LEN = 255


def extract_client_ip(request: Request) -> str | None:
    """
    Извлечь IP клиента из HTTP-запроса.

    Приоритет:
    1) X-Forwarded-For (первый IP)
    2) X-Real-IP
    3) request.client.host
    """
    forwarded_for = _header_value(request, "X-Forwarded-For")
    if forwarded_for:
        first_ip = forwarded_for.split(",", 1)[0].strip()
        if first_ip:
            return first_ip

    real_ip = _header_value(request, "X-Real-IP")
    if real_ip:
        return real_ip

    if request.client and request.client.host:
        return request.client.host
    return None


def extract_user_agent(request: Request) -> str | None:
    user_agent = _header_value(request, "User-Agent")
    return _truncate(user_agent, _USER_AGENT_MAX_LEN)


def extract_geo_metadata(request: Request) -> GeoLocation:
    city = _first_existing_header(
        request,
        (
            "X-Geo-City",
            "CF-IPCity",
            "CloudFront-Viewer-City",
        ),
    )
    region = _first_existing_header(
        request,
        (
            "X-Geo-Region",
            "CloudFront-Viewer-Country-Region",
        ),
    )
    country = _first_existing_header(
        request,
        (
            "X-Geo-Country",
            "CF-IPCountry",
            "CloudFront-Viewer-Country",
        ),
    )

    city = _truncate(city, _GEO_VALUE_MAX_LEN)
    region = _truncate(region, _GEO_VALUE_MAX_LEN)
    country = _truncate(country, _GEO_VALUE_MAX_LEN)
    display = _build_geo_display(city=city, region=region, country=country)
    return GeoLocation(city=city, region=region, country=country, display=display)


def _first_existing_header(request: Request, names: tuple[str, ...]) -> str | None:
    for name in names:
        value = _header_value(request, name)
        if value:
            return value
    return None


def _header_value(request: Request, name: str) -> str | None:
    raw = request.headers.get(name)
    if raw is None:
        return None
    normalized = raw.strip()
    if not normalized:
        return None
    return normalized


def _build_geo_display(
    *, city: str | None, region: str | None, country: str | None
) -> str | None:
    parts = [item for item in (city, region, country) if item]
    if not parts:
        return None
    return _truncate(", ".join(parts), _GEO_DISPLAY_MAX_LEN)


def _truncate(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    if len(value) <= max_len:
        return value
    return value[:max_len]
