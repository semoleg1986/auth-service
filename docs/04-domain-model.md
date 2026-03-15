# Доменная Модель

## Назначение

Документ фиксирует текущую структуру Domain Layer в `auth-service` после перехода на контекстную организацию пакетов.

## Структура Domain

```shell
src/domain/
├── access/
│   ├── actor.py
│   ├── policies.py
│   └── role.py
├── identity/
│   ├── entity.py
│   ├── repository.py
│   └── value_objects.py
├── session/
│   ├── entity.py
│   └── repository.py
└── errors.py
```

## Контекст `access`

- `Actor` — контекст актора для policy-checks (`user_id`, `roles`, `is_admin` для совместимости).
- `Role` — Value Object с жестким whitelist ролей:
  - `user`, `admin`, `content_manager`, `auditor`, `support`.
- `AccessPolicy` — доменные правила доступа:
  - назначение ролей, блокировка/разблокировка;
  - просмотр ролей/сессий (`self | admin | auditor | support`);
  - проверка возможности логина/refresh.

## Контекст `identity`

### `UserAccount` (Aggregate Root)

- Поля:
  - `user_id`, `email`, `phone`, `org_id`;
  - `status`, `created_at`, `updated_at`, `version`;
  - `last_login_at`, `blocked_at`, `status_reason`;
  - `roles: set[Role]`;
  - `credentials: list[Credential]`.
- Поведение:
  - роли: `assign_role`, `remove_role`;
  - статус: `block`, `unblock`, `mark_login`;
  - credential-поток: `add_credential`, `register_failed_password_attempt`,
    `register_successful_password_login`, `replace_password_hash`.

### `Credential` (Value Object, immutable)

- Хранится в `identity/value_objects.py` как `@dataclass(frozen=True)`.
- Поддерживает типы:
  - `password` (`secret_hash` обязателен);
  - `oauth` (`provider` и `provider_user_id` обязательны).
- Ведет метаданные безопасности:
  - `failed_attempts`, `locked_until`, `last_used_at`, `password_changed_at`.

### `AccountStatus` (VO enum)

- `active | blocked | deleted`.

### `UserAccountRepository` (порт домена)

- `get_by_id`, `get_by_email`, `get_by_phone`, `save`.

## Контекст `session`

### `Session` (Entity)

- Refresh-session:
  - `token_id`, `user_id`, `expires_at`, `revoked_at`, `revoke_reason`;
  - metadata: `ip_address`, `user_agent`, `geo_city`, `geo_region`, `geo_country`, `geo_display`.
- Поведение:
  - `revoke(at, reason)`;
  - `is_active(now)`.

### `SessionRepository` (порт домена)

- `get_by_id`, `save`, `revoke`, `list_by_user`, `revoke_all_by_user`.

## Ключевые инварианты

1. `UserAccount` обязан иметь хотя бы один идентификатор: `email` или `phone`.
2. В аккаунте не может быть двух credential одного типа.
3. Для `Credential(type=password)` обязательный `secret_hash`, для `oauth` — `provider + provider_user_id`.
4. Сессия активна только если не отозвана и не истек срок `expires_at`.
5. Domain Layer не содержит зависимостей на HTTP, JWT transport и SQLAlchemy.
