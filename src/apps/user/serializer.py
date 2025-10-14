from typing import ClassVar

from rest_framework import serializers  # type: ignore

from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: ClassVar[list[str]] = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "cpf",
            "phone",
        ]
