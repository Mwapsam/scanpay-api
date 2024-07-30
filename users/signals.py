from django.conf import settings
from users.models import Merchant
from users.services import AccountActivationService
from utils.email_client import EmailClient
from utils.qr_code_generator import convert_base64, generate_qr
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Merchant)
def create_merchant_qr_code(sender, instance, created, **kwargs):
    if created:

        qr_data = generate_qr(instance.pk)
        qr_code_dict = generate_qr(qr_data)
        base64_str = qr_code_dict["image_base64"]

        img = convert_base64(base64_str, instance.pk)

        instance.qr_code = img
        instance.save()

        logger.debug("QR code generated and saved successfully.")


@receiver(post_save, sender=Merchant)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        AccountActivationService.send_activation_email(instance)
