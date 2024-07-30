import random
import string
import uuid

from django.core.management.base import BaseCommand
from users.models import Address, Company, Merchant


class Command(BaseCommand):
    help = "Generate dummy companies and addresses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=10,
            help="Number of companies and addresses to create",
        )

    def handle(self, *args, **options):
        number = options["number"]
        merchants = Merchant.objects.all()
        if not merchants.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No merchants found. Please create some merchants first."
                )
            )
            return

        for _ in range(number):
            address = Address.objects.create(
                street=self.random_string(10) + " Street",
                city=self.random_string(6),
                province=self.random_string(6),
                postal_code=self.random_string(5, digits=True),
                country="Country " + self.random_string(3),
            )

            company = Company.objects.create(
                name=self.random_string(10) + " Co.",
                address=address,
                tpin=random.randint(1000000000, 9999999999),
                phone_number="+1" + self.random_string(10, digits=True),
                status=random.choice([status for status, _ in Company.Status.choices]),
            )
            merchant = random.choice(merchants)
            merchant.company = company
            merchant.save()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {number} companies and addresses")
        )

    def random_string(self, length, digits=False):
        if digits:
            return "".join(random.choices(string.digits, k=length))
        return "".join(random.choices(string.ascii_letters, k=length))
