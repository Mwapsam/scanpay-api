from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Invoice, Transaction
from .services import create_invoice_for_transaction


@receiver(post_save, sender=Transaction)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        create_invoice_for_transaction(instance)


@receiver(pre_save, sender=Transaction)
def update_transaction_ledger(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Transaction.objects.get(pk=instance.pk)
            if previous.status != instance.status:
                if instance.ledger_entry:
                    if instance.status == Transaction.STATUS_COMPLETED:
                        instance.ledger_entry.debit = instance.amount
                        instance.ledger_entry.credit = 0.00
                    elif instance.status == Transaction.STATUS_FAILED:
                        instance.ledger_entry.debit = 0.00
                        instance.ledger_entry.credit = instance.amount
                    instance.ledger_entry.save()
        except Transaction.DoesNotExist:
            pass

@receiver(post_delete, sender=Transaction)
def delete_transaction_ledger(sender, instance, **kwargs):
    if instance.ledger_entry:
        instance.ledger_entry.delete()


@receiver(post_delete, sender=Invoice)
def delete_invoice_ledger(sender, instance, **kwargs):
    if instance.ledger_entry:
        instance.ledger_entry.delete()
