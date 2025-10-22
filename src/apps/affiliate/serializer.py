from rest_framework import serializers  # type: ignore

from apps.affiliate.models import Affiliate, Payout


class AffiliateSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Affiliate
        fields = (
            "id",
            "user",
            "code",
            "commission_balance",
            "total_earned",
            "pix_key",
            "pix_key_type",
            "joined_at",
        )
        read_only_fields = (
            "id",
            "commission_balance",
            "total_earned",
            "joined_at",
            "code",
        )


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Payout
        fields = (
            "id",
            "affiliate",
            "amount",
            "pix_key",
            "status",
            "requested_at",
            "paid_at",
            "notes",
        )
        read_only_fields = (
            "id",
            "status",
            "requested_at",
            "paid_at",
        )
