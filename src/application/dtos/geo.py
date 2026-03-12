from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoLocation:
    city: str | None = None
    region: str | None = None
    country: str | None = None
    display: str | None = None

    def is_empty(self) -> bool:
        return not any((self.city, self.region, self.country, self.display))
