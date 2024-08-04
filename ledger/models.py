import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class LedgerEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(
        "sales.Transaction",
        on_delete=models.CASCADE,
        related_name="ledger_entry",
        null=True,
        blank=True,
    )
    invoice = models.OneToOneField(
        "sales.Invoice",
        on_delete=models.CASCADE,
        related_name="ledger_entry",
        null=True,
        blank=True,
    )
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        last_entry = LedgerEntry.objects.last()
        if last_entry:
            self.balance = last_entry.balance + self.debit - self.credit
        else:
            self.balance = self.debit - self.credit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.balance}"

    class Meta:
        indexes = [
            models.Index(fields=["date"], name="ledger_entry_date_idx"),
        ]
