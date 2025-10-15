from django.db.models.query import QuerySet
from rest_framework import permissions  # type: ignore

from apps.user.models import User
from apps.user.serializer import UserSerializer
from utils.base_view import BaseView


class BaseUserView(BaseView[User]):
    serializer_class = UserSerializer
    model = User

    def get_object(self, user_id: int) -> User:  # type: ignore[override]
        return self.model.objects.get(id=user_id)

    def get_queryset(self) -> QuerySet[User]:  # type: ignore[override]
        return self.model.objects.all()

    def get_permissions(self) -> list[permissions.BasePermission]:  # type: ignore[override]
        if self.request.method in ["GET,DELETE,PATCH,PUT"]:
            return [permissions.IsAuthenticated()]
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return super().get_permissions()
