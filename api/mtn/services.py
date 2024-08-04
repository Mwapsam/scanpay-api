from payments.mtn_api import MtnPaymentHelper, auth_keys
import logging
from django.db import transaction as db_transaction
from sales.models import Transaction

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def create_payment(validated_data):
        return Transaction.objects.create(
            client=validated_data["client"],
            merchant=validated_data["merchant"],
            amount=validated_data["amount"],
            payment_method=validated_data.get("payment_method", "DEFAULT_METHOD"),
            description=validated_data.get("description", ""),
        )

    @staticmethod
    def authenticate():
        result_hash = auth_keys()
        if not result_hash:
            logger.error("Failed to obtain API keys.")
            return None, None

        api_key = result_hash.get("api_key")
        api_user = result_hash.get("api_user")

        if not api_key or not api_user:
            logger.error("API key or user not found")
            return None, None

        return api_user, api_key

    @staticmethod
    def initiate_payment(transaction, api_user, api_key):
        party_id = "46733123453"
        external_id = str(transaction.reference_number)
        payment_helper = MtnPaymentHelper(api_user_id=api_user, api_key=api_key)

        try:
            transaction_ref = payment_helper.request_to_pay(
                amount=transaction.amount,
                currency="EUR",
                party_id=party_id,
                external_id=external_id,
            )
            if not transaction_ref:
                logger.error("Failed to initiate payment request.")
                return None

            logger.info(f"Payment initiated. Transaction reference: {transaction_ref}")
            return transaction_ref
        except Exception as e:
            logger.error(f"Error during payment initiation: {e}")
            return None

    @staticmethod
    def check_payment_status(payment_helper, transaction_ref):
        try:
            payment_status = payment_helper.check_payment_status(transaction_ref)
            if not payment_status:
                logger.error("Failed to check payment status.")
                return None

            logger.info(f"Payment status: {payment_status}")
            return payment_status
        except Exception as e:
            logger.error(f"Error during payment status check: {e}")
            return None

    @staticmethod
    @db_transaction.atomic
    def process_payment(validated_data):
        transaction = PaymentService.create_payment(validated_data)

        api_user, api_key = PaymentService.authenticate()
        if not api_user or not api_key:
            raise Exception("Failed to obtain API keys")

        transaction_ref = PaymentService.initiate_payment(
            transaction, api_user, api_key
        )
        if not transaction_ref:
            raise Exception("Failed to initiate payment request")

        payment_helper = MtnPaymentHelper(api_user_id=api_user, api_key=api_key)
        payment_status = PaymentService.check_payment_status(
            payment_helper, transaction_ref
        )
        if not payment_status:
            raise Exception("Failed to check payment status")

        return transaction, transaction_ref, payment_status
