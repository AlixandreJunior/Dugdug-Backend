from rest_framework import serializers

from apps.user.models import User
from utils.validate import validate_cpf, validate_phone


class UserSerializer(serializers.ModelSerializer):
    class Meta(serializers.ModelSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "cpf",
            "phone",
        )

    def validate_cpf(self, cpf: str) -> str:
        validate_cpf(cpf)
        return cpf

    def validate_phone(self, phone: str) -> str:
        validate_phone(phone)
        return phone
