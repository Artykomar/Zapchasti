from django.db import models


class PriceImport(models.Model):
    filename = models.CharField(max_length=240)
    file_kind = models.CharField(max_length=40)
    imported_rows = models.PositiveIntegerField(default=0)
    skipped_rows = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.filename}: {self.imported_rows} imported"

# Create your models here.
