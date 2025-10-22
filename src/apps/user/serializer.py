from typing import cast

from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.user.models import User
from utils.validate import (
    validate_cpf,
    validate_email,
    validate_password,
    validate_phone,
)


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
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}  # noqa

    def validate_cpf(self, cpf: str) -> str:
        validate_cpf(cpf)
        return cpf

    def validate_phone(self, phone: str) -> str:
        validate_phone(phone)
        return phone

    def validate_password(self, password: str) -> str:
        validate_password(password)
        return password

    def validate_email(self, email: str) -> str:
        email = email.lower().strip()
        validate_email(email)
        return email

    def to_internal_value(self, data: dict[object, object]) -> None:
        allowed_fields = set(self.fields.keys())
        received_fields = set(data.keys())

        extra_fields = received_fields - allowed_fields
        if extra_fields:
            raise serializers.ValidationError(
                {str(field): "Campo não permitido." for field in extra_fields}
            )

        return super().to_internal_value(data)

    def create(self, validated_data: dict[str, object]) -> User:
        password = cast("str", validated_data.pop("password"))
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: User, validated_data: dict[str, str]) -> User:
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


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
