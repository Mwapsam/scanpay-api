from rest_framework.permissions import BasePermission
from users.models import User


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.MERCHANT
        )


class AllowAnyPostPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )
