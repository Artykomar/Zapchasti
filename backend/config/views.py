from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache


@never_cache
def admin_entry(request):
    """Send the active owner persona to its dashboard after every admin login."""
    if not request.user.is_active or not request.user.is_staff:
        return redirect_to_login(request.get_full_path(), reverse("admin:login"))
    if request.user.is_superuser or request.user.groups.filter(name="owner").exists():
        return redirect("owner-dashboard")
    return admin.site.index(request)


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable", "backend": "django", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "backend": "django", "database": "ok"})
