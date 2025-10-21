from django.contrib import admin
from django.urls import URLPattern, URLResolver, path

from apps.user.views import LoginView, LogoutView, RefreshView

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
]
