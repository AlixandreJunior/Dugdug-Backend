from django.urls import URLPattern, URLResolver, path

from apps.user.views import (
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)

app_name = "user"

urlpatterns: list[URLPattern | URLResolver] = [
    path("detail/<str:username>/", UserDetailView.as_view(), name="detail"),
    path("create/", UserCreateView.as_view(), name="create"),
    path("list/", UserListView.as_view(), name="list"),
    path("delete/", UserDeleteView.as_view(), name="delete"),
    path("update/", UserUpdateView.as_view(), name="update"),
]
