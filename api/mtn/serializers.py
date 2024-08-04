from rest_framework import serializers
from sales.models import PaymentMethods
from users.models import Client, Merchant


class PaymentSerializer(serializers.Serializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), pk_field=serializers.UUIDField()
    )
    merchant = serializers.PrimaryKeyRelatedField(
        queryset=Merchant.objects.all(), pk_field=serializers.UUIDField()
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(
        choices=PaymentMethods.choices, required=False
    )  
    description = serializers.CharField(required=False, allow_blank=True)
