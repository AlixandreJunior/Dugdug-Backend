from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from utils.validate import validate_cpf, validate_phone


class User(AbstractUser):
    class Meta:
        app_label = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    email = models.EmailField(max_length=150, unique=True)
    cpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf])
    phone = models.CharField(max_length=15, unique=True, validators=[validate_phone])
    password = models.CharField(max_length=128, null=False)

    objects = UserManager["User"]()

    groups = None
    user_permissions = None

    def __str__(self) -> str:
        return self.username
