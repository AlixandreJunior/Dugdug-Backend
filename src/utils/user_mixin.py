from __future__ import annotations

import os
from typing import TYPE_CHECKING

from apps.user import models

if TYPE_CHECKING:
    from rest_framework.test import APIClient


class UserMixin:
    client: APIClient

    def make_user_auth(
        self,
        first_name: str = "User",
        last_name: str = "Auth",
        username: str = "auth_user",
        email: str = "auth_user@email.com",
        cpf: str = "123.456.789-09",
        phone: str = "(11) 91234-5678",
        password: str = "SenhaMuitoSegura123",  # noqa: S107
    ) -> models.User:
        password = password or os.getenv("TEST_USER_PASSWORD", "SenhaMuitoSegura123")

        user = models.User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cpf=cpf,
            phone=phone,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        self.client.force_authenticate(user)
        return user

    def make_user_not_auth(
        self,
        first_name: str = "User",
        last_name: str = "NotAuth",
        username: str = "not_auth_user",
        email: str = "not_auth_user@email.com",
        cpf: str = "987.654.321-00",
        phone: str = "(11) 97654-3210",
        password: str = "SenhaMuitoSegura321",  # noqa: S107
    ) -> models.User:
        user = models.User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cpf=cpf,
            phone=phone,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        return user

    def make_user_not_active(
        self,
        first_name: str = "User",
        last_name: str = "Inactive",
        username: str = "inactive_user",
        email: str = "inactive_user@email.com",
        cpf: str = "321.654.987-00",
        phone: str = "(11) 99876-5432",
        password: str = "SenhaMuitoSegura213",  # noqa: S107
    ) -> models.User:
        user = models.User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cpf=cpf,
            phone=phone,
            is_active=False,
        )
        user.set_password(password)
        user.save()
        return user
