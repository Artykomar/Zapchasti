# Yandex Cloud production runbook

Дата актуализации: 2026-08-20.

## Целевая схема

```text
DNS -> Certificate Manager -> Application Load Balancer
    -> Smart Web Security/WAF -> VM с Docker Compose
        -> Next.js frontend
        -> Django/Gunicorn
        -> Managed PostgreSQL (закрытая подсеть)
        -> Object Storage (фото и документы)
        -> Lockbox (секреты)
```

База PostgreSQL не получает публичный IP. Порт Django не публикуется наружу. На VM открыт только вход от балансировщика; SSH ограничен административным IP или заменен управляемым доступом.

## Последовательность создания

1. Создать отдельные каталоги/окружения `zemazap-staging` и `zemazap-production`.
2. Создать VPC с edge- и backend-подсетями, security groups по принципу минимальных прав.
3. Создать Managed Service for PostgreSQL, отдельную БД и пользователя. Пароль хранить в Lockbox. Включить автоматические бэкапы и окно обслуживания.
4. Создать приватный Object Storage bucket. Сервисному аккаунту приложения выдать только доступ к нужному bucket.
5. Создать Container Registry и включить сканирование образов.
6. Создать VM/группу VM и привязать отдельный service account с минимальной ролью `container-registry.images.puller` на нужный registry. Установить Docker, Docker Compose и Yandex Cloud CLI; настроить для пользователя деплоя `yc container registry configure-docker` и проверить `docker pull` без `sudo`. Затем использовать `compose.yandex.yml`; `DATABASE_URL` должен указывать на Managed PostgreSQL.
7. Создать Application Load Balancer, HTTPS-сертификат и DNS-записи. После проверки включить HSTS.
8. Подключить Smart Web Security/WAF, rate limiting и журналирование событий безопасности.
9. Настроить Monitoring: доступность `/api/health`, 5xx, задержка, CPU/RAM/disk, соединения PostgreSQL, ошибки платежей и фискализации.
10. Настроить GitHub OIDC federation. Не использовать долгоживущий JSON-ключ сервисного аккаунта в GitHub Secrets.

В workflow используются два разных доступа: federated service account GitHub должен
уметь публиковать образы и подключаться к VM, а service account самой VM — только
скачивать образы. До первого rollout команда `docker compose pull` на VM обязана
пройти вручную; иначе автоматический deploy остановится до перезапуска контейнеров.

Официальные опорные материалы:

- Managed PostgreSQL: <https://yandex.cloud/ru/docs/managed-postgresql/>
- Object Storage: <https://yandex.cloud/ru/docs/storage/>
- Lockbox: <https://yandex.cloud/ru/docs/lockbox/>
- GitHub OIDC/Workload Identity Federation: <https://yandex.cloud/ru/docs/tutorials/security/wlif-github-integration>
- Аутентификация Container Registry: <https://yandex.cloud/en/docs/container-registry/operations/authentication>

## Lockbox contract

Секреты production:

- `DJANGO_SECRET_KEY`, `DATABASE_URL`;
- `ALFA_BANK_USERNAME` + `ALFA_BANK_PASSWORD` либо `ALFA_BANK_TOKEN`;
- `ALFA_BANK_CALLBACK_TOKEN`;
- ключи Object Storage;
- SMTP credentials;
- Telegram token только если канал разрешен юридически;
- будущие API-ключи кассы/ОФД, MAX и мониторинга.

Не являются секретами: бренд, публичный домен, телефон, email, адрес, ИНН/ОГРН, версии юридических документов, feature flags.

## Первый деплой

1. Заполнить реальные публичные данные и секреты в staging.
2. Собрать оба образа из одного commit SHA и пометить тегом SHA.
3. Выполнить миграции на пустой staging PostgreSQL.
4. Запустить `seed_demo` только в staging; production наполнять проверенным импортом.
5. Выполнить `check --deploy`, smoke-check и тестовый платежный цикл.
6. Создать ручной backup перед production-миграцией.
7. Развернуть тот же SHA в production, затем выполнить smoke-check.

## Backup и восстановление

- PostgreSQL: автоматические snapshots + ежедневный логический `pg_dump` в отдельный приватный bucket с retention.
- Object Storage: versioning и lifecycle; критичные документы не удалять без подтвержденной копии.
- Ежемесячно выполнять тестовое восстановление в изолированное окружение.
- Перед миграцией сохранять backup и фиксировать commit SHA образов.

Порядок восстановления: остановить запись -> развернуть чистую БД -> восстановить backup -> выполнить совместимые миграции -> проверить `/api/health` и ключевые сценарии -> открыть трафик.

## Rollback

1. Убрать новый экземпляр из балансировщика.
2. Вернуть предыдущие образы по commit SHA.
3. Если миграция обратно совместима, оставить БД и проверить сервис.
4. Если миграция несовместима, остановить запись и восстановить pre-deploy backup. Не выполнять обратную миграцию вслепую.
5. Выполнить smoke-check и только затем вернуть трафик.
