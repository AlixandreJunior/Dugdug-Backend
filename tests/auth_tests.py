from datetime import timedelta
from typing import cast

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from utils.user_mixin import UserMixin


class AuthTest(APITestCase, UserMixin):
    def setUp(self):
        self.login_api = reverse("login")
        self.logout_api = reverse("logout")
        self.refresh_api = reverse("refresh")

        self.user_data = {
            "username": "testuser",
            "email": "testuser@email.com",
            "cpf": "04967659063",
            "password": "SenhaForte321.",
        }

    # region LOGIN TESTS
    def test_login_with_email_should_return_tokens(self) -> None:
        self.user = self.make_user_not_auth(**self.user_data)
        valid_data = {"identifier": "testuser@email.com", "password": "SenhaForte321."}

        response = self.client.post(self.login_api, data=valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_with_cpf_should_return_tokens(self) -> None:
        self.user = self.make_user_not_auth(**self.user_data)
        valid_data = {"identifier": "04967659063", "password": "SenhaForte321."}

        response = self.client.post(self.login_api, data=valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_with_invalid_cpf_should_return_error(self) -> None:
        self.user = self.make_user_not_auth(**self.user_data)
        invalid_data = {"identifier": "04967659065", "password": "SenhaForte321."}

        response = self.client.post(self.login_api, data=invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuário ou senha incorretos!!", response.json().get("detail"))

    def test_login_with_malformed_cpf_should_return_error(self) -> None:
        invalid_cpf = "123456"
        response = self.client.post(
            self.login_api,
            data={"identifier": invalid_cpf, "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuário ou senha incorretos!!", response.json().get("detail"))

    def test_login_with_wrong_credentials_should_fail(self) -> None:
        invalid_data = {"identifier": "wrong@email.com", "password": "wrongpassword"}
        response = self.client.post(self.login_api, data=invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuário ou senha incorretos!!", response.json().get("detail"))

    def test_login_with_inactive_user_should_fail(self) -> None:
        user = self.make_user_not_auth(**self.user_data)
        user.is_active = False
        user.save()

        response = self.client.post(
            self.login_api,
            data={
                "identifier": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuário ou senha incorretos!!", response.json().get("detail"))

    def test_login_with_empty_fields_should_return_validation_error(self) -> None:
        self.make_user_not_auth(**self.user_data)
        response = self.client.post(
            self.login_api, data={"identifier": "", "password": ""}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", response.json().get("identifier"))
        self.assertIn("This field may not be blank.", response.json().get("password"))

    # endregion

    # region LOGOUT TESTS
    def test_logout_with_valid_token_should_succeed(self) -> None:
        user = self.make_user_auth(**self.user_data)
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")

        response = self.client.post(
            self.logout_api, data={"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertIn("Logout realizado com sucesso.", response.json().get("detail"))

    def test_logout_without_token_should_fail(self) -> None:
        response = self.client.post(self.logout_api, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided.",
            response.json().get("detail"),
        )

    def test_logout_with_expired_token_should_return_unauthorized(self) -> None:
        self.user = self.make_user_not_auth(**self.user_data)
        refresh = RefreshToken.for_user(self.user)
        expired_access = AccessToken.for_user(self.user)
        expired_access.set_exp(lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_access}")

        response = self.client.post(
            self.logout_api, data={"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Token is expired", response.json().get("messages")[0].get("message")
        )

    # endregion

    # region REFRESH TESTS
    def test_refresh_with_valid_token_should_issue_new_access_token(self) -> None:
        user = self.make_user_auth(**self.user_data)
        refresh = RefreshToken.for_user(user)

        response = self.client.post(
            self.refresh_api, data={"refresh": str(refresh)}, format="json"
        )

        data = cast("dict[str, object]", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", data)
        self.assertIn("Token atualizado com sucesso.", response.json().get("detail"))

    def test_refresh_with_invalid_token_should_return_error(self) -> None:
        response = self.client.post(
            self.refresh_api, data={"refresh": "tokeninvalido"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token inválido: Token is invalid", response.json().get("detail"))

    def test_refresh_with_blacklisted_token_should_return_unauthorized(self) -> None:
        self.user = self.make_user_not_auth(**self.user_data)
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()

        response = self.client.post(
            self.refresh_api, data={"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Token inválido: Token is blacklisted", response.json().get("detail")
        )

    # endregion
