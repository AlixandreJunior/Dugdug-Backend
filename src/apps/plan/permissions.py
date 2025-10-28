from typing import TYPE_CHECKING, cast, override

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

if TYPE_CHECKING:
    from apps.user.models import User


class IsAdminOrReadOnly(BasePermission):
    @override
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        user = cast("User", request.user)
        return user and user.is_staff
