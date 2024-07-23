from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from oauth2_provider import urls as oauth2_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("o/", include(oauth2_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
