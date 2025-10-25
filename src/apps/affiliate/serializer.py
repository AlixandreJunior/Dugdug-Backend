from rest_framework import serializers  # type: ignore

from apps.affiliate.models import Affiliate, Payout
from utils.validate import validate_pix_key


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
            "user",
            "commission_balance",
            "total_earned",
            "joined_at",
            "code",
        )

    def validate_pix_key(self, key: str) -> str:
        key_type = self.initial_data.get("pix_key_type")
        validate_pix_key(key, key_type)

        return key


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
            "affiliate",
            "id",
            "requested_at",
            "paid_at",
        )
