# Zemazap backend migration notes

## Branches

- `main` is kept as the pre-migration Next.js backend backup.
- `master` is the Django backend branch.

## Ported to Django

- Domain models for brands, car models, generations, categories, manufacturers,
  suppliers, parts, part numbers, compatibility, specs, price offers, customers,
  customer requests, request items, request events, price imports and
  notification settings.
- Django Admin registration for the operational entities.
- DRF API scaffold compatible with the current frontend catalog/request shapes.
- Demo seed command: `python backend/manage.py seed_demo`.
- CSV/XLSX price import service and staff-only API endpoint.
- Telegram and SMTP notification service called after request creation.
- Local SQLite development database and `DATABASE_URL` PostgreSQL production
  target.
- PyCharm project config with Git mapping and run configuration.

## Still to port or improve

- Full frontend switch from Next route handlers to the Django API.
- Rich Django admin workflows for status changes, comments and import preview.
- Production auth hardening: roles, 2FA, audit log and backups.
- Real supplier feeds, product photos and real contact/legal content.

## Security rule: SQL injection

Use Django ORM query methods and parameterized queries for all database access.
Do not build raw SQL with f-strings, string concatenation, `%` formatting or
`.format()` using user input. If raw SQL becomes unavoidable, pass user values
through Django cursor parameters, keep the query small and add a regression test
for hostile input.
