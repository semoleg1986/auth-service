# auth-service

Сервис аутентификации и авторизации.

## Что реализовано
- регистрация: `POST /v1/auth/register`
- логин: `POST /v1/auth/login`
- refresh: `POST /v1/auth/refresh`
- logout (revoke refresh): `POST /v1/auth/logout`
- JWKS: `GET /.well-known/jwks.json`
- admin операции:
  - `POST /v1/admin/users/{user_id}/roles`
  - `POST /v1/admin/users/{user_id}/block`
  - `POST /v1/admin/users/{user_id}/unblock`

## Быстрый запуск
```bash
cd /Users/olegsemenov/Programming/monitoring/auth-service
make install
make run
```

## Обязательные env
- `JWT_ISSUER`
- `JWT_AUDIENCE`
- `JWT_PRIVATE_KEY_PEM`
- `JWT_PUBLIC_KEY_PEM`

Важно: PEM-ключи в `.env` должны быть в одну строку с `\n`.

## Контракт
- OpenAPI: `/Users/olegsemenov/Programming/monitoring/auth-service/openapi.yaml`
- Проверка контракта:
```bash
make openapi-check
make contract-provider
```

## Статус
Подтвержден в e2e smoke (`5/5`):
- login/refresh/logout lifecycle
- доступ админа и user флоу через web-клиенты
