from __future__ import annotations

from src.application.dtos import GeoLocation


class NoopGeoLookup:
    def lookup_by_ip(self, ip_address: str | None) -> GeoLocation:
        del ip_address
        return GeoLocation()
