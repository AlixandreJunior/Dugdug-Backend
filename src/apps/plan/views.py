from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models.query import QuerySet
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.affiliate.models import Affiliate
from apps.plan.models import Plan, Subscription
from apps.plan.permissions import IsAdminOrReadOnly
from utils.base_view import BasePlanView, BaseSubscriptionView


class PlanListView(BasePlanView, generics.ListAPIView):
    pass


class PlanCreateView(BasePlanView, generics.CreateAPIView):
    permission_classes = (IsAdminOrReadOnly,)


class PlanDetailView(BasePlanView, generics.RetrieveAPIView):
    pass


class PlanUpdateView(BasePlanView, generics.UpdateAPIView):
    permission_classes = (IsAdminOrReadOnly,)


class PlanDeleteView(BasePlanView, generics.DestroyAPIView):
    permission_classes = (IsAdminOrReadOnly,)


class SubscriptionListView(generics.ListAPIView):
    def get_queryset(self) -> QuerySet[Subscription]:
        user = self.request.user
        return Subscription.objects.filter(costumer=user).order_by("-start_date")


class SubscriptionCreateView(BaseSubscriptionView, generics.CreateAPIView):
    @transaction.atomic
    def perform_create(self, serializer: BaseSerializer) -> None:
        user = self.request.user
        plan_id = self.request.data.get("plan_id")
        affiliate_code = self.request.data.get("affiliate_code")
        payment_method = self.request.data.get("payment_method", "pix")

        try:
            plan = Plan.objects.get(pk=plan_id)
        except Plan.DoesNotExist:
            msg = {"plan_id": "Plano inválido."}
            raise serializers.ValidationError(msg) from None

        start_date = timezone.now()
        end_date = start_date + timedelta(days=plan.duration_days)

        affiliate = None
        if affiliate_code:
            try:
                affiliate = Affiliate.objects.get(code=affiliate_code)
            except Affiliate.DoesNotExist:
                msg = {"affiliate_code": "Código de afiliado inválido."}
                raise serializers.ValidationError(msg) from None

            commission = plan.price * Decimal("0.10")
            affiliate.commission_balance += commission
            affiliate.total_earned += commission
            affiliate.save(update_fields=["commission_balance", "total_earned"])

        serializer.save(
            costumer=user,
            plan=plan,
            affiliate=affiliate,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            payment_method=payment_method,
        )


class SubscriptionDetailView(BaseSubscriptionView, generics.RetrieveAPIView):
    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(costumer=self.request.user)


class SubscriptionCancelView(BaseSubscriptionView, generics.UpdateAPIView):
    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(costumer=self.request.user)

    def update(
        self, request: Request, *args: object, **kwargs: dict[str, object]
    ) -> Response:
        instance = self.get_object()

        if not instance.is_active:
            return Response(
                {"error": "A assinatura já está cancelada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(
            {"message": "Assinatura cancelada com sucesso."},
            status=status.HTTP_200_OK,
        )


class SubscriptionAdminListView(BaseSubscriptionView, generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.select_related(
            "costumer", "plan", "affiliate"
        ).order_by("-start_date")
