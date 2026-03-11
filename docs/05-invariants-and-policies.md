# Инварианты И Политики

## Назначение

Фиксирует инварианты безопасности и политики доступа.

## Бизнес-инварианты

1. **Unique Identifier**: email/phone уникальны в системе.
2. **Credential Safety**: пароль хранится только как хеш.
3. **Blocked User**: заблокированный пользователь не может логиниться.
4. **Refresh Validity**: refresh token не может использоваться после истечения.
5. **Refresh Revocation**: отозванный refresh не может быть использован.
6. **Refresh Rotation**: при refresh старая session помечается `rotated`, создается новая session и новый refresh token.
7. **Refresh Reuse Detection**: повторное использование уже ротированного refresh токена ведет к revoke всех активных сессий пользователя.
8. **Role Assignment**: роль присваивается только через Admin policy и только из канонического списка ролей.
9. **Optional Organization**: `org_id` может отсутствовать; отсутствие `org_id` означает B2C-сценарий.
10. **Audit Metadata**: успешный логин обновляет `last_login_at` аккаунта и `last_used_at` password-credential.
11. **Session Revoke Trace**: отзыв сессии фиксирует `revoke_reason` и `updated_at`.

## Политики

### Админские политики

| Policy | Описание | Актор | Точка применения |
|---|---|---|---|
| can_assign_role | Admin может назначать роли | Admin | Application Layer |
| can_block_user | Admin может блокировать | Admin | Application Layer |
| can_unblock_user | Admin может разблокировать | Admin | Application Layer |
| can_view_roles | Просмотр ролей пользователя | Self/Admin/Auditor/Support | Application Layer |
| can_view_sessions | Просмотр сессий пользователя | Self/Admin/Auditor/Support | Application Layer |

### Пользовательские политики

| Policy | Описание | Актор | Точка применения |
|---|---|---|---|
| can_login | User может логиниться | User | Application Layer |
| can_refresh | User может обновлять токен | User | Application Layer |

## Стратегия контроля

1. **Application Layer** вызывает политики до изменения агрегата.
2. **Domain Layer** гарантирует инварианты (ошибка при нарушении).
3. **Infrastructure** не меняет бизнес-логику.
4. Tenant-isolation по `org_id` пока не применяется (поле контрактно зарезервировано).
