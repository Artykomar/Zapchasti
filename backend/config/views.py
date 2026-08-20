from django.db import connection
from django.http import JsonResponse


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable", "backend": "django", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "backend": "django", "database": "ok"})
