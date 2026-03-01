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
  - `roles: set[Role]`
- **Поведение**:
  - `register(credentials)`
  - `assign_role(role)`
  - `block()` / `unblock()`
  - `change_email()` / `change_phone()`
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
  - `hash: str` (для password)
- **Инварианты**:
  - хранится только хеш
  - нельзя иметь два одинаковых credential одного типа

### 3. Session / RefreshToken (Entity)
- **Атрибуты**:
  - `token_id: UUID`
  - `user_id: UUID`
  - `expires_at: datetime`
  - `revoked_at: datetime | None`
- **Поведение**:
  - `revoke()`
  - `is_active(now)`

### 4. Role (Value Object)
- **Атрибуты**:
  - `name: str` (например, admin, user)
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

## Примечания

1. Access token не является сущностью домена.
2. RefreshToken хранится и управляется доменом.
3. Доменные сущности не знают о HTTP, JWT или инфраструктуре.
4. `org_id` сохраняется как опциональный атрибут и может пробрасываться в access token без активации B2B-правил.
