from django.test import SimpleTestCase

from .logging import redact_sensitive_text


class SensitiveLoggingTests(SimpleTestCase):
    def test_email_and_phone_are_redacted(self):
        text = redact_sensitive_text("client@example.ru called +7 (999) 111-22-33")

        self.assertNotIn("client@example.ru", text)
        self.assertNotIn("999", text)
        self.assertIn("[email-redacted]", text)
        self.assertIn("[phone-redacted]", text)
