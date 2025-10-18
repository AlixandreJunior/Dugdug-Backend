from backend.src.apps.user.serializer import LoginUserSerializer
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

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


class LoginView(generics.CreateAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(
        self, request: Request, *arg: object, **kwargs: dict[object, object]
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        print(serializer.is_valid())
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


class RefreshView(generics.GenericAPIView):
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
    permission_classes = (permissions.IsAuthenticated,)

    def post(
        self, request: Request, *args: object, **kwargs: dict[object, object]
    ) -> Response:
        return Response(
            {"detail": "Logout realizado com sucesso."}, status=status.HTTP_200_OK
        )
