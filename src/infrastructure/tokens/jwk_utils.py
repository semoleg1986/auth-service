from __future__ import annotations

import hashlib
import json
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from jwt.utils import base64url_encode


def _load_public_key(public_key_pem: str):
    return serialization.load_pem_public_key(public_key_pem.encode("utf-8"))


def build_jwk_with_kid(public_key_pem: str) -> dict[str, Any]:
    public_key = _load_public_key(public_key_pem)
    jwk_json = jwt.algorithms.RSAAlgorithm.to_jwk(public_key)
    jwk = json.loads(jwk_json)
    kid = compute_kid(jwk)
    jwk["kid"] = kid
    return jwk


def compute_kid(jwk: dict[str, Any]) -> str:
    # RFC 7638 JWK thumbprint (SHA-256 of canonical JSON)
    thumbprint = json.dumps(
        {k: jwk[k] for k in sorted(jwk) if k != "kid"},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    digest = hashlib.sha256(thumbprint).digest()
    return base64url_encode(digest).decode("utf-8")
