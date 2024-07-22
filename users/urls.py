from django.urls import path
from .views import Clients, ExchangeToken, Merchants, StaffUsers, UserDetailView


urlpatterns = [
    path("exchange-token/", ExchangeToken.as_view(), name="exchange-token"),
    path("current-user/", UserDetailView.as_view(), name="user_detail"),
    path("merchants/", Merchants.as_view(), name="merchants"),
    path("merchants/<uuid:pk>/", Merchants.as_view(), name="merchants-detail"),
    path("staff-users/", StaffUsers.as_view(), name="staff-users"),
    path("staff-users/<uuid:pk>/", StaffUsers.as_view(), name="staff-users-detail"),
    path("clients/", Clients.as_view(), name="clients"),
    path("clients/<uuid:pk>/", StaffUsers.as_view(), name="clients-detail"),
]
