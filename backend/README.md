# Zemazap Django backend

This folder is the Django migration target for the Zemazap backend. The old
Django migration branch has become the active project state: Next.js is now the
public frontend and Django is the only backend/admin surface.

## Local setup

```powershell
cd C:\Users\Arsik\Documents\ChatGPT\Сайт\Zapchasti
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_demo
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

The Next.js frontend proxies public `/api/catalog`, `/api/catalog/<slug>` and
`/api/requests` calls to this Django server through `ZEMAZAP_DJANGO_API_URL`
(default `http://127.0.0.1:8000`).

## Current API scaffold

- `GET /api/health/`
- `GET /api/catalog/`
- `GET /api/catalog/<slug>/`
- `POST /api/requests/`
- `POST /api/imports/prices/` for authenticated staff users

The public catalog and request endpoints also support the no-trailing-slash
forms used by the current frontend: `/api/catalog`, `/api/catalog/<slug>` and
`/api/requests`.

## Database plan

Local development uses SQLite by default:

`backend/data/zemazap_django.sqlite3`

Production should use PostgreSQL via `DATABASE_URL`.

For production, set `DJANGO_DEBUG=false`, a strong `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS` and
`DJANGO_CSRF_TRUSTED_ORIGINS`. Secure cookies, HTTPS redirect and HSTS are
enabled by default outside development, and DRF Browsable API is disabled.

## PyCharm

Open the repository root `C:\Users\Arsik\Documents\ChatGPT\Сайт\Zapchasti` in PyCharm. The
project includes Git metadata and a Django run configuration. On a fresh clone,
create `.venv`, install `backend\requirements.txt`, run migrations and seed the
demo catalog.

Useful commands from the PyCharm terminal:

```powershell
git status -sb
git pull --ff-only origin main
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py test apps.catalog apps.leads apps.imports apps.notifications
git add .gitignore .idea backend
git commit -m "Describe the backend change"
git push origin main
```
