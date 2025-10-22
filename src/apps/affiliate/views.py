from typing import TYPE_CHECKING, cast, override

from django.db.models.query import QuerySet
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import BaseSerializer

from apps.affiliate.models import Affiliate, Payout
from apps.affiliate.serializer import AffiliateSerializer, PayoutSerializer

if TYPE_CHECKING:
    from apps.user.models import User


class AffiliateCreateView(generics.CreateAPIView):
    serializer_class = AffiliateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @override
    def perform_create(self, serializer: BaseSerializer) -> None:
        user = self.request.user

        if Affiliate.objects.filter(user=user).exists():
            msg = "Você já possui um registro de afiliado."
            raise PermissionDenied(msg)

        serializer.save(user=user)


class AffiliateListView(generics.ListAPIView):
    serializer_class = AffiliateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Affiliate]:
        user = cast("User", self.request.user)

        if user.is_staff or user.is_superuser:
            return Affiliate.objects.select_related("user").all()
        return Affiliate.objects.filter(user=user)


class AffiliateDetailView(generics.RetrieveAPIView):
    """
    Exibe detalhes de um afiliado específico.
    """

    serializer_class = AffiliateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Affiliate]:
        user = cast("User", self.request.user)

        if user.is_staff or user.is_superuser:
            return Affiliate.objects.select_related("user").all()
        return Affiliate.objects.filter(user=user)


class AffiliateUpdateView(generics.UpdateAPIView):
    """
    Atualiza dados do afiliado autenticado (ex: chave Pix).
    """

    serializer_class = AffiliateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Affiliate]:
        user = cast("User", self.request.user)
        if user.is_staff or user.is_superuser:
            return Affiliate.objects.select_related("user").all()
        return Affiliate.objects.filter(user=user)


class AffiliateDeleteView(generics.DestroyAPIView):
    """
    Exclui o afiliado autenticado.
    """

    serializer_class = AffiliateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Affiliate]:
        user = cast("User", self.request.user)
        if user.is_staff or user.is_superuser:
            return Affiliate.objects.select_related("user").all()
        return Affiliate.objects.filter(user=user)


class PayoutCreateView(generics.CreateAPIView):
    """
    Cria uma nova solicitação de pagamento (payout) para o afiliado autenticado.
    """

    serializer_class = PayoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer: BaseSerializer) -> None:
        user = self.request.user
        try:
            affiliate = Affiliate.objects.get(user=user)
        except Affiliate.DoesNotExist as e:
            msg = "Você precisa ser um afiliado para solicitar um saque."
            raise PermissionDenied(msg) from e

        serializer.save(affiliate=affiliate, pix_key=affiliate.pix_key)


class PayoutListView(generics.ListAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Payout]:
        user = cast("User", self.request.user)
        if user.is_staff or user.is_superuser:
            return Payout.objects.select_related("affiliate", "affiliate__user").all()
        return Payout.objects.filter(affiliate__user=user)


class PayoutDetailView(generics.RetrieveAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Payout]:
        user = cast("User", self.request.user)
        if user.is_staff or user.is_superuser:
            return Payout.objects.select_related("affiliate", "affiliate__user").all()
        return Payout.objects.filter(affiliate__user=user)


class PayoutUpdateView(generics.UpdateAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self) -> QuerySet[Payout]:
        return Payout.objects.select_related("affiliate", "affiliate__user").all()


class PayoutDeleteView(generics.DestroyAPIView):
    serializer_class = PayoutSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self) -> QuerySet[Payout]:
        return Payout.objects.select_related("affiliate", "affiliate__user").all()
