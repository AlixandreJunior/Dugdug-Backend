from typing import override

from django.db.models.query import QuerySet
from rest_framework import permissions
from rest_framework.generics import GenericAPIView

from apps.affiliate.models import Affiliate, Payout
from apps.affiliate.serializer import AffiliateSerializer, PayoutSerializer
from apps.plan.models import Plan, Subscription
from apps.plan.serializer import PlanSerializer, SubscriptionSerializer
from apps.user.models import User
from apps.user.serializer import UserSerializer


class BaseUserView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    model = User

    @override
    def get_queryset(self) -> QuerySet[User]:
        return self.model.objects.all()

    @override
    def get_object(self) -> User:
        user_id = self.request.user.pk
        return self.model.objects.get(id=user_id)


class BasePlanView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PlanSerializer
    model = Plan

    @override
    def get_queryset(self) -> QuerySet["Plan"]:
        return self.model.objects.all()

    def get_object(self) -> Plan:
        plan_name = self.kwargs.get("name")
        return self.model.objects.get(name=plan_name)


class BaseSubscriptionView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    model = Subscription


class BaseAffiliateView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AffiliateSerializer
    model = Affiliate


class BasePayoutView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PayoutSerializer
    model = Payout
