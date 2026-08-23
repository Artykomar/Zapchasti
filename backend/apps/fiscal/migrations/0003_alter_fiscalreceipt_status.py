from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("fiscal", "0002_fiscalreceipt_refund_and_more")]

    operations = [
        migrations.AlterField(
            model_name="fiscalreceipt",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "draft"),
                    ("validated", "validated"),
                    ("pending_confirmation", "pending confirmation"),
                    ("sent", "sent"),
                    ("failed", "failed"),
                ],
                default="draft",
                max_length=40,
            ),
        ),
    ]
