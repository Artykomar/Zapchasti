from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?7|8)?[\s(.-]*\d{3}[\s).-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}(?!\d)")


def redact_sensitive_text(value: str) -> str:
    return PHONE_PATTERN.sub("[phone-redacted]", EMAIL_PATTERN.sub("[email-redacted]", value))


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_text(str(record.msg))
        if isinstance(record.args, dict):
            record.args = {key: redact_sensitive_text(str(value)) for key, value in record.args.items()}
        elif isinstance(record.args, tuple):
            record.args = tuple(redact_sensitive_text(str(value)) for value in record.args)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("delivery_id", "channel", "error_code", "request_id", "payment_id", "refund_id"):
            value = getattr(record, key, None)
            if value not in (None, ""):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False, default=str)
