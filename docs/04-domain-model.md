# Auth Service — Domain Model

## Purpose

Фиксирует агрегаты и сущности auth‑контекста.

---

## Aggregates

### 1. UserAccount (Aggregate Root)

- **Attributes**:
  - `user_id: UUID`
  - `email: str | None`
  - `phone: str | None`
  - `status: active | blocked | deleted`
  - `roles: set[Role]`
- **Behavior**:
  - `register(credentials)`
  - `assign_role(role)`
  - `block()` / `unblock()`
  - `change_email()` / `change_phone()`
- **Invariants**:
  - хотя бы один идентификатор (email или phone)
  - уникальность email/phone
  - blocked не может логиниться

---

### 2. Credential (Entity)

- **Types**:
  - PasswordCredential
  - OAuthCredential (опционально)
- **Attributes**:
  - `credential_id: UUID`
  - `type: password | oauth`
  - `hash: str` (для password)
- **Invariants**:
  - хранится только хеш
  - нельзя иметь два одинаковых credential одного типа

---

### 3. Session / RefreshToken (Entity)

- **Attributes**:
  - `token_id: UUID`
  - `user_id: UUID`
  - `expires_at: datetime`
  - `revoked_at: datetime | None`
- **Behavior**:
  - `revoke()`
  - `is_active(now)`

---

### 4. Role (Value Object)

- **Attributes**:
  - `name: str` (например, admin, user)
- **Rules**:
  - присваивается через политики

---

## Repositories (Interfaces)

- **UserAccountRepository**
  - `get_by_id(user_id)`
  - `get_by_email(email)`
  - `get_by_phone(phone)`
  - `save(user_account)`
- **SessionRepository**
  - `get_by_id(token_id)`
  - `save(session)`
  - `revoke(token_id)`

---

## Notes

1. Access token не является сущностью домена.
2. RefreshToken хранится и управляется доменом.
3. Доменные сущности не знают о HTTP, JWT или инфраструктуре.
