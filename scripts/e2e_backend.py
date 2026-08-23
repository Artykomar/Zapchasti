from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
MANAGE_PY = BACKEND_DIR / "manage.py"
ALLOWED_DATABASE_PATH = (BACKEND_DIR / "data" / "zemazap_e2e.sqlite3").resolve()


def run_management_command(*arguments: str) -> None:
    import subprocess

    subprocess.run(
        [sys.executable, str(MANAGE_PY), *arguments],
        cwd=ROOT_DIR,
        env=os.environ.copy(),
        check=True,
    )


def prepare_admin() -> None:
    sys.path.insert(0, str(BACKEND_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()

    from django.contrib.auth import get_user_model

    username = os.getenv("E2E_ADMIN_USERNAME", "e2e_admin")
    password = os.getenv("E2E_ADMIN_PASSWORD", "zemazap-e2e-only")
    user_model = get_user_model()
    admin, _created = user_model.objects.update_or_create(
        username=username,
        defaults={
            "email": "e2e-admin@example.invalid",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    admin.set_password(password)
    admin.save(update_fields=["password"])


def main() -> None:
    database_path = Path(os.environ.get("E2E_DATABASE_PATH", ALLOWED_DATABASE_PATH)).resolve()
    if database_path != ALLOWED_DATABASE_PATH:
        raise RuntimeError(f"Refusing to reset a non-E2E database: {database_path}")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.unlink(missing_ok=True)

    run_management_command("migrate", "--noinput")
    run_management_command("seed_demo")
    run_management_command("bootstrap_roles")
    prepare_admin()

    from django.core.management import execute_from_command_line

    os.chdir(ROOT_DIR)
    execute_from_command_line(
        [
            str(MANAGE_PY),
            "runserver",
            "127.0.0.1:8100",
            "--noreload",
        ]
    )


if __name__ == "__main__":
    main()
