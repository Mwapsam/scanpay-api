from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid


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


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.province}, {self.postal_code}, {self.country}"


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    logo = models.ImageField(upload_to="logos", blank=True, null=True)
    tpin = models.IntegerField(blank=True, null=True)
    business_profile = models.FileField(
        upload_to="business_profiles/",
        validators=[FileExtensionValidator(["pdf", "docx"])],
        blank=True,
        null=True,
    )
    id_card = models.FileField(
        upload_to="id_card/",
        validators=[FileExtensionValidator(["pdf", "docx"])],
        blank=True,
        null=True,
    )
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, related_name="company"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        blank=True,
        null=True,
    )

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        unique=True,
        blank=True,
        null=True,
    )
    picture = models.ImageField(upload_to="picture", blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    network_size = models.PositiveIntegerField(default=0)
    mfa_token = models.CharField(max_length=100, blank=True, null=True)
    mfa_token_expiry = models.DateTimeField(blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, blank=True, null=True, related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CLIENT = "CLIENT", "Client"
        MERCHANT = "MERCHANT", "Merchant"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)

    def save(self, *args, **kwargs):
        if not self.mfa_token:
            self.mfa_token = get_random_string(50)
            self.mfa_token_expiry = timezone.now() + timezone.timedelta(days=7)
        if not self.pk:
            self.role = self.base_role
        super().save(*args, **kwargs)

    def clean(self):
        if (
            self.mfa_token
            and self.mfa_token_expiry
            and self.mfa_token_expiry < timezone.now()
        ):
            raise ValidationError("MFA token has expired.")
        super().clean()

    class Meta:
        indexes = [
            models.Index(fields=["email"], name="email_idx"),
        ]


class ClientManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Role.CLIENT)


class Client(User):
    base_role = User.Role.CLIENT

    objects = ClientManager()

    class Meta:
        proxy = True
        ordering = ["email"]

    @classmethod
    def all_clients(cls):
        return cls.objects.filter(is_active=True).count()


class MerchantManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Role.MERCHANT)


class Merchant(User):
    base_role = User.Role.MERCHANT

    objects = MerchantManager()

    class Meta:
        proxy = True
        ordering = ["email"]

    @classmethod
    def all_merchants(cls):
        return cls.objects.all()
