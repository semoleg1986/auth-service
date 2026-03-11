# Доменная Модель

## Назначение

Фиксирует агрегаты и сущности auth-контекста.

## Агрегаты

### 1. UserAccount (Aggregate Root)
- **Атрибуты**:
  - `user_id: UUID`
  - `email: str | None`
  - `phone: str | None`
  - `org_id: str | None` (опциональная принадлежность к организации)
  - `status: active | blocked | deleted`
  - `created_at: datetime`
  - `updated_at: datetime`
  - `version: int`
  - `last_login_at: datetime | None`
  - `blocked_at: datetime | None`
  - `status_reason: str | None`
  - `roles: set[Role]`
- **Поведение**:
  - `assign_role(role)`
  - `remove_role(role)`
  - `block()` / `unblock()`
  - `mark_login()`
- **Инварианты**:
  - хотя бы один идентификатор (email или phone)
  - уникальность email/phone
  - blocked не может логиниться

### 2. Credential (Entity)
- **Типы**:
  - PasswordCredential
  - OAuthCredential (опционально)
- **Атрибуты**:
  - `credential_id: UUID`
  - `type: password | oauth`
  - `secret_hash: str | None` (для password)
  - `provider: str | None` (для oauth)
  - `provider_user_id: str | None` (для oauth)
  - `created_at: datetime`
  - `updated_at: datetime`
  - `last_used_at: datetime | None`
  - `password_changed_at: datetime | None`
  - `failed_attempts: int`
  - `locked_until: datetime | None`
- **Инварианты**:
  - хранится только хеш
  - нельзя иметь два одинаковых credential одного типа

### 3. Session / RefreshToken (Entity)
- **Атрибуты**:
  - `token_id: UUID`
  - `user_id: UUID`
  - `created_at: datetime`
  - `updated_at: datetime`
  - `expires_at: datetime`
  - `revoked_at: datetime | None`
  - `revoke_reason: str | None`
  - `ip_address: str | None`
  - `user_agent: str | None`
- **Поведение**:
  - `revoke()`
  - `is_active(now)`

### 4. Role (Value Object)
- **Атрибуты**:
  - `name: str` (`user | admin | content_manager | auditor | support`)
- **Правила**:
  - присваивается через политики

## Репозитории (интерфейсы)

- **UserAccountRepository**
  - `get_by_id(user_id)`
  - `get_by_email(email)`
  - `get_by_phone(phone)`
  - `save(user_account)`
- **SessionRepository**
  - `get_by_id(token_id)`
  - `save(session)`
  - `revoke(token_id)`
  - `list_by_user(user_id)`
  - `revoke_all_by_user(user_id, reason)`

## Примечания

1. Access token не является сущностью домена.
2. RefreshToken хранится и управляется доменом.
3. Доменные сущности не знают о HTTP, JWT или инфраструктуре.
4. `org_id` сохраняется как опциональный атрибут и может пробрасываться в access token без активации B2B-правил.
