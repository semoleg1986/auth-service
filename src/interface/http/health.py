from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readyz() -> dict[str, str]:
    return {"status": "ready"}
