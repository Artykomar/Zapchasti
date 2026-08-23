# Локальная проверка PostgreSQL без Docker

Этот сценарий проверяет Zemazap на настоящем PostgreSQL, но не устанавливает
Windows service, не меняет системный `PATH` и не затрагивает обычную SQLite-базу.
Для ежедневной разработки SQLite остается достаточной.

## 1. Подготовить portable PostgreSQL

Скачайте актуальный 64-bit zip archive по ссылке с официальной страницы
[PostgreSQL for Windows](https://www.postgresql.org/download/windows/). На
2026-08-23 проект проверен с PostgreSQL 18.6.

Распакуйте архив и создайте data directory в путях, содержащих только латиницу.
Windows-сборка EDB может некорректно передать кириллический путь в UTF-8 во время
`initdb`. Ниже используются временные пути; они подходят только для локальной
приемки:

```powershell
$pgRoot = "$env:TEMP\zemazap-postgresql-18.6\pgsql"
$pgData = "$env:TEMP\zemazap-postgres-rehearsal-data"

& "$pgRoot\bin\initdb.exe" `
  -D $pgData `
  -U zemazap_admin `
  --encoding=UTF8 `
  --locale=C `
  --auth=trust
```

`trust` допустим здесь только потому, что кластер одноразовый и дальше слушает
только loopback. Для постоянной локальной базы используйте пароль и
`scram-sha-256`.

## 2. Запустить loopback-only сервер и создать базу

```powershell
& "$pgRoot\bin\pg_ctl.exe" `
  -D $pgData `
  -l "$env:TEMP\zemazap-postgres-rehearsal.log" `
  -o '-p 55432 -h 127.0.0.1' `
  start -w

& "$pgRoot\bin\createdb.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin zemazap_rehearsal

$env:DATABASE_URL = 'postgresql://zemazap_admin@127.0.0.1:55432/zemazap_rehearsal'
$env:DATABASE_CONN_MAX_AGE = '0'
```

Не используйте имя production-базы или production credentials в этом сценарии.

## 3. Прогнать приложение и операции

Перед scheduler принудительно отключите внешние каналы, чтобы rehearsal ничего
не отправил:

```powershell
$env:PAYMENTS_ENABLED = 'false'
$env:FISCALIZATION_ENABLED = 'false'
$env:ZEMAZAP_SMTP_HOST = ''
$env:ZEMAZAP_SMTP_USER = ''
$env:ZEMAZAP_SMTP_PASSWORD = ''
$env:ZEMAZAP_TELEGRAM_BOT_TOKEN = ''
$env:ZEMAZAP_TELEGRAM_CHAT_ID = ''
$env:PII_IN_NOTIFICATIONS_ALLOWED = 'false'

.\.venv\Scripts\python.exe backend\manage.py migrate --noinput
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend\manage.py seed_demo
.\.venv\Scripts\python.exe backend\manage.py bootstrap_roles
.\.venv\Scripts\python.exe backend\manage.py bootstrap_roles
.\.venv\Scripts\python.exe backend\manage.py run_operations_scheduler --once
.\.venv\Scripts\python.exe backend\manage.py anonymize_personal_data --dry-run
.\.venv\Scripts\python.exe backend\manage.py test `
  apps.core apps.catalog apps.customers apps.leads apps.orders apps.payments `
  apps.fiscal apps.refunds apps.imports apps.notifications
```

Повторный `bootstrap_roles` проверяет идемпотентность настройки прав. Scheduler
работает по disposable data и с отключенными SMTP/Telegram/payment/fiscal
интеграциями.

## 4. Проверить backup/restore и остановить сервер

```powershell
& "$pgRoot\bin\pg_dump.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin `
  -d zemazap_rehearsal -Fc -f "$env:TEMP\zemazap-rehearsal.dump"

& "$pgRoot\bin\createdb.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin zemazap_restore
& "$pgRoot\bin\pg_restore.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin `
  -d zemazap_restore --exit-on-error "$env:TEMP\zemazap-rehearsal.dump"
& "$pgRoot\bin\psql.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin -d zemazap_restore `
  -c 'select count(*) as parts from catalog_part;'
& "$pgRoot\bin\dropdb.exe" `
  -h 127.0.0.1 -p 55432 -U zemazap_admin zemazap_restore

& "$pgRoot\bin\pg_ctl.exe" -D $pgData stop -m fast -w
```

Удалять `$pgData`, archive и dump можно только после проверки точных абсолютных
путей и остановки сервера. Эти локальные файлы не являются production backup.
