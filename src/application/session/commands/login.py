from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    identifier: str  # email or phone
    password: str
    ip_address: str | None = None
    user_agent: str | None = None
    geo_city: str | None = None
    geo_region: str | None = None
    geo_country: str | None = None
    geo_display: str | None = None
