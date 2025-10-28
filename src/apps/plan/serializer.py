from datetime import timedelta
from decimal import Decimal
from typing import cast

from django.utils import timezone
from rest_framework import serializers

from apps.affiliate.models import Affiliate
from apps.plan.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Plan
        fields = ("id", "name", "price", "duration_days")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    plan_price = serializers.DecimalField(
        source="plan.price", read_only=True, max_digits=8, decimal_places=2
    )
    affiliate_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:  # type: ignore
        model = Subscription
        fields = (
            "id",
            "costumer",
            "plan",
            "plan_name",
            "plan_price",
            "affiliate",
            "affiliate_code",
            "start_date",
            "end_date",
            "is_active",
            "payment_method",
        )
        read_only_fields = (
            "id",
            "costumer",
            "affiliate",
            "start_date",
            "end_date",
            "is_active",
        )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        plan = attrs.get("plan")
        user = self.context["request"].user

        if Subscription.objects.filter(costumer=user, is_active=True).exists():
            msg = "Você já possui uma assinatura ativa."
            raise serializers.ValidationError(msg)

        if not plan:
            msg = "É necessário escolher um plano válido."
            raise serializers.ValidationError(msg)

        return attrs

    def create(self, validated_data: dict[str, object]) -> Subscription:
        user = self.context["request"].user
        affiliate_code = validated_data.pop("affiliate_code", None)
        plan = cast("Plan", validated_data["plan"])

        start_date = timezone.now()
        end_date = start_date + timedelta(days=plan.duration_days)

        affiliate = None
        if affiliate_code:
            affiliate = Affiliate.objects.filter(code=affiliate_code).first()

        subscription = Subscription.objects.create(
            costumer=user,
            plan=plan,
            affiliate=affiliate,
            start_date=start_date,
            end_date=end_date,
            payment_method=validated_data.get("payment_method", "pix"),
        )

        if affiliate:
            commission = plan.price * Decimal("0.10")
            affiliate.commission_balance += commission
            affiliate.total_earned += commission
            affiliate.save(update_fields=["commission_balance", "total_earned"])

        return subscription
