from __future__ import annotations

from src.interface.http.geo_lookup import GeoLookupResult, lookup_geo_by_ip


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    def read(self) -> bytes:
        return self._payload


def test_geo_lookup_disabled_by_default() -> None:
    result = lookup_geo_by_ip("8.8.8.8")
    assert result == GeoLookupResult()


def test_geo_lookup_skips_private_ip(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_GEO_LOOKUP_ENABLED", "true")
    result = lookup_geo_by_ip("172.19.0.1")
    assert result == GeoLookupResult()


def test_geo_lookup_resolves_public_ip(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_GEO_LOOKUP_ENABLED", "true")
    monkeypatch.setenv("AUTH_GEO_LOOKUP_CACHE_TTL_SECONDS", "1")
    monkeypatch.setattr(
        "src.interface.http.geo_lookup.urlopen",
        lambda *args, **kwargs: _FakeResponse(
            b'{"success":true,"city":"Batumi","region":"Adjara","country":"Georgia"}'
        ),
    )

    result = lookup_geo_by_ip("89.168.77.132")
    assert result.city == "Batumi"
    assert result.region == "Adjara"
    assert result.country == "Georgia"
    assert result.display == "Batumi, Adjara, Georgia"


def test_geo_lookup_provider_failure(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_GEO_LOOKUP_ENABLED", "true")
    monkeypatch.setattr(
        "src.interface.http.geo_lookup.urlopen",
        lambda *args, **kwargs: _FakeResponse(
            b'{"success":false,"message":"reserved range"}'
        ),
    )

    result = lookup_geo_by_ip("8.8.4.4")
    assert result == GeoLookupResult()
