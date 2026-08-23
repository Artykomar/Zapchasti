from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("payments", "0002_alter_payment_options_payment_provider_order_number_and_more")]

    operations = [
        migrations.AlterModelOptions(
            name="payment",
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    ("view_payment_details", "Can view payment provider details"),
                    ("create_payment_link", "Can create payment links"),
                    ("reconcile_payment", "Can reconcile payment status with provider"),
                ],
            },
        ),
    ]
