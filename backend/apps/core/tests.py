from django.core.checks import Tags, run_checks
from django.test import SimpleTestCase, TestCase, override_settings

from .services import build_public_site_settings


class PublicSiteSettingsTests(TestCase):
    def test_site_settings_endpoint_returns_safe_defaults(self):
        response = self.client.get("/api/site-settings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["brand"]["name"], "Zemazap")
        self.assertFalse(response.json()["featureFlags"]["paymentsEnabled"])

    def test_public_site_settings_service_returns_feature_flags(self):
        payload = build_public_site_settings()

        self.assertIn("contacts", payload)
        self.assertIn("legal", payload)
        self.assertEqual(payload["featureFlags"]["paymentsMode"], "test")


class LaunchConfigurationChecksTests(SimpleTestCase):
    @override_settings(PAYMENTS_MODE="broken")
    def test_rejects_unknown_payment_mode(self):
        messages = run_checks(tags=[Tags.security])

        self.assertTrue(any(message.id == "zemazap.E001" for message in messages))

    @override_settings(
        DEBUG=False,
        ZEMAZAP_SITE_URL="http://127.0.0.1:3000",
        ZEMAZAP_PUBLIC_PHONE_LABEL="",
        ZEMAZAP_PUBLIC_EMAIL="",
        ZEMAZAP_LEGAL_NAME="",
        ZEMAZAP_LEGAL_INN="",
        ZEMAZAP_PRIVACY_POLICY_VERSION="",
        ZEMAZAP_PRIVACY_CONSENT_VERSION="",
    )
    def test_production_requires_public_legal_contract(self):
        messages = run_checks(tags=[Tags.security], include_deployment_checks=True)

        ids = {message.id for message in messages}
        self.assertIn("zemazap.E006", ids)
        self.assertIn("zemazap.E007", ids)

    @override_settings(
        PAYMENTS_ENABLED=True,
        PAYMENTS_MODE="prod",
        PAYMENTS_PROVIDER="alfa",
        ZEMAZAP_SELLER_PROFILE="ip",
        FISCALIZATION_ENABLED=False,
        ALFA_BANK_GATEWAY_URL="",
        ALFA_BANK_USERNAME="",
        ALFA_BANK_PASSWORD="",
    )
    def test_production_payments_require_fiscalization_and_bank_credentials(self):
        messages = run_checks(tags=[Tags.security])

        ids = {message.id for message in messages}
        self.assertIn("zemazap.E004", ids)
        self.assertIn("zemazap.E005", ids)
