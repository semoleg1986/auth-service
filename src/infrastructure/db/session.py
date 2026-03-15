from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def get_database_url() -> str | None:
    """
    Вернуть URL базы данных из окружения.

    :return: URL подключения к БД или None.
    :rtype: str | None
    """
    return os.getenv("DATABASE_URL")


def _normalize_database_url(url: str) -> str:
    """
    Нормализовать URL для sync SQLAlchemy engine.

    :param url: Исходный URL.
    :type url: str
    :return: Нормализованный URL.
    :rtype: str
    """
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    return url


def is_database_enabled() -> bool:
    """
    Проверить, включено ли подключение к БД.

    :return: True, если DATABASE_URL задан.
    :rtype: bool
    """
    return bool(get_database_url())


@lru_cache(maxsize=1)
def get_engine() -> Engine | None:
    """
    Создать и закэшировать SQLAlchemy Engine.

    :return: Engine или None, если DATABASE_URL не задан.
    :rtype: Engine | None
    """
    raw_url = get_database_url()
    if not raw_url:
        return None
    return create_engine(_normalize_database_url(raw_url), pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session] | None:
    """
    Создать и закэшировать фабрику сессий SQLAlchemy.

    :return: Фабрика сессий или None.
    :rtype: sessionmaker[Session] | None
    """
    engine = get_engine()
    if engine is None:
        return None
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def ensure_schema() -> None:
    """
    Создать таблицы в БД при их отсутствии.
    """
    engine = get_engine()
    if engine is None:
        return
    Base.metadata.create_all(bind=engine)
