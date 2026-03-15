# Слой Application

## Назначение

Application Layer оркестрирует use-cases `auth-service`: связывает доменные агрегаты, policy-checks, порты инфраструктуры и транзакции.

## Структура Application

```shell
src/application/
├── access/
│   ├── commands/assign_role.py
│   ├── handlers/{assign_role,list_role_assignments}.py
│   └── queries/list_role_assignments.py
├── identity/
│   ├── commands/{register,block_user,unblock_user}.py
│   └── handlers/{register,block_user,unblock_user}.py
├── session/
│   ├── commands/{login,refresh,logout,revoke_session}.py
│   ├── handlers/{login,refresh,logout,revoke_session,list_sessions}.py
│   └── queries/list_sessions.py
├── dtos/{auth,geo}.py
├── ports/{crypto,tokens,time,jwks,geo_lookup}.py
├── services/geo_enricher.py
├── actor_context.py
└── unit_of_work.py
```

## Команды и запросы

### Write-side (commands)

- `identity`: `Register`, `BlockUser`, `UnblockUser`.
- `session`: `Login`, `Refresh`, `Logout`, `RevokeSession`.
- `access`: `AssignRole`.

### Read-side (queries)

- `session`: `ListSessions`.
- `access`: `ListRoleAssignments`.

## Порты и транзакции

- `UnitOfWork`:
  - `user_repo: UserAccountRepository`
  - `session_repo: SessionRepository`
  - `commit()`, `rollback()`.
- Порты инфраструктуры:
  - `PasswordHasher`, `TokenService`, `TimeProvider`, `JwksProvider`, `GeoLookupPort`.

## Ключевые обязанности

1. Преобразование `ActorContext -> domain.Actor` и запуск policy-checks (`AccessPolicy`).
2. Оркестрация сценариев логина/refresh с ротацией refresh-сессий.
3. Обновление security-состояния аккаунта (`failed_attempts`, `locked_until`, last login).
4. Выдача DTO для interface-слоя без зависимости от HTTP/transport.
5. Обогащение геоданных сессии через `services/geo_enricher.py` и `GeoLookupPort`.

## Границы слоя

- Application не знает о FastAPI/Nuxt/headers/cookies/status codes.
- HTTP-мэппинг и валидация payload выполняются в interface-слое.
- Доменная логика остается в `src/domain/*`; application только оркестрирует.
