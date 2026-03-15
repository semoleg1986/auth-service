from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domain.session.session import Session


def test_session_active_before_expiry() -> None:
    now = datetime.now(timezone.utc)
    session = Session(
        token_id=uuid4(),
        user_id=uuid4(),
        expires_at=now + timedelta(minutes=5),
    )
    assert session.is_active(now=now) is True


def test_session_inactive_after_expiry() -> None:
    now = datetime.now(timezone.utc)
    session = Session(
        token_id=uuid4(),
        user_id=uuid4(),
        expires_at=now - timedelta(seconds=1),
    )
    assert session.is_active(now=now) is False


def test_session_revoked_is_inactive() -> None:
    now = datetime.now(timezone.utc)
    session = Session(
        token_id=uuid4(),
        user_id=uuid4(),
        expires_at=now + timedelta(minutes=5),
    )
    session.revoke(at=now)
    assert session.is_active(now=now) is False
