from __future__ import annotations

from src.application.dtos import GeoLocation
from src.application.ports import GeoLookupPort


def enrich_geo_location(
    *, ip_address: str | None, header_geo: GeoLocation, geo_lookup: GeoLookupPort
) -> GeoLocation:
    if not header_geo.is_empty():
        return GeoLocation(
            city=header_geo.city,
            region=header_geo.region,
            country=header_geo.country,
            display=header_geo.display or _build_display(header_geo),
        )
    return geo_lookup.lookup_by_ip(ip_address)


def _build_display(geo: GeoLocation) -> str | None:
    parts = [value for value in (geo.city, geo.region, geo.country) if value]
    if not parts:
        return None
    return ", ".join(parts)
