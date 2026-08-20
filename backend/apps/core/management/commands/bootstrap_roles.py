from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLE_PERMISSIONS = {
    "owner": ["*"],
    "manager": [
        "view_customerrequest",
        "change_customerrequest",
        "view_request_pii",
        "view_customer",
        "view_customer_pii",
        "view_order",
        "view_order_pii",
        "add_order",
        "change_order",
        "view_payment",
        "view_refund",
        "add_claim",
        "change_claim",
        "view_claim",
        "view_claim_pii",
    ],
    "content": [
        "view_brand",
        "change_brand",
        "view_carmodel",
        "change_carmodel",
        "view_category",
        "change_category",
        "view_part",
        "add_part",
        "change_part",
        "view_manufacturer",
        "view_supplier",
    ],
    "accountant": [
        "view_order",
        "view_payment",
        "view_payment_details",
        "view_refund",
        "add_refund",
        "change_refund",
        "view_fiscalreceipt",
    ],
    "techadmin": [
        "view_sitesettings",
        "change_sitesettings",
        "view_legalentitysettings",
        "change_legalentitysettings",
        "view_notificationdelivery",
        "change_notificationdelivery",
    ],
}


class Command(BaseCommand):
    help = "Create/update Zemazap Django admin groups with least-privilege model permissions."

    def handle(self, *args, **options):
        all_permissions = Permission.objects.select_related("content_type").all()
        by_codename = {}
        for permission in all_permissions:
            by_codename.setdefault(permission.codename, []).append(permission)

        for role_name, codenames in ROLE_PERMISSIONS.items():
            group, _created = Group.objects.get_or_create(name=role_name)
            if codenames == ["*"]:
                permissions = list(all_permissions)
            else:
                permissions = [permission for codename in codenames for permission in by_codename.get(codename, [])]
            group.permissions.set(permissions)
            self.stdout.write(f"{role_name}: {len(permissions)} permission(s)")

        self.stdout.write(self.style.SUCCESS("Zemazap roles are ready."))
