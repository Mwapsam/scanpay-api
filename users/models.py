from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CLIENT = "CLIENT", "Client"
        MERCHANT = "MERCHANT", "Merchant"

    base_role = Role.CLIENT

    role = models.CharField(max_length=10, choices=Role.choices, default=base_role)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        super().save(*args, **kwargs)


class ClientManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.CLIENT)


class Client(User):
    base_role = User.Role.CLIENT

    objects = ClientManager()

    class Meta:
        proxy = True
        ordering = ["email"]

    @classmethod
    def all_clients(cls):
        return User.objects.filter(role=User.Role.CLIENT, is_active=True).count()


class MerchantManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.MERCHANT)


class Merchant(User):
    base_role = User.Role.MERCHANT

    objects = MerchantManager()

    class Meta:
        proxy = True
        ordering = ["email"]

    @classmethod
    def all_merchants(cls):
        return User.objects.filter(role=User.Role.MERCHANT, is_active=True).count()
