# auth-service

Сервис аутентификации и авторизации.

## Что реализовано
- регистрация: `POST /v1/auth/register`
- логин: `POST /v1/auth/login`
- refresh (rotation): `POST /v1/auth/refresh`
- logout (revoke refresh): `POST /v1/auth/logout`
- JWKS: `GET /.well-known/jwks.json`
- admin операции:
  - `POST /v1/admin/users/{user_id}/roles`
  - `GET /v1/admin/users/{user_id}/roles`
  - `POST /v1/admin/users/{user_id}/block`
  - `POST /v1/admin/users/{user_id}/unblock`
  - `GET /v1/admin/users/{user_id}/sessions`
  - `POST /v1/admin/users/{user_id}/sessions/{token_id}/revoke`

## Безопасность (текущее поведение)
- password hashing: Argon2 (+ fallback verify для legacy hash)
- refresh-token rotation на каждом `refresh`
- reuse-detection: повторный refresh старым токеном отзывает все активные сессии пользователя
- admin endpoints требуют Bearer access token и проверку ролей
- role model: `user`, `admin`, `content_manager`, `auditor`, `support`
- session telemetry: `ip_address`, `user_agent`, `geo_city`, `geo_region`, `geo_country`, `geo_display`

## Быстрый запуск
```bash
cd /Users/olegsemenov/Programming/monitoring/auth-service
make install
make run
```

## Последовательность запуска (локально, с внешним Postgres)
1. Подготовить `.env` (JWT + `DATABASE_URL`).
2. Активировать окружение и установить зависимости:
```bash
cd /Users/olegsemenov/Programming/monitoring/auth-service
source .venv/bin/activate
make install
```
3. Применить миграции:
```bash
make db-upgrade
```
4. Запустить сервис:
```bash
make run
```
5. Проверить health:
```bash
curl http://localhost:8000/healthz
```
6. Smoke auth flow:
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'
```
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"user@example.com","password":"pass"}'
```

## Docker запуск
```bash
cd /Users/olegsemenov/Programming/monitoring/auth-service
make docker-up
```

Перед запуском Docker обязательно задай `DATABASE_URL` (в `.env` или через export),
так как Postgres вынесен во внешний сервис:

```bash
export DATABASE_URL=postgresql+asyncpg://auth_user:asawakan@<POSTGRES_HOST>:<POSTGRES_PORT>/auth_db
```

По умолчанию контейнер применяет миграции автоматически при старте (`alembic upgrade head`).
Это поведение управляется env-переменными:
- `AUTO_MIGRATE_ON_START=true`
- `MIGRATION_MAX_RETRIES=20`
- `MIGRATION_RETRY_DELAY=2`

Опциональный geo lookup (если нет `X-Geo-*` заголовков):
- `AUTH_GEO_LOOKUP_ENABLED=false`
- `AUTH_GEO_LOOKUP_URL_TEMPLATE=https://ipwho.is/{ip}`
- `AUTH_GEO_LOOKUP_TIMEOUT_SECONDS=2`
- `AUTH_GEO_LOOKUP_CACHE_TTL_SECONDS=900`

Остановка:
```bash
make docker-down
```

Логи:
```bash
make docker-logs
```

Последовательность в Docker:
1. Указать `DATABASE_URL` на внешний Postgres
2. Собрать и запустить контейнеры: `make docker-up`
3. Проверить логи миграции/старта: `make docker-logs`
4. Проверить health: `curl http://localhost:8000/healthz`

## Обязательные env
- `JWT_ISSUER`
- `JWT_AUDIENCE`
- `JWT_PRIVATE_KEY_PEM`
- `JWT_PUBLIC_KEY_PEM`

Важно: PEM-ключи в `.env` должны быть в одну строку с `\n`.

## Postgres (опционально)
По умолчанию сервис работает с in-memory репозиториями.
Чтобы включить PostgreSQL persistence, добавь `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://auth_user:asawakan@127.0.0.1:55432/auth_db
```

Текущая реализация автоматически нормализует
`postgresql+asyncpg://` в `postgresql+psycopg://` для sync SQLAlchemy.

### Миграции Alembic
В сервис добавлен каталог миграций:
- `/Users/olegsemenov/Programming/monitoring/auth-service/alembic`
- `/Users/olegsemenov/Programming/monitoring/auth-service/alembic/versions`

Команды:
```bash
make db-upgrade
make db-downgrade
make db-revision MSG="add something"
```

Важно: для `make run` (без Docker) при включенном `DATABASE_URL` сначала выполни `make db-upgrade`.

## Контракт
- OpenAPI: `/Users/olegsemenov/Programming/monitoring/auth-service/openapi.yaml`
- Проверка контракта:
```bash
make openapi-check
make contract-provider
```

## Статус
Подтвержден в e2e smoke (`6/6`):
- login/refresh/logout lifecycle
- доступ админа и user флоу через web-клиенты
