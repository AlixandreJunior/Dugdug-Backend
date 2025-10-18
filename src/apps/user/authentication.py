from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.http import HttpRequest

User = get_user_model()


class EmailAndCPFBackend:
    def authenticate(
        self,
        request: HttpRequest,
        identifier: str,
        password: str,
        **kwargs: object,
    ) -> AbstractUser | None:
        try:
            user = User.objects.get(Q(email=identifier) | Q(cpf=identifier))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id: int | str) -> AbstractUser | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user: AbstractUser) -> bool:
        return user.is_active
