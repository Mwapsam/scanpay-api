from .models import Transaction, Invoice
from django.utils import timezone

def create_invoice_for_transaction(transaction):
    invoice = Invoice.objects.create(
        client=transaction.client,
        merchant=transaction.merchant,
        due_date=timezone.now() + timezone.timedelta(days=30),
        total_amount=transaction.amount,
        status="PENDING",
    )
    invoice.transactions.add(transaction)
    return invoice
