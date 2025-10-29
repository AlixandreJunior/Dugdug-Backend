from django.contrib.auth.models import BaseUserManager

from apps.user.models import User


class UserManager(BaseUserManager[User]):
    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        if not username:
            msg = "O campo 'username' é obrigatório."
            raise ValueError(msg) from None
        if not email:
            msg = "O campo 'email' é obrigatório."
            raise ValueError(msg)

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("cpf"):
            raise ValueError("O campo 'cpf' é obrigatório para superusuário.")
        if not extra_fields.get("phone"):
            raise ValueError("O campo 'phone' é obrigatório para superusuário.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)
