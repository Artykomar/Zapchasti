# Zemazap

Мультибрендовая витрина автозапчастей: Next.js 16 frontend, Django/DRF backend,
заказы, интеграционный контур Альфа-Банка, фискализация, возвраты и админка.

## Локальный запуск

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt pip-audit==2.10.1
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

Docker для локальной разработки и тестирования не нужен.

## Проверки

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend\manage.py check_launch_content
.\.venv\Scripts\python.exe backend\manage.py test apps.core apps.catalog apps.customers apps.leads apps.orders apps.payments apps.fiscal apps.refunds apps.imports apps.notifications
$env:PYTHONUTF8 = "1"
.\.venv\Scripts\python.exe -m pip_audit -r backend\requirements.txt
npm.cmd run typecheck
npm.cmd run build
npm.cmd run e2e
.\.venv\Scripts\python.exe scripts\smoke-check.py http://127.0.0.1:3000
```

`npm.cmd run e2e` сам поднимает Next.js на `3100` и Django на `8100`, создает
отдельную `backend/data/zemazap_e2e.sqlite3`, загружает demo seed и удаляет данные
следующего прогона перед стартом. Текущая локальная база не используется. Первый
раз Chromium устанавливается командой `npm.cmd run e2e:install`. Тот же набор
сценариев является отдельным обязательным job в GitHub CI.

## Локальная проверка PostgreSQL без Docker

Проект проверен на нативном PostgreSQL 18.6/UTF-8: миграции, полный backend test-suite,
повторный `bootstrap_roles`, одноразовый scheduler, retention dry-run и
`pg_dump`/restore прошли успешно. Повторяемый сценарий описан в
[инструкции по локальному PostgreSQL](docs/local-postgresql-rehearsal.md).

## Production

- `.env.example` и `backend/.env.example` описывают контракт переменных.
- `compose.production.yml` остается вариантом удаленного production-like rollout:
  Caddy, Next.js, Django, scheduler и PostgreSQL. Для локальной работы он не нужен.
- `compose.yandex.yml` предназначен для Yandex Cloud и готовых registry images.
- CI находится в `.github/workflows/ci.yml`, ручной staging/production rollout —
  в `.github/workflows/deploy.yml`.
- Инструкции: [запуск в Yandex Cloud](docs/yandex-cloud-production-runbook.md),
  [Альфа-Банк и фискализация](docs/alfa-bank-and-fiscalization-runbook.md),
  [launch checklist](docs/launch-readiness-checklist.md).

Реальные платежи и чеки выключены до заполнения реквизитов продавца, утверждения
юридических текстов, создания production-инфраструктуры, выдачи секретов
Альфа-Банка и успешной приемки кассы/ОФД. Чек Alfa остается в состоянии
`pending_confirmation`, пока реальный провайдер/ОФД не подтвердит его. Номер
карты, CVV и срок действия карты приложение не принимает и не хранит.
