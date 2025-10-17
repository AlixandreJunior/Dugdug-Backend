from typing import ClassVar

from django.db.models import Model
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rest_framework.serializers import Serializer


class BaseView[T: Model](GenericAPIView):
    permission_classes: ClassVar[tuple[type[BasePermission]]]
    serializer_class: ClassVar[type[Serializer]]
    model: type[T]
