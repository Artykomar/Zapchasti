from django.core.checks import Tags, run_checks
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from unittest.mock import patch

from .management.commands.check_launch_content import REQUIRED_DOCUMENT_KINDS
from .models import LegalDocument
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

    def test_public_site_settings_exposes_only_published_legal_document(self):
        published = LegalDocument.objects.create(
            kind=LegalDocument.Kind.PRIVACY_POLICY,
            version="policy-v1",
            title="Политика",
            body="Утвержденный публичный текст политики.",
            is_published=True,
        )
        LegalDocument.objects.create(
            kind=LegalDocument.Kind.TERMS,
            version="private-draft",
            title="Черновик",
            body="Не публиковать",
            is_published=False,
        )

        payload = build_public_site_settings()

        self.assertEqual(payload["documents"]["published"]["privacy_policy"]["body"], published.body)
        self.assertNotIn("terms", payload["documents"]["published"])

    def test_unpublishing_resets_timestamp_so_republishing_becomes_current(self):
        document = LegalDocument.objects.create(
            kind=LegalDocument.Kind.PRIVACY_POLICY,
            version="policy-v1",
            title="Политика",
            body="Утвержденный публичный текст политики.",
            is_published=True,
        )
        first_published_at = document.published_at

        document.is_published = False
        document.save()
        self.assertIsNone(document.published_at)

        document.is_published = True
        document.save()
        self.assertIsNotNone(document.published_at)
        self.assertGreaterEqual(document.published_at, first_published_at)

    @override_settings(
        ZEMAZAP_PRIVACY_POLICY_VERSION="2026-08-23-v1",
        ZEMAZAP_PRIVACY_CONSENT_VERSION="2026-08-23-v1",
        ZEMAZAP_TERMS_VERSION="2026-08-23-v1",
    )
    def test_launch_content_command_requires_all_approved_documents(self):
        with self.assertRaises(CommandError):
            call_command("check_launch_content")

        for kind in REQUIRED_DOCUMENT_KINDS:
            LegalDocument.objects.create(
                kind=kind,
                version="2026-08-23-v1",
                title=f"Утвержденный документ: {kind}",
                body=("Утвержденные условия работы магазина и права покупателя. " * 5),
                is_published=True,
            )

        call_command("check_launch_content", verbosity=0)


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

    @override_settings(
        PAYMENTS_ENABLED=True,
        PAYMENTS_MODE="prod",
        PAYMENTS_PROVIDER="alfa",
        ZEMAZAP_SELLER_PROFILE="ooo",
        FISCALIZATION_ENABLED=True,
        FISCAL_PROVIDER="alfa",
        FISCAL_TAX_SYSTEM="",
        ALFA_BANK_GATEWAY_URL="http://bank.invalid",
        ALFA_BANK_TOKEN="token",
        ALFA_BANK_CALLBACK_TOKEN="short",
    )
    def test_production_payment_contract_rejects_insecure_values(self):
        ids = {message.id for message in run_checks(tags=[Tags.security])}

        self.assertIn("zemazap.E014", ids)
        self.assertIn("zemazap.E015", ids)
        self.assertIn("zemazap.E016", ids)


class OperationsSchedulerTests(SimpleTestCase):
    @patch("apps.core.management.commands.run_operations_scheduler.call_command")
    def test_once_runs_all_operational_commands(self, scheduled_call_command):
        call_command("run_operations_scheduler", once=True)

        self.assertEqual(
            [call.args[0] for call in scheduled_call_command.call_args_list],
            [
                "reconcile_pending_payments",
                "retry_failed_receipts",
                "retry_notifications",
                "sync_cdek_shipments",
                "anonymize_personal_data",
            ],
        )
