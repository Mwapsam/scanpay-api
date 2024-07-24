import requests

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from django.utils.timezone import now, timedelta
from django.core.exceptions import ObjectDoesNotExist
from users.models import Client, Merchant, User
from users.serializers import (
    ClientSerializer,
    MerchantSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    StaffUserSerializer,
)
from utils.email_client import EmailClient
from utils.permissions import IsAdminUser


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "username": user.username,
                "email": user.email,
            }
        )


class Merchants(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        merchants = Merchant.all_merchants()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MerchantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        merchant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Clients(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.delete()
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
        try:
            user = User.objects.get(email=email)
            token = AccessToken.objects.create(
                user=user,
                scope="read write",
                expires=now() + timedelta(hours=1),
                token_generator=oauth2_settings.ACCESS_TOKEN_GENERATOR,
            )
            reset_url = request.build_absolute_uri(
                f"/password-reset-confirm/?token={token.token}"
            )

            email_client = EmailClient(
                token=settings.MAILTRAP_TOKEN,
                receiver=email,
                sender="sender@example.com",
                subject="Password Reset Request",
                html_body=f"<p>Use the link below to reset your password:</p><p><a href='{reset_url}'>Reset Password</a></p>",
            )
            email_client.send()

            return Response(
                {
                    "message": "If your email is registered, you will receive a password reset email shortly."
                },
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": "If your email is registered, you will receive a password reset email shortly."
                },
                status=status.HTTP_200_OK,
            )


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        try:
            access_token = AccessToken.objects.get(token=token, expires__gte=now())
            user = access_token.user
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password reset successful."}, status=status.HTTP_200_OK
            )
        except AccessToken.DoesNotExist:
            return Response(
                {"message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
