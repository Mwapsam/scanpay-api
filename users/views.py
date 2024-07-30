# views.py
from django.conf import settings
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Address, Client, Merchant, User
from users.services import (
    AccountActivationService,
    UserService,
    MerchantService,
    ClientService,
    CompanyService,
    PasswordService,
)
from users.serializers import (
    AddressSerializer,
    ClientSerializer,
    CompanySerializer,
    MerchantSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    StaffUserSerializer,
)
from utils.permissions import AllowAnyPostPermission, IsAdminUser, IsMerchant


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_detail = UserService.get_user_detail(user)
        return Response(user_detail)


class Merchants(APIView):
    permission_classes = [AllowAnyPostPermission]

    def get(self, request):
        merchants = MerchantService.list_merchants()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MerchantSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            merchant = serializer.save()
            return Response(
                MerchantSerializer(merchant).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            updated_merchant = MerchantService.update_merchant(
                merchant, serializer.validated_data
            )
            return Response(
                MerchantSerializer(updated_merchant).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            updated_merchant = MerchantService.update_merchant(
                merchant, serializer.validated_data
            )
            return Response(
                MerchantSerializer(updated_merchant).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        MerchantService.delete_merchant(merchant)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Clients(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        clients = ClientService.list_clients()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            client = ClientService.create_client(serializer.validated_data)
            return Response(
                ClientSerializer(client).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            updated_client = ClientService.update_client(
                client, serializer.validated_data
            )
            return Response(
                ClientSerializer(updated_client).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            updated_client = ClientService.update_client(
                client, serializer.validated_data
            )
            return Response(
                ClientSerializer(updated_client).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        ClientService.delete_client(client)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExchangeToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            code = request.data.get("code")
            redirect_uri = request.data.get("redirect_uri")
            code_verifier = request.data.get("code_verifier")

            if not all([code, redirect_uri, code_verifier]):
                return Response(
                    {"error": "Missing code, redirect_uri, or code_verifier"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = requests.post(
                f"{settings.BASE_URL}/o/token/",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                },
            )

            if response.status_code == 200:
                return Response(response.json())
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RevokeToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            token = request.data.get("token")

            if not token:
                return Response(
                    {"error": "Missing token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = requests.post(
                f"{settings.BASE_URL}/o/revoke_token/",
                data={
                    "token": token,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                return Response(
                    {"detail": "Token revoked successfully"}, status=status.HTTP_200_OK
                )
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            client_identifier = request.headers.get("X-Client-Identifier")

            if not refresh_token:
                return Response(
                    {"error": "Missing refresh_token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not client_identifier:
                return Response(
                    {"error": "Missing client identifier"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if client_identifier != settings.CLIENT_IDENTIFIER:
                return Response(
                    {"error": "Invalid client identifier"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            response = requests.post(
                f"{settings.BASE_URL}/o/token/",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                return Response(response.json())
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StaffUsers(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk, is_staff=True)
            serializer = StaffUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            users = User.objects.filter(is_staff=True)
            serializer = StaffUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StaffUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_staff=True)
        serializer = StaffUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_staff=True)
        serializer = StaffUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_staff=True)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        response_data = PasswordService.request_password_reset(
            email, settings.CLIENT_URL
        )
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        response_data = PasswordService.reset_password(uid, token, new_password)
        return Response(
            response_data,
            status=(
                status.HTTP_200_OK
                if response_data["message"] == "Password reset successful."
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class ActivateAccount(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        response_data = AccountActivationService.activate_account(uid, token)
        return Response(
            response_data,
            status=(
                status.HTTP_200_OK
                if response_data["message"] == "Account activated successfully."
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class AddressListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant | IsAdminUser]

    def get(self, request):
        companies = CompanyService.list_companies()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            company = CompanyService.create_company(serializer.validated_data)
            return Response(
                CompanySerializer(company).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
