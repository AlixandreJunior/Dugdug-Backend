from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

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
        )

    def validate_pix_key(self, key: str) -> str:
        key_type = self.initial_data.get("pix_key_type")
        validate_pix_key(key, key_type)

        return key

    def validate_code(self, code: str) -> str:
        if code and Affiliate.objects.filter(code=code).exists():
            msg = "Este código de afiliado já está em uso."
            raise serializers.ValidationError(msg)
        return code


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
            "pix_key",
            "requested_at",
            "paid_at",
            "amount",
        )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        user = self.context["request"].user

        if user.is_staff or user.is_superuser:
            return attrs

        try:
            affiliate = Affiliate.objects.get(user=user)
        except Affiliate.DoesNotExist:
            error_msg = "Você precisa ser um afiliado para solicitar um saque."
            raise PermissionDenied(error_msg) from None

        commission_balance = affiliate.commission_balance

        if commission_balance < 50:
            error_msg = (
                f"Saldo insuficiente para saque. Total acumulado: R$ {commission_balance:.2f}. "
                "É necessário ter pelo menos R$ 50,00."
            )
            raise serializers.ValidationError(error_msg)

        # Preenche o amount com todo o commission_balance
        attrs["affiliate"] = affiliate
        attrs["pix_key"] = affiliate.pix_key
        attrs["amount"] = commission_balance

        # Zera o commission_balance do afiliado
        affiliate.commission_balance = Decimal(0)
        affiliate.save(update_fields=["commission_balance"])

        return attrs
