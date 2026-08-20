from __future__ import annotations

import hashlib

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


def _client_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "unknown")


class AdminLoginRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_login_post = request.method == "POST" and request.path.rstrip("/").endswith("/admin/login")
        if not is_login_post:
            return self.get_response(request)

        digest = hashlib.sha256(_client_ip(request).encode("utf-8")).hexdigest()
        cache_key = f"zemazap:admin-login:{digest}"
        limit = getattr(settings, "ADMIN_LOGIN_RATE_LIMIT", 10)
        if cache.get(cache_key, 0) >= limit:
            return JsonResponse({"error": "Too many login attempts. Try again later."}, status=429)

        response = self.get_response(request)
        if 300 <= response.status_code < 400:
            cache.delete(cache_key)
        else:
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, timeout=getattr(settings, "ADMIN_LOGIN_LOCKOUT_SECONDS", 900))
        return response
