from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from users.models import Client, Merchant, User


class Command(BaseCommand):
    help = "Generate test data for clients, merchants, and staff users"

    def handle(self, *args, **options):
        self.generate_users(Client, "client", 100)
        self.generate_users(Merchant, "merchant", 100, role=User.Role.MERCHANT)
        self.generate_users(User, "staff", 15, is_staff=True, role=User.Role.ADMIN)

        self.stdout.write(self.style.SUCCESS("Successfully generated test data"))

    def generate_users(self, user_class, prefix, count, is_staff=False, role=None):
        for i in range(count):
            email = f"{prefix}{i + 133}@example.com"
            username = f"{prefix}{i + 133}"
            password = "password123"
            user = user_class.objects.create_user(
                email=email,
                username=username,
                password=password,
                is_staff=is_staff,
                first_name=f"First{get_random_string(5)}",
                last_name=f"Last{get_random_string(5)}",
            )
            if role:
                user.role = role
            user.save()
