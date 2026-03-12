from __future__ import annotations

from src.application.dtos import GeoLocation
from src.application.services import enrich_geo_location


class _StubGeoLookup:
    def __init__(self, result: GeoLocation) -> None:
        self._result = result
        self.calls: list[str | None] = []

    def lookup_by_ip(self, ip_address: str | None) -> GeoLocation:
        self.calls.append(ip_address)
        return self._result


def test_enricher_keeps_header_geo_without_lookup() -> None:
    lookup = _StubGeoLookup(result=GeoLocation(city="Should", country="NotUse"))
    header_geo = GeoLocation(city="Batumi", region="Adjara", country="Georgia")

    result = enrich_geo_location(
        ip_address="89.168.77.132",
        header_geo=header_geo,
        geo_lookup=lookup,
    )

    assert result.city == "Batumi"
    assert result.region == "Adjara"
    assert result.country == "Georgia"
    assert result.display == "Batumi, Adjara, Georgia"
    assert lookup.calls == []


def test_enricher_uses_lookup_when_header_geo_empty() -> None:
    expected = GeoLocation(
        city="Batumi",
        region="Adjara",
        country="Georgia",
        display="Batumi, Adjara, Georgia",
    )
    lookup = _StubGeoLookup(result=expected)

    result = enrich_geo_location(
        ip_address="89.168.77.132",
        header_geo=GeoLocation(),
        geo_lookup=lookup,
    )

    assert result == expected
    assert lookup.calls == ["89.168.77.132"]
