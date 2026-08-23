# TODO: запуск Zemazap

Дата обновления: 2026-08-23.

Активная release-ветка — `main`. Устаревшая рабочая копия `Zapchasti-master`
удалена. Здесь перечислена только незавершенная работа; реализованные изменения и
проверки фиксируются в `PROJECT_PLAN_LOG.md`.

## P0 — внешние блокеры production

- [ ] **CEO:** заполнить реальные данные владельца: ИП/ООО, название, ИНН, ОГРН/ОГРНИП,
  КПП при необходимости, юридический/фактический адрес, телефон, email, график,
  налоговый режим и НДС.
- [ ] **CEO:** утвердить с юристом политику ПДн, согласие, оферту, доставку, гарантию и
  возвраты; опубликовать 7 записей `LegalDocument`, пройти
  `check_launch_content`. Проверить уведомление РКН.
- [ ] Создать staging/production в Yandex Cloud: DNS/HTTPS, ALB -> Caddy `:8080`,
  Managed PostgreSQL, Object Storage, Lockbox, WAF, Monitoring и backups.
- [ ] Получить и проверить production-реквизиты Альфа-Банка. Провести банковскую
  модерацию сайта, зарегистрировать callback и включить реальные платежи только
  после полного test-контура.
- [ ] Подключить кассу/ОФД и реализовать/подтвердить получение финального статуса
  чека. До этого Alfa-чек остается `pending_confirmation` и не считается пробитым.
- [ ] **CEO:** загрузить реальные товары и прайсы; не запускать `seed_demo` в production.
- [ ] Создать admin-аккаунты, выполнить `bootstrap_roles`, назначить владельца,
  менеджера и бухгалтера по принципу минимальных прав.
- [ ] Пройти ручной staging smoke из `docs/launch-readiness-checklist.md`, включая
  платеж, неуспешный платеж, частичный/полный возврат, чек прихода/возврата,
  уведомления, backup restore и rollback.

## P1 — обязательная операционная приемка

- [ ] Настроить alerts по 5xx, health, scheduler, БД, payment/fiscal failures,
  pending receipts и notification backlog; назначить ответственных.
- [ ] Проверить SMTP/Telegram на staging, PII-safe logging и доставку из очереди.
- [ ] Настроить регулярный `pg_dump`, Object Storage versioning/lifecycle и
  ежемесячное тестовое восстановление.
- [ ] Подобрать production throttle/WAF правила после нагрузочного теста; решить,
  нужен ли Turnstile/CAPTCHA.
- [ ] Проверить импорт крупных реальных CSV/XLSX, откат плохого импорта и
  производительность каталога/admin после загрузки.

## P2 — после первого стабильного запуска

- [x] Добавить browser E2E для каталога, корзины, заявки, `/admin` handoff и
  payment-return сценария.
- [x] Добавить Product schema.org при разрешенной индексации и заполненных
  реквизитах продавца.
- [ ] **CEO:** утвердить production SEO-тексты.
- [x] Удалить остаточные demo arrays из `src/data/catalog.ts`, оставив типы/helpers.
- [x] Оставить избранное в `localStorage` для MVP без аккаунтов; явно сообщить, что
  список хранится только в текущем браузере.
- [x] Удалить сломанное старое локальное `venv`; PyCharm использует `.venv`.

## Release gate

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py check --deploy
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend\manage.py check_launch_content
.\.venv\Scripts\python.exe backend\manage.py test apps.core apps.catalog apps.customers apps.leads apps.orders apps.payments apps.fiscal apps.refunds apps.imports apps.notifications
$env:PYTHONUTF8 = "1"
.\.venv\Scripts\python.exe -m pip_audit -r backend\requirements.txt
npm.cmd run typecheck
npm.cmd run build
npm.cmd run e2e
npm.cmd audit --omit=dev
.\.venv\Scripts\python.exe scripts\smoke-check.py https://<staging-domain>
```

GitHub deploy workflow выполняется только после reusable CI. Реальный rollout
разрешен, когда все P0 закрыты и commit SHA прошел этот gate.
