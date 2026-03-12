from __future__ import annotations

import math
import os
import threading
import time
from collections import deque
from dataclasses import dataclass

from fastapi import Request

from src.interface.http.request_client import extract_client_ip


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    methods: tuple[str, ...]
    path_prefixes: tuple[str, ...]
    max_requests: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitViolation:
    rule_name: str
    retry_after_seconds: int


class RequestRateLimiter:
    def __init__(self, rules: tuple[RateLimitRule, ...]) -> None:
        self._rules = rules
        self._buckets: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, request: Request) -> RateLimitViolation | None:
        if not self._rules:
            return None

        method = request.method.upper()
        path = request.url.path
        client_id = self._extract_client_id(request)

        for rule in self._rules:
            if method not in rule.methods:
                continue
            if not any(path.startswith(prefix) for prefix in rule.path_prefixes):
                continue
            bucket_key = f"{rule.name}:{client_id}"
            allowed, retry_after = self._consume_bucket(
                bucket_key=bucket_key,
                max_requests=rule.max_requests,
                window_seconds=rule.window_seconds,
            )
            if not allowed:
                return RateLimitViolation(
                    rule_name=rule.name,
                    retry_after_seconds=retry_after,
                )
        return None

    def _consume_bucket(
        self,
        *,
        bucket_key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._buckets.setdefault(bucket_key, deque())
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= max_requests:
                retry_after = max(1, math.ceil((bucket[0] + window_seconds) - now))
                return False, retry_after
            bucket.append(now)
            return True, 0

    @staticmethod
    def _extract_client_id(request: Request) -> str:
        return extract_client_ip(request) or "unknown"


def load_rate_limit_rules_from_env() -> tuple[RateLimitRule, ...]:
    enabled = _env_bool("AUTH_RATE_LIMIT_ENABLED", True)
    if not enabled:
        return ()
    return (
        RateLimitRule(
            name="auth_login",
            methods=("POST",),
            path_prefixes=("/v1/auth/login",),
            max_requests=_env_int("AUTH_RATE_LIMIT_LOGIN_MAX", 20),
            window_seconds=_env_int("AUTH_RATE_LIMIT_LOGIN_WINDOW_SECONDS", 60),
        ),
        RateLimitRule(
            name="auth_refresh",
            methods=("POST",),
            path_prefixes=("/v1/auth/refresh",),
            max_requests=_env_int("AUTH_RATE_LIMIT_REFRESH_MAX", 40),
            window_seconds=_env_int("AUTH_RATE_LIMIT_REFRESH_WINDOW_SECONDS", 60),
        ),
        RateLimitRule(
            name="auth_register",
            methods=("POST",),
            path_prefixes=("/v1/auth/register",),
            max_requests=_env_int("AUTH_RATE_LIMIT_REGISTER_MAX", 20),
            window_seconds=_env_int("AUTH_RATE_LIMIT_REGISTER_WINDOW_SECONDS", 60),
        ),
        RateLimitRule(
            name="auth_admin",
            methods=("GET", "POST", "PUT", "PATCH", "DELETE"),
            path_prefixes=("/v1/admin",),
            max_requests=_env_int("AUTH_RATE_LIMIT_ADMIN_MAX", 120),
            window_seconds=_env_int("AUTH_RATE_LIMIT_ADMIN_WINDOW_SECONDS", 60),
        ),
    )


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}
