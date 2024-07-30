import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Client, Merchant


class PaymentMethods(models.TextChoices):
    MTN_MONEY = "MTN_MONEY", _("Mtn")
    AIRTEL = "AIRTEL_MONEY", _("Airtel")
    ZAMTEL = "ZAMTEL_KWACHA", _("Zamtel")
    CREDIT_CARD = "CREDIT_CARD", _("Credit Card")


class Transaction(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_COMPLETED, _("Completed")),
        (STATUS_FAILED, _("Failed")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_transactions"
    )
    merchant = models.ForeignKey(
        Merchant, on_delete=models.CASCADE, related_name="merchant_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethods.choices,
        default=PaymentMethods.AIRTEL,
    )
    reference_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.reference_number} - {self.amount} {self.get_payment_method_display()}"

    class Meta:
        indexes = [
            models.Index(fields=["payment_method"], name="payment_method_idx"),
            models.Index(fields=["-transaction_date"], name="transaction_date_idx"),
        ]


class Invoice(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"
    STATUS_OVERDUE = "OVERDUE"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_PAID, _("Paid")),
        (STATUS_OVERDUE, _("Overdue")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_invoices"
    )
    merchant = models.ForeignKey(
        Merchant, on_delete=models.CASCADE, related_name="merchant_invoices"
    )
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    transactions = models.ManyToManyField(
        Transaction, related_name="invoices", blank=True
    )

    def __str__(self):
        return f"Invoice {self.id} - {self.total_amount} {self.get_status_display()}"

    class Meta:
        indexes = [
            models.Index(fields=["status"], name="invoice_status_idx"),
            models.Index(fields=["-issue_date"], name="issue_date_idx"),
        ]
