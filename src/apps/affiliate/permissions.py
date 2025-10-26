from typing import TYPE_CHECKING, cast

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.affiliate.models import Affiliate

if TYPE_CHECKING:
    from apps.user.models import User


class IsAffiliateOrAdmin(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        # Staff ou superuser sempre permitido
        if user.is_staff or user.is_superuser:
            return True

        # Verifica se é afiliado
        return Affiliate.objects.filter(user=user).exists()
