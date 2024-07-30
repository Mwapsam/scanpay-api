import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sales.models import PaymentMethods, Transaction
from users.models import Client, Merchant


class Command(BaseCommand):
    help = "Generate dummy transactions"

    def handle(self, *args, **kwargs):
        clients = Client.objects.all()
        merchants = Merchant.objects.all()

        if not clients.exists():
            self.stdout.write(
                self.style.ERROR("No clients found. Please create some clients first.")
            )
            return

        if not merchants.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No merchants found. Please create some merchants first."
                )
            )
            return

        for _ in range(100):
            client = random.choice(clients)
            merchant = random.choice(merchants)
            amount = round(
                random.uniform(10.00, 1000.00), 2
            )  # Random amount between 10 and 1000
            transaction_date = timezone.now() - timedelta(days=random.randint(0, 30))
            status = random.choice(["PENDING", "COMPLETED", "FAILED"])
            payment_method = random.choice(PaymentMethods.values)
            reference_number = str(uuid.uuid4())
            description = "Dummy transaction description"

            Transaction.objects.create(
                client=client,
                merchant=merchant,
                amount=amount,
                transaction_date=transaction_date,
                status=status,
                payment_method=payment_method,
                reference_number=reference_number,
                description=description,
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully created 100 dummy transactions.")
        )
