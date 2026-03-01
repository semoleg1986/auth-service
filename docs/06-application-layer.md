# Слой Application

## Назначение

Оркестрация use cases auth-контекста.
Application Layer связывает домен, политики и инфраструктуру (хранилище, криптография, время).

## Ответственность

1. Проверка политик перед любым действием.
2. Управление транзакциями и сессиями.
3. Интеграция с Crypto/JWT инфраструктурой.
4. Возврат DTO для внешнего интерфейса.

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
5. Сохранить refresh session.

### 3. Refresh

**Input**: refresh token

**Шаги**:
1. Проверить сессию и срок действия.
2. Проверить, что refresh не отозван.
3. Выдать новый access токен.

### 4. Logout

**Input**: refresh token

**Шаги**:
1. Найти refresh session.
2. Отозвать сессию.

### 5. Assign Role

**Input**: admin actor, user_id, role

**Шаги**:
1. Проверить policy (admin).
2. Присвоить роль.
3. Сохранить агрегат.

## Структура (предложение)

```shell
application/
├── commands/
├── handlers/
├── dtos/
├── policies/
└── unit_of_work.py
```

## Примечания

- JWT и криптография находятся в Infrastructure.
- Application Layer не зависит от HTTP.
