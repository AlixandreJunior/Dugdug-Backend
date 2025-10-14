from typing import ClassVar

from rest_framework import serializers  # type: ignore

from apps.plan.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields: ClassVar[list[str]] = ["id", "name", "price", "duration_days"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields: ClassVar[list[str]] = [
            "id",
            "costumer",
            "plan",
            "start_date",
            "end_date",
            "is_active",
            "payment_method",
        ]
