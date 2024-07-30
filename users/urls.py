from django.urls import path
from .views import (
    ActivateAccount,
    AddressListCreateAPIView,
    Clients,
    CompanyListCreateAPIView,
    ExchangeToken,
    Merchants,
    PasswordResetRequestView,
    PasswordResetView,
    RefreshToken,
    RevokeToken,
    StaffUsers,
    UserDetailView,
)


urlpatterns = [
    path("exchange-token/", ExchangeToken.as_view(), name="exchange-token"),
    path("revoke-token/", RevokeToken.as_view(), name="revoke-token"),
    path("refresh-token/", RefreshToken.as_view(), name="refresh-token"),
    path("current-user/", UserDetailView.as_view(), name="user_detail"),
    path("merchants/", Merchants.as_view(), name="merchants"),
    path("merchants/<uuid:pk>/", Merchants.as_view(), name="merchants-detail"),
    path("staff-users/", StaffUsers.as_view(), name="staff-users"),
    path("staff-users/<uuid:pk>/", StaffUsers.as_view(), name="staff-users-detail"),
    path("clients/", Clients.as_view(), name="clients"),
    path("clients/<uuid:pk>/", StaffUsers.as_view(), name="clients-detail"),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetView.as_view(),
        name="password_reset_confirm",
    ),
    path("addresses/", AddressListCreateAPIView.as_view(), name="address-list-create"),
    path("companies/", CompanyListCreateAPIView.as_view(), name="company-list-create"),
    path(
        "account-confirmation/", ActivateAccount.as_view(), name="account-confirmation"
    ),
]
