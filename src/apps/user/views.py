from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from utils.base_view import BaseUserView


class UserListView(BaseUserView, generics.ListAPIView):
    pass


class UserDetailView(BaseUserView, generics.RetrieveAPIView):
    pass


class UserUpdateView(BaseUserView, generics.UpdateAPIView):
    def update(self, request: Request, *args: object, **kwargs: object) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response("Usuario excluido com sucesso.", status=status.HTTP_200_OK)


class UserDeleteView(BaseUserView, generics.DestroyAPIView):
    def destroy(self, request: Request, *args: object, **kwargs: object) -> Response:
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            "Usuario excluido com sucesso.", status=status.HTTP_204_NO_CONTENT
        )


class UserCreateView(BaseUserView, generics.CreateAPIView):
    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response("Usuario criado com sucesso.", status=status.HTTP_201_CREATED)
