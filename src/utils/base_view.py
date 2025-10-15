from abc import abstractmethod
from typing import ClassVar, Generic, TypeVar

from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework.generics import GenericAPIView  # type: ignore
from rest_framework.permissions import BasePermission, IsAuthenticated  # type: ignore
from rest_framework.serializers import Serializer  # type: ignore

T = TypeVar("T", bound=Model)


class BaseView(GenericAPIView, Generic[T]):
    permission_classes: ClassVar[list[type[BasePermission]]] = [IsAuthenticated]
    serializer_class: ClassVar[type[Serializer]]
    model: type[T]

    @abstractmethod
    def get_object(self) -> T:  # type: ignore[override]
        pass

    @abstractmethod
    def get_queryset(self) -> QuerySet[T]:  # type: ignore[override]
        pass

    def get_permissions(self) -> list[BasePermission]:
        return [perm() for perm in self.permission_classes]
