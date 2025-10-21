from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.user.models import User
from utils.validate import validate_cpf, validate_phone


class UserSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
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


class LoginUserSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        user = authenticate(identifier=attrs["identifier"], password=attrs["password"])

        if user:
            attrs["user"] = user
            return attrs

        raise serializers.ValidationError({"detail": "Usuário ou senha incorretos!!"})


class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        refresh = attrs.get("refresh")

        if not refresh:
            msg = "O campo 'refresh' é obrigatório."
            raise serializers.ValidationError(msg)
        return attrs
