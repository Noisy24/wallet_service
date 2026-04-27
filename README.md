# Wallet Service

FastAPI-сервис кошельков с SQLite-хранилищем.

## Локальный запуск

```bash
cd /home/aleks/wallet_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --reload-dir app
```

По умолчанию приложение использует SQLite. Путь к базе задается через `DATABASE_URL`:

```text
DATABASE_URL=sqlite:///./wallet_service.db
```

При старте приложение создает SQLite-файл `wallet_service.db`, если его еще нет.

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
