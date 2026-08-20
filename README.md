# Zemazap

Мультибрендовая витрина автозапчастей: Next.js 16 frontend, Django/DRF backend,
заказы, интеграционный контур Альфа-Банка, фискализация, возвраты и админка.

## Локальный запуск

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_demo
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

В отдельном терминале:

```powershell
npm.cmd ci
npm.cmd run dev
```

Витрина будет доступна на `http://127.0.0.1:3000`, Django API и admin — на
`http://127.0.0.1:8000`.

## Проверки

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend\manage.py test
npm.cmd run typecheck
npm.cmd run build
.\.venv\Scripts\python.exe scripts\smoke-check.py http://127.0.0.1:3000
```

## Production

- `.env.example` и `backend/.env.example` описывают контракт переменных.
- `compose.production.yml` поднимает локальный production-like PostgreSQL-контур.
- `compose.yandex.yml` предназначен для Yandex Cloud и готовых registry images.
- CI находится в `.github/workflows/ci.yml`, ручной staging/production rollout —
  в `.github/workflows/deploy.yml`.
- Инструкции: [запуск в Yandex Cloud](docs/yandex-cloud-production-runbook.md),
  [Альфа-Банк и фискализация](docs/alfa-bank-and-fiscalization-runbook.md),
  [launch checklist](docs/launch-readiness-checklist.md).

Реальные платежи и чеки выключены до заполнения реквизитов продавца, домена,
секретов Альфа-Банка, кассы/ОФД и production-инфраструктуры. Номер карты, CVV и
срок действия карты приложение не принимает и не хранит.
