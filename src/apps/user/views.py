from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.serializer import LoginUserSerializer, LogoutUserSerializer
from utils.base_view import BaseUserView


class UserListView(BaseUserView, generics.ListAPIView):
    pass


class UserDetailView(BaseUserView, generics.RetrieveAPIView):
    def get_object(self) -> User:
        username: str = self.kwargs.get("username")
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist as e:
            message = "Diário não encontrado."
            raise NotFound(message) from e


class UserUpdateView(BaseUserView, generics.UpdateAPIView):
    def update(self, request: Request, *args: object, **kwargs: object) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response("Usuário atualizado com sucesso.", status=status.HTTP_200_OK)


class UserDeleteView(BaseUserView, generics.DestroyAPIView):
    def destroy(self, request: Request, *args: object, **kwargs: object) -> Response:
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            "Usuário excluído com sucesso.", status=status.HTTP_204_NO_CONTENT
        )


class UserCreateView(BaseUserView, generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response("Usuário criado com sucesso.", status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(
        self, request: Request, *arg: object, **kwargs: dict[object, object]
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(
        self, request: Request, *args: object, **kwargs: dict[object, object]
    ) -> Response:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Token de atualização não fornecido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response(
                {"access": access_token, "detail": "Token atualizado com sucesso."},
                status=status.HTTP_200_OK,
            )

        except TokenError as e:
            return Response(
                {"detail": f"Token inválido: {e!s}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(
        self, request: Request, *args: object, **kwargs: dict[object, object]
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            if hasattr(token, "blacklist"):
                token.blacklist()
            return Response(
                {"detail": "Logout realizado com sucesso."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {"error": "Token inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
