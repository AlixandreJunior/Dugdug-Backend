from typing import ClassVar

from rest_framework import serializers

from apps.user.models import User
from utils.validate import validate_cpf, validate_phone

type Fields = list[str]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: ClassVar[Fields] = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "cpf",
            "phone",
        ]

    def validate_cpf(self, cpf: str) -> str:
        validate_cpf(cpf)
        return cpf

    def validate_phone(self, phone: str) -> str:
        validate_phone(phone)
        return phone
