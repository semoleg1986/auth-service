from __future__ import annotations

from typing import Protocol

from src.application.dtos import GeoLocation


class GeoLookupPort(Protocol):
    def lookup_by_ip(self, ip_address: str | None) -> GeoLocation:
        ...
