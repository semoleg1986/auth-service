# Слой Interface

## Назначение

Interface Layer принимает HTTP-запросы, валидирует transport DTO и маппит ошибки/ответы для клиентов (`admin-web`, `user-web`, `e2e`).

## Структура

```shell
src/interface/http/
├── app.py
├── main.py
├── health.py
├── jwks.py
├── errors.py
├── problem_types.py
├── rate_limit.py
├── request_client.py
├── wiring.py
├── di/providers.py
└── v1/
    ├── auth_router.py
    ├── admin_router.py
    ├── schemas.py
    └── error_responses.py
```

## Что делает слой

- Собирает FastAPI-приложение и роутинг (`app.py`, `main.py`).
- Публикует служебные endpoint'ы: `/healthz`, `/.well-known/jwks.json`.
- Обрабатывает API v1:
  - `auth_router.py` — login/refresh/logout/session API.
  - `admin_router.py` — admin read/write API.
- Выполняет transport-валидацию (`schemas.py`) и маппинг ошибок (`errors.py`, `error_responses.py`).
- Проставляет инфраструктурные HTTP-политики (rate-limit, request metadata).
- Собирает зависимости через `wiring.py` и `di/providers.py`.

## Границы ответственности

- Interface не содержит бизнес-правил домена.
- Access-policy/инварианты проверяются в domain/application.
- ORM/SQL/crypto-код не размещается в interface; он подключается через application порты и DI.
