# Zemazap Django backend

Django/DRF — единственный backend и административный контур проекта. Next.js
обращается к нему через `ZEMAZAP_DJANGO_API_URL` (по умолчанию
`http://127.0.0.1:8000`).

## Локальная настройка

Из корня репозитория:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_demo
.\.venv\Scripts\python.exe backend\manage.py bootstrap_roles
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Локально используется SQLite (`backend/data/zemazap_django.sqlite3`), production
подключается к PostgreSQL через `DATABASE_URL`. Media может храниться локально
или в Yandex Object Storage через S3-compatible настройки.

## Основные API

- `GET /api/health/` — проверка приложения и БД.
- `GET /api/catalog/`, `GET /api/catalog/<slug>/` — публичный каталог.
- `POST /api/requests/` — заявки клиентов.
- `GET /api/orders/<token>/` — безопасная публичная карточка заказа.
- `/api/payments/...` — staff payment link, mock/test callbacks и защищенный
  callback Альфа-Банка с server-to-server сверкой.
- `POST /api/imports/prices/` — импорт прайса для staff.

## Эксплуатационные команды

```powershell
.\.venv\Scripts\python.exe backend\manage.py reconcile_pending_payments
.\.venv\Scripts\python.exe backend\manage.py retry_failed_receipts
.\.venv\Scripts\python.exe backend\manage.py retry_notifications
.\.venv\Scripts\python.exe backend\manage.py anonymize_personal_data --dry-run
```

Production требует `DJANGO_DEBUG=false`, сильный `DJANGO_SECRET_KEY`, HTTPS,
реальные hosts/origins, legal settings, PostgreSQL и внешние секреты. Проверка
контракта выполняется через `manage.py check --deploy`.
