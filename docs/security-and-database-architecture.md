# Zemazap: база данных и защита

Дата обновления: 2026-08-09.

## Текущее архитектурное решение

Проект перешел на Django как единственный backend.

- Next.js отвечает за публичный frontend.
- Django отвечает за каталог, заявки, импорт прайсов, уведомления и админку.
- `/admin` на стороне Next.js только перенаправляет пользователей в Django admin.
- `/api/catalog`, `/api/catalog/[slug]` и `/api/requests` на стороне Next.js являются тонкими proxy-роутами к Django API.

## База данных

Локальная разработка сейчас использует Django SQLite:

`backend/data/zemazap_django.sqlite3`

Production-цель остается прежней:

`PostgreSQL`

PostgreSQL нужен для нормального production-контура: индексы, транзакции, резервные копии, миграции, масштабирование, отчеты и будущие интеграции.

## Админка

Административная зона должна жить только в Django:

- пользователи и права доступа через Django admin;
- каталог через модели `catalog`;
- заявки через модели `leads`;
- импорт прайсов через `imports`;
- настройки уведомлений через `notifications`.

Старая TypeScript-админка и локальный TS backend удалены из активной архитектуры.

## API

Актуальные Django endpoints:

- `GET /api/catalog/` - каталог, фильтры и поиск;
- `GET /api/catalog/<slug>/` - карточка товара;
- `POST /api/requests/` - заявка из формы или корзины;
- `POST /api/imports/prices/` - импорт CSV/XLSX, доступен только admin-пользователям Django.

Next.js proxy endpoints оставлены временно, чтобы frontend мог обращаться к своему origin и не зависеть от CORS/CSRF-настройки в браузере.

## Минимальные правила защиты

- секреты хранятся только в `.env`, не в git;
- Django admin доступна только авторизованным пользователям;
- публичные формы проходят серверную валидацию в Django;
- заявки ограничиваются throttling-правилами Django REST Framework;
- production и development окружения разделяются;
- база данных и медиа должны иметь регулярные backup-и с проверкой восстановления.

## Что еще нужно перед production

1. Перейти с локальной Django SQLite на PostgreSQL.
2. Настроить реальные домены, HTTPS и production-переменные окружения.
3. Настроить backup-и PostgreSQL и media/storage.
4. Проверить права Django admin-групп для менеджеров.
5. Решить, остаются ли Next proxy routes или frontend будет ходить в Django API напрямую.
