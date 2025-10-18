from typing import Self

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from utils.validate import validate_cpf, validate_phone


class User(AbstractUser):
    class Meta:
        app_label = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    cpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf])
    phone = models.CharField(max_length=15, unique=True, validators=[validate_phone])

    objects = UserManager[Self]()

    groups = None
    user_permissions = None

    def __str__(self) -> str:
        return self.username
