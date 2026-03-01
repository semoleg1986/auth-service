# Auth Service — Invariants and Policies

## Purpose

Фиксирует инварианты безопасности и политики доступа.

---

## Business Invariants

1. **Unique Identifier**: email/phone уникальны в системе.
2. **Credential Safety**: пароль хранится только как хеш.
3. **Blocked User**: заблокированный пользователь не может логиниться.
4. **Refresh Validity**: refresh token не может использоваться после истечения.
5. **Refresh Revocation**: отозванный refresh не может быть использован.
6. **Role Assignment**: роль присваивается только через Admin policy.
7. **Optional Organization**: `org_id` может отсутствовать; отсутствие `org_id` означает B2C-сценарий.

---

## Policies

### Admin Policies

| Policy | Description | Actor | Enforcement Point |
|---|---|---|---|
| can_assign_role | Admin может назначать роли | Admin | Application Layer |
| can_block_user | Admin может блокировать | Admin | Application Layer |
| can_unblock_user | Admin может разблокировать | Admin | Application Layer |

### User Policies

| Policy | Description | Actor | Enforcement Point |
|---|---|---|---|
| can_login | User может логиниться | User | Application Layer |
| can_refresh | User может обновлять токен | User | Application Layer |

---

## Enforcement Strategy

1. **Application Layer** вызывает политики до изменения агрегата.
2. **Domain Layer** гарантирует инварианты (ошибка при нарушении).
3. **Infrastructure** не меняет бизнес‑логику.
4. Логика tenant-isolation по `org_id` пока не применяется (поле контрактно зарезервировано).
