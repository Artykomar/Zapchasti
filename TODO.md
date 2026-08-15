# TODO: подготовка Zemazap к deployment

Дата обновления: 2026-08-15.

Этот список заменяет старый TODO по проблемам текущего билда. Закрытые задачи по Django-переезду, фильтрам каталога, корзине, URL по артикулу, удалению старого TypeScript backend и переходу админки в Django убраны. Ниже остались только задачи, которые еще нужны перед реальным запуском сайта.

Приоритеты:

- `P0` - блокер перед deployment.
- `P1` - обязательно закрыть до первого production-запуска.
- `P2` - важно для стабильности, поддержки и роста после запуска.
- `P3` - улучшения и организационные задачи без немедленного риска.

## P0

- [x] `P0` Зафиксировать production-ветку и правило релизов.
  Сейчас активная рабочая ветка с Django-only backend находится в `main`. Нужно убедиться, что GitHub, PyCharm, CI/CD и будущий хостинг деплоят именно эту ветку, а старые инструкции про `master` больше не используются.
  2026-08-15: `origin/HEAD` указывает на `main`, удаленная `origin/master` удалена, локальная работа переведена на `main`, checkpoint и foundation-коммиты отправляются в `origin/main`.

- [ ] `P0` Выбрать production-инфраструктуру.
  Нужно решить, где будут жить Django, Next.js, PostgreSQL, reverse proxy, static/media files и backups. Минимальная схема: домен -> HTTPS/reverse proxy -> Next.js frontend + Django backend -> PostgreSQL.

