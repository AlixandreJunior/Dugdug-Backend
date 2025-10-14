from typing import ClassVar

from rest_framework import serializers  # type: ignore

from apps.affiliate.models import Affiliate, Payout


class AffiliateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Affiliate
        fields: ClassVar[list[str]] = [
            "id",
            "user",
            "code",
            "commission_balance",
            "total_earned",
            "pix_key",
            "pix_key_type",
            "joined_at",
        ]
        read_only_fields: ClassVar[list[str]] = [
            "id",
            "commission_balance",
            "total_earned",
            "joined_at",
            "code",
        ]


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields: ClassVar[list[str]] = [
            "id",
            "affiliate",
            "amount",
            "pix_key",
            "status",
            "requested_at",
            "paid_at",
            "notes",
        ]
        read_only_fields: ClassVar[list[str]] = [
            "id",
            "status",
            "requested_at",
            "paid_at",
        ]
