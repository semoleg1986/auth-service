from __future__ import annotations

from uuid import uuid4

import pytest

from src.infrastructure.tokens.in_memory_token_service import InMemoryTokenService


def test_token_service_round_trip() -> None:
    service = InMemoryTokenService()
    token_id = uuid4()
    user_id = uuid4()
    token = service.issue_refresh_token(token_id=token_id, user_id=user_id)
    decoded_token_id, decoded_user_id = service.decode_refresh_token(token)

    assert decoded_token_id == token_id
    assert decoded_user_id == user_id


def test_token_service_invalid_prefix_raises() -> None:
    service = InMemoryTokenService()
    with pytest.raises(ValueError):
        service.decode_refresh_token("bad:token")
