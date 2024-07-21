import requests

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Merchant, User
from users.serializers import MerchantSerializer, StaffUserSerializer, UserSerializer
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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        merchants = Merchant.objects.all()
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

    def delete(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        merchant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            response = requests.post(
                f"{settings.BASE_URL}/o/token/",
                data={
                    "grant_type": "password",
                    "username": request.data["email"],
                    "password": request.data["password"],
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                },
            )

            if response.status_code == 200:
                return Response(response.json())
            else:
                return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except KeyError as e:
            return Response(
                {"error": f"Missing parameter: {e}"}, status=status.HTTP_400_BAD_REQUEST
            )


class ExchangeToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            code = request.data.get("code")
            redirect_uri = request.data.get("redirect_uri")
            code_verifier = request.data.get("code_verifier")

            if not code or not redirect_uri or not code_verifier:
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
            else:
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

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_staff=True)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
