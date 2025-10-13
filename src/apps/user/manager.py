from django.contrib.auth.models import BaseUserManager

from .models import User


class UserManager(BaseUserManager[User]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> User:
        if not email:
            error_message = "O e-mail é obrigatório!"
            raise ValueError(error_message)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)
