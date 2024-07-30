from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from .services import create_invoice_for_transaction


@receiver(post_save, sender=Transaction)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        create_invoice_for_transaction(instance)
