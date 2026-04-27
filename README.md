# Wallet Service

FastAPI-сервис кошельков с SQLite-хранилищем.

## Текущее состояние

Проект реализует базовый wallet API:

- создание кошелька;
- получение одного кошелька и списка кошельков;
- пополнение баланса;
- списание средств;
- историю транзакций;
- статусы кошелька: `active`, `blocked`, `closed`;
- запрет `deposit` и `withdraw` для неактивных кошельков;
- пагинацию и сортировку истории транзакций.

Техническая база:

- FastAPI;
- SQLAlchemy;
- SQLite для локального запуска;
- Alembic для миграций;
- pytest для API-тестов;
- конфигурация базы через `DATABASE_URL`;
- git/GitHub как основной журнал изменений.

Ключевые правила:

- денежные значения принимаются только с точностью до двух знаков после запятой;
- списание баланса выполняется атомарным SQL `UPDATE` с условием `balance >= amount`;
- схема базы изменяется через Alembic, а не через создание таблиц в `lifespan`;
- локальные файлы окружения, база, кеши и Postman-папки не попадают в git.

## Локальный запуск

```bash
cd /home/aleks/wallet_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --reload-dir app
```

По умолчанию приложение использует SQLite. Путь к базе задается через `DATABASE_URL`:

```text
DATABASE_URL=sqlite:///./wallet_service.db
```

При старте приложение создает SQLite-файл `wallet_service.db`, если его еще нет.

Схема базы управляется миграциями Alembic. После изменения моделей применяй миграции:

```bash
alembic upgrade head
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ping
```

Основной ручной сценарий:

1. Открой Swagger UI.
2. Выполни `POST /wallets`.
3. Выполни `GET /wallets` и скопируй `id`.
4. Используй этот `id` в `deposit`, `withdraw` и `transactions`.

История транзакций поддерживает параметры:

```text
GET /wallets/{wallet_id}/transactions?limit=50&offset=0&order=asc
```

Кошелек имеет статус:

```text
active  - операции разрешены
blocked - deposit и withdraw запрещены
closed  - deposit и withdraw запрещены
```

Изменение статуса:

```text
PATCH /wallets/{wallet_id}/status
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Тесты

```bash
cd /home/aleks/wallet_service
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## План разработки

Ближайшие этапы:

1. Добавить пользователей и связь `user -> wallets`.
2. Добавить авторизацию через JWT.
3. Ограничить доступ к кошелькам владельцем.
4. Добавить Dockerfile и docker-compose.
5. Добавить GitHub Actions для запуска тестов при push.
6. Добавить более строгие бизнес-правила для статусов, например запрет возвращать `closed` кошелек в `active`.
7. Добавить фильтры истории транзакций по типу операции и диапазону дат.
8. Подготовить Postman collection или HTTP-файл с ручными сценариями проверки.
