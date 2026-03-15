# Слой Infrastructure

## Назначение

Infrastructure Layer реализует порты application слоя: persistence, crypto/token security, внешние клиенты.

## Структура

```shell
src/infrastructure/
├── db/
│   ├── session.py
│   ├── models.py
│   ├── repositories/
│   │   ├── sqlalchemy_user_account_repository.py
│   │   ├── sqlalchemy_session_repository.py
│   │   ├── in_memory_user_account_repository.py
│   │   └── in_memory_session_repository.py
│   └── uow/
│       ├── sqlalchemy_uow.py
│       └── in_memory_uow.py
├── security/
│   ├── argon2_hasher.py
│   ├── jwt_token_service.py
│   ├── jwks_provider.py
│   ├── jwk_utils.py
│   ├── jwt_settings.py
│   └── in_memory_token_service.py
├── clients/
│   └── geo/
│       ├── ipwhois_lookup.py
│       └── noop_lookup.py
├── observability/
└── messaging/
```

## Что делает слой

- `db/*`: SQLAlchemy-модели, репозитории и UoW для транзакций.
- `security/*`: реализация `PasswordHasher`, `TokenService`, `JwksProvider`.
- `clients/geo/*`: реализация `GeoLookupPort` (боевой и noop варианты).
- `in_memory_*`: тестовые реализации для unit/integration сценариев.

## Границы ответственности

- Infrastructure не оркестрирует use-case сценарии.
- Проверки access/invariants не реализуются здесь; они остаются в domain/application.
- Layer не должен импортировать interface роуты.
