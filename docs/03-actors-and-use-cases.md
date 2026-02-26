# Auth Service — Actors and Use Cases

## Actors

| Actor | Description | Permissions / Scope |
|---|---|---|
| **User** | Конечный пользователь | Регистрация, логин, refresh, logout |
| **Admin** | Администратор системы | Управление ролями, блокировка пользователей |
| **Client App** | Web/Mobile/Admin client | Передает токены и refresh токены |
| **Domain Services** | Другие сервисы | Проверяют JWT через JWKS |

---

## Use Cases

### User Use Cases

| Use Case | Description | Preconditions | Postconditions |
|---|---|---|---|
| Register | Создать учетную запись | email/phone уникальны | UserAccount создан |
| Login | Получить access/refresh | учетные данные валидны | выданы токены |
| Refresh | Обновить access token | refresh валиден | новый access токен |
| Logout | Отозвать refresh | refresh существует | refresh отозван |

### Admin Use Cases

| Use Case | Description | Preconditions | Postconditions |
|---|---|---|---|
| Assign Role | Назначить роль | admin авторизован | роль обновлена |
| Block User | Заблокировать пользователя | user существует | доступ запрещен |
| Unblock User | Разблокировать пользователя | user заблокирован | доступ разрешен |

### Supporting Use Cases

| Use Case | Description | Actors |
|---|---|---|
| JWKS Publish | Публикация ключей | Auth Service |
| Token Verify | Проверка подписи JWT | Domain Services |

---

## Rules and Constraints

1. Access token живет коротко и не хранится в базе.
2. Refresh token живет дольше и может быть отозван.
3. Заблокированный пользователь не может логиниться.
4. Роли меняются только через Admin use case.
5. Все use cases должны иметь проверку политик и аудит.
