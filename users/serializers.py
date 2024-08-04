from rest_framework import serializers
from .models import Address, Client, Company, Merchant, User
from .services import UserService, CompanyService


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "is_active"]
        read_only_fields = ["id"]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class MerchantSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Merchant
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "ip_address": {"read_only": True},
        }

    def create(self, validated_data):
        ip_address = self.context.get("request").META.get("REMOTE_ADDR")
        return UserService.create_merchant(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            username=validated_data.get("username", ""),
            is_active=True,
            ip_address=ip_address,
            role=User.Role.MERCHANT
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.date_joined.strftime("%d %B, %Y")
        return representation

    def validate_email(self, value):
        if Merchant.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.date_joined.strftime("%d %B, %Y")
        return representation

    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data):
        return UserService.create_client(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            username=validated_data.get("username", ""),
        )


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        return UserService.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_staff=True,
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        # Add more password validation if needed
        return data


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Company
        fields = "__all__"

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        return CompanyService.create_company(address_data, validated_data)

    def update(self, instance, validated_data):
        return CompanyService.update_company(instance, validated_data)

    def validate_name(self, value):
        if Company.objects.filter(name=value).exists():
            raise serializers.ValidationError("Company name is already in use.")
        return value
