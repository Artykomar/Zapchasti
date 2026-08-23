from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import LegalDocument


REQUIRED_DOCUMENT_KINDS = (
    LegalDocument.Kind.PRIVACY_POLICY,
    LegalDocument.Kind.PRIVACY_CONSENT,
    LegalDocument.Kind.TERMS,
    LegalDocument.Kind.DELIVERY,
    LegalDocument.Kind.PAYMENT,
    LegalDocument.Kind.WARRANTY,
    LegalDocument.Kind.RETURNS,
)
PLACEHOLDER_MARKERS = ("draft", "example", "заготов", "нужно заполн", "будет указан")


class Command(BaseCommand):
    help = "Fail unless every required public legal document has approved published content."

    def handle(self, *args, **options):
        failures = []
        expected_versions = {
            LegalDocument.Kind.PRIVACY_POLICY: settings.ZEMAZAP_PRIVACY_POLICY_VERSION,
            LegalDocument.Kind.PRIVACY_CONSENT: settings.ZEMAZAP_PRIVACY_CONSENT_VERSION,
            LegalDocument.Kind.TERMS: settings.ZEMAZAP_TERMS_VERSION,
        }
        for kind in REQUIRED_DOCUMENT_KINDS:
            document = (
                LegalDocument.objects.filter(kind=kind, is_published=True)
                .order_by("-published_at", "-created_at")
                .first()
            )
            if document is None:
                failures.append(f"{kind}: no published document")
                continue
            combined = f"{document.version}\n{document.title}\n{document.body}".strip().lower()
            if not document.published_at:
                failures.append(f"{kind}: published_at is empty")
            if kind in expected_versions and document.version != expected_versions[kind]:
                failures.append(
                    f"{kind}: published version {document.version!r} does not match configured "
                    f"version {expected_versions[kind]!r}"
                )
            if len(document.body.strip()) < 200:
                failures.append(f"{kind}: body is shorter than 200 characters")
            if any(marker in combined for marker in PLACEHOLDER_MARKERS):
                failures.append(f"{kind}: placeholder text detected")

        if failures:
            raise CommandError("Launch content is not ready: " + "; ".join(failures))
        self.stdout.write(self.style.SUCCESS("All required launch documents are published and non-placeholder."))
