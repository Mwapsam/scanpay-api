# services.py
from django.conf import settings
from utils.email_client import EmailClient
from .models import Address, Client, Company, Merchant, User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import logging

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_user(email, password, **extra_fields):
        user = User.objects.create_user(email=email, password=password, **extra_fields)
        return user

    @staticmethod
    def create_merchant(email, password, **extra_fields):
        user = Merchant.objects.create_user(
            email=email, password=password, **extra_fields
        )
        return user

    @staticmethod
    def create_client(email, password, **extra_fields):
        user = Client.objects.create_user(
            email=email, password=password, **extra_fields
        )
        return user

    @staticmethod
    def get_user_detail(user):
        return {
            "username": user.username,
            "email": user.email,
        }


class CompanyService:
    @staticmethod
    def create_company(address_data, company_data):
        address = Address.objects.create(**address_data)
        company = Company.objects.create(address=address, **company_data)
        return company

    @staticmethod
    def update_company(instance, validated_data):
        address_data = validated_data.pop("address", None)
        address = instance.address

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if address_data:
            for attr, value in address_data.items():
                setattr(address, attr, value)
            address.save()

        return instance


class MerchantService:
    @staticmethod
    def list_merchants():
        return Merchant.all_merchants()

    @staticmethod
    def create_merchant(
        email, password, first_name, last_name, username, is_active, ip_address
    ):
        merchant = Merchant.objects.create(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
            is_active=is_active,
            ip_address=ip_address,
            role="MERCHANT",
        )
        return merchant

    @staticmethod
    def update_merchant(merchant, validated_data):
        for attr, value in validated_data.items():
            setattr(merchant, attr, value)
        merchant.save()
        return merchant

    @staticmethod
    def delete_merchant(merchant):
        merchant.delete()


class ClientService:
    @staticmethod
    def list_clients():
        return Client.objects.all()

    @staticmethod
    def create_client(validated_data):
        return Client.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            username=validated_data.get("username", ""),
        )

    @staticmethod
    def update_client(client, validated_data):
        for attr, value in validated_data.items():
            setattr(client, attr, value)
        client.save()
        return client

    @staticmethod
    def delete_client(client):
        client.delete()


class PasswordService:
    @staticmethod
    def request_password_reset(email, client_url):
        try:
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{client_url}/password-reset-confirm/{uid}/{token}"

            email_client = EmailClient(
                token=settings.MAILTRAP_TOKEN,
                receiver=email,
                sender="mailtrap@mwape.org",
                subject="Password Reset Request",
                html_body=f"<p>Use the link below to reset your password:</p><p><a href='{reset_url}'>Reset Password</a></p>",
            )
            email_client.send()

            return {
                "message": "If your email is registered, you will receive a password reset email shortly."
            }
        except ObjectDoesNotExist:
            return {
                "message": "If your email is registered, you will receive a password reset email shortly."
            }

    @staticmethod
    def reset_password(uid, token, new_password):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            token_generator = PasswordResetTokenGenerator()

            if token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return {"message": "Password reset successful."}
            else:
                return {"message": "Invalid or expired token."}
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return {"message": "Invalid or expired token."}


class AccountActivationService:
    @staticmethod
    def send_activation_email(user):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.CLIENT_URL}/account-confirmation/{uid}/{token}"
        email = user.email
        email_client = EmailClient(
            token=settings.MAILTRAP_TOKEN,
            receiver=email,
            sender="mailtrap@mwape.org",
            subject="Account Activation",
            html_body=f"<p>Use the link below to activate your account:</p><p><a href='{reset_url}'>Activate Account</a></p>",
        )
        try:
            email_client.send()
            logger.info("Confirmation Email Sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

    @staticmethod
    def activate_account(uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            token_generator = PasswordResetTokenGenerator()

            if token_generator.check_token(user, token):
                user.is_active = True
                user.is_staff = True
                user.save()
                logger.info(f"User {user.email} activated successfully.")
                return {"message": "Account activated successfully."}
            else:
                logger.warning(f"Invalid or expired token for user {user.email}.")
                return {"message": "Invalid or expired token."}
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Error activating account: {e}")
            return {"message": "Invalid or expired token."}
