from django.contrib.auth.models import UserManager as UserManagerType

from .models import User


class UserManager(UserManagerType[User]):
    pass