- [~] `P0` Настроить production env-переменные.
  Для Django: `DJANGO_DEBUG=false`, сильный `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `ZEMAZAP_SITE_URL`, SMTP/Telegram при необходимости. Для Next.js: `ZEMAZAP_DJANGO_API_URL` должен указывать на доступный Django backend.
  2026-08-15: расширены `.env.example` и `backend/.env.example` для публичных контактов, реквизитов, версий документов, feature flags, Альфа-Банка, фискализации, MAX, Object Storage и analytics. Осталось заполнить реальные production-секреты и URL.

- [ ] `P0` Перевести production-базу на PostgreSQL.
  Локально Django может оставаться на SQLite, но production должен использовать PostgreSQL. Нужно создать базу, применить миграции, загрузить стартовые данные, проверить backup и тестовое восстановление.

- [ ] `P0` Создать реальные Django admin-аккаунты и права.
  Нужно создать superuser, staff-пользователей менеджеров, группы прав и проверить, что `/admin` в Next.js ведет в Django admin, а старой TypeScript-админки больше нет в production-пути.

- [ ] `P0` Заменить демо-данные на реальные данные компании.
  Нужны реальные телефон, email, мессенджеры, регион работы, график, юридический текст, политика обработки персональных данных, условия доставки и первые реальные товары/прайсы.

- [ ] `P0` Провести staging smoke test перед релизом.
  Проверить главную, каталог, фильтры, сброс фильтров, карточку товара по артикулу, добавление/удаление из корзины, отправку заявки, Django admin, импорт прайса и отображение ошибок формы.

## P1

- [ ] `P1` Настроить CI/CD.
  Минимальный pipeline должен выполнять TypeScript typecheck, `next build`, `python backend/manage.py check`, Django tests и проверку миграций перед деплоем.

- [ ] `P1` Настроить static/media files.
  Нужно решить, где хранятся product images и Django static files: локально на сервере, в object storage или через CDN. Для Django production нужен `collectstatic`.

- [~] `P1` Усилить production security.
  Проверить HTTPS, secure cookies, HSTS, trusted proxy headers, CORS/CSRF, доступ к Django admin, хранение секретов, ротацию секретов и отсутствие `.env`/баз данных в git.
  2026-08-15: добавлены launch configuration checks, безопасные feature flags, Next security headers без HSTS для локального режима и env-contract для секретов. Осталось проверить HTTPS/HSTS/proxy headers на реальном staging.

- [~] `P1` Подключить реальные уведомления менеджеру.
  Нужно заполнить SMTP или Telegram env-переменные, отправить тестовую заявку и убедиться, что менеджер получает понятное уведомление со ссылкой на Django admin.
  2026-08-15: Telegram по умолчанию получает PII-safe текст без имени, телефона и текста заявки; подробные уведомления остаются для email. Осталось заполнить реальные SMTP/MAX/Telegram данные и протестировать канал.

- [ ] `P1` Настроить monitoring и logs.
  Нужны health checks, логирование ошибок Django/Next.js, alerts при падении API, ошибках отправки уведомлений и проблемах с базой.

- [ ] `P1` Проверить антиспам на production-настройках.
  Сейчас есть DRF throttle и honeypot. Нужно подобрать реальные лимиты и решить, нужен ли Turnstile/CAPTCHA после первых тестов.

- [ ] `P1` Прогнать импорт реальных прайсов.
  Проверить CSV/XLSX поставщиков: кодировки, названия колонок, дубли, цены с пробелами/валютой, большие файлы, откат после плохого импорта и качество созданных карточек.

## P2

- [ ] `P2` Добавить browser e2e smoke tests.
  Нужны автотесты на каталог, фильтры, карточку товара, корзину, форму заявки и redirect `/admin` в Django.

- [ ] `P2` Проверить производительность на большом каталоге.
  После реального импорта измерить скорость `/api/catalog/`, карточек товара, фильтров и Django admin. При необходимости добавить пагинацию, индексы и лимиты выдачи.

- [~] `P2` Доработать SEO.
  Нужны production title/description, sitemap, robots.txt, canonical URLs, Open Graph и базовая schema-разметка для карточек товаров.
  2026-08-15: добавлены env-based metadata, canonical base URL, Open Graph, `robots.txt` и `sitemap.xml`; staging/dev закрыты от индексации по умолчанию. Остались schema-разметка и финальные production тексты.

- [~] `P2` Улучшить UX форм.
  Проверить понятные ошибки валидации, форматирование телефона, подсказки для артикула/номера детали и поведение при недоступном Django API.
  2026-08-15: чекбоксы форм ведут на отдельные страницы политики и согласия, backend сохраняет версии согласия, время, источник, IP и user-agent. Остались финальные тексты ошибок и production smoke.

- [ ] `P2` Разобраться с остатками демо-данных во frontend.
  `src/data/catalog.ts` сейчас еще хранит типы, helpers и демо-массивы. Нужно оставить только типы/helpers или перенести оставшиеся статичные данные в Django/отдельный content-source.

- [ ] `P2` Решить судьбу избранного.
  Сейчас wishlist остается клиентской функцией на localStorage. Нужно решить, достаточно ли этого для MVP или нужно хранить избранное на backend.

## P3

- [ ] `P3` Решить, оставляем ли Next proxy routes.
  Сейчас `/api/catalog`, `/api/catalog/[slug]` и `/api/requests` в Next.js являются тонким proxy к Django. Перед production можно оставить так или перевести frontend на прямой Django API с корректными CORS/CSRF.

- [ ] `P3` Обновить developer docs после выбора хостинга.
  После решения по deployment нужно обновить README, backend README и инструкции запуска под фактический сервер/CI.

- [ ] `P3` Удалить старые локальные окружения вручную.
  Если в рабочей папке остался старый `venv`, проверить в PyCharm, что используется `.venv\Scripts\python.exe`, и удалить старый `venv`, если он точно не нужен.

- [ ] `P3` Подготовить launch checklist для ручной приемки.
  Сделать короткий чеклист для CEO/менеджера: открыть страницы, найти товар, оформить заявку, проверить уведомление, проверить заявку в Django admin.

## Проверки, которые нужно запускать перед каждым релизом

- [ ] `python backend/manage.py check`
- [ ] `python backend/manage.py test apps.catalog apps.leads apps.imports apps.notifications`
- [ ] `node node_modules/typescript/bin/tsc --noEmit`
- [ ] `node node_modules/next/dist/bin/next build`
- [ ] Ручной smoke test на staging
