# Zemazap Django backend

This folder is the Django migration target for the Zemazap backend. The old
Next.js backend remains on the `main` branch as a backup; the Django backend is
developed on `master`.

## Local setup

```powershell
cd C:\Users\ArtyM\Documents\Website
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_demo
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

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

## PyCharm

Open the repository root `C:\Users\ArtyM\Documents\Website` in PyCharm. The
project includes Git metadata and a Django run configuration. On a fresh clone,
create `.venv`, install `backend\requirements.txt`, run migrations and seed the
demo catalog.

Useful commands from the PyCharm terminal:

```powershell
git status -sb
git pull --ff-only origin master
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py test apps.catalog apps.leads
git add .gitignore .idea backend
git commit -m "Describe the backend change"
git push origin master
```
