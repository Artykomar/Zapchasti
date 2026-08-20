from django.db import models


class Customer(models.Model):
    display_name = models.CharField(max_length=160)
    contact = models.CharField(max_length=160)
    normalized_contact = models.CharField(max_length=160, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["normalized_contact"]),
        ]
        permissions = [("view_customer_pii", "Can view customer personal data")]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.contact})"

# Create your models here.
