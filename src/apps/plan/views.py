from rest_framework.permissions import AllowAny, IsAuthenticated  # type: ignore

from apps.plan.models import Plan, Subscription
from apps.plan.serializer import SubscriptionSerializer
from apps.user.serializer import UserSerializer
from utils.base_view import BaseView


class BasePlanView(BaseView[Plan]):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    model = Plan


class BaseSubscriptionView(BaseView[Subscription]):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    model = Subscription
