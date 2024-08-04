from payments.mtn_api import MtnPaymentHelper, auth_keys
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import PaymentSerializer
from .services import PaymentService
import logging

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                transaction, transaction_ref, payment_status = (
                    PaymentService.process_payment(serializer.validated_data)
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                {
                    "transaction_id": str(transaction.id),
                    "reference": str(transaction.reference_number),
                    "message": "Payment created successfully",
                    "status": payment_status,
                    "transaction_ref": transaction_ref,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
