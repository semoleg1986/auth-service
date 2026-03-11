# Слой Application

## Назначение

Оркестрация use cases auth-контекста.
Application Layer связывает домен, политики и инфраструктуру (хранилище, криптография, время).

## Ответственность

1. Проверка политик перед любым действием.
2. Управление транзакциями и сессиями.
3. Интеграция с Crypto/JWT инфраструктурой.
4. Возврат DTO для внешнего интерфейса.
5. Преобразование application actor context в domain actor для policy-checks.

## Реализация сценариев

### 1. Register

**Input**: email/phone, password

**Шаги**:
1. Проверить уникальность email/phone.
2. Создать UserAccount и Credential.
3. Сохранить агрегат.

### 2. Login

**Input**: идентификатор + пароль

**Шаги**:
1. Загрузить UserAccount.
2. Проверить статус (not blocked).
3. Проверить credential.
4. Сгенерировать access + refresh токены.
5. Обновить `UserAccount.last_login_at`.
6. Обновить `Credential.last_used_at` для password-credential.
7. Сохранить refresh session.

### 3. Refresh

**Input**: refresh token

**Шаги**:
1. Проверить сессию и срок действия.
2. Проверить, что refresh не отозван.
3. Отозвать старую сессию c `revoke_reason=rotated`.
4. Создать новую сессию и выдать пару `access + refresh`.
5. При повторном использовании уже ротированного refresh выполнить revoke всех активных сессий пользователя.

### 4. Logout

**Input**: refresh token

**Шаги**:
1. Найти refresh session.
2. Отозвать сессию с заполнением `revoke_reason`.

### 5. Assign Role

**Input**: admin actor, user_id, role

**Шаги**:
1. Проверить policy (admin).
2. Присвоить роль.
3. Сохранить агрегат.

### 6. List Roles

**Input**: actor context, user_id

**Шаги**:
1. Загрузить UserAccount.
2. Проверить policy `can_view_roles`.
3. Вернуть список ролей пользователя.

### 7. List Sessions

**Input**: actor context, user_id

**Шаги**:
1. Загрузить UserAccount.
2. Проверить policy `can_view_sessions`.
3. Вернуть список сессий пользователя.

### 8. Revoke Session

**Input**: admin actor context, user_id, token_id

**Шаги**:
1. Проверить policy (admin).
2. Найти session пользователя.
3. Отозвать session с `revoke_reason=admin_revoked`.
4. Сохранить изменения.

## Структура (предложение)

```shell
application/
├── actor_context.py
├── commands/
├── handlers/
├── dtos/
├── ports/
└── unit_of_work.py
```

## Примечания

- JWT и криптография находятся в Infrastructure.
- Application Layer не зависит от HTTP.
