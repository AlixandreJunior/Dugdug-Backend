from rest_framework import serializers

from apps.plan.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Plan
        fields = ("id", "name", "price", "duration_days")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Subscription
        fields = (
            "id",
            "costumer",
            "plan",
            "start_date",
            "end_date",
            "is_active",
            "payment_method",
        )
