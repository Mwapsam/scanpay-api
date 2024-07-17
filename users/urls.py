from django.urls import path

from .views import CustomTokenObtainPairView, UserDetailView

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("current-user/", UserDetailView.as_view(), name="user_detail"),
]
