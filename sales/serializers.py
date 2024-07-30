from rest_framework import serializers
from users.serializers import ClientSerializer, MerchantSerializer
from .models import Transaction, Invoice


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    merchant = MerchantSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["issue_date"] = instance.issue_date.strftime("%d %B, %Y")
        return representation
