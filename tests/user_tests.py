from typing import cast

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.user.models import User
from utils.tests_mixins import UserMixin


class UserViewTests(APITestCase, UserMixin):
    def setUp(self):
        self.user = self.make_user_auth(
            username="user1",
            email="user1@email.com",
            password="SenhaForte321.",  # noqa: S106
        )
        self.client.force_authenticate(user=self.user)

        self.user_data = {
            "username": "newuser",
            "email": "newuser@email.com",
            "phone": "(12)34567-8901",
            "cpf": "04967659063",
            "password": "SenhaForte321.",
        }

        self.create_url = reverse("user:create")
        self.list_url = reverse("user:list")
        self.detail_url = reverse("user:detail", args=[self.user.username])
        self.update_url = reverse("user:update")
        self.delete_url = reverse("user:delete")

    # -------------------------------
    # DETAIL VIEW
    # -------------------------------
    def test_detail_json_fields(self):
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "cpf",
            "phone",
        ]
        for field in expected_fields:
            self.assertIn(field, response.json())

    def test_detail_view_success(self):
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], self.user.username)

    def test_detail_view_not_found(self):
        url = reverse("user:detail", args=["inexistente"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------
    # CREATE VIEW
    # -------------------------------
    def test_create_view_success(self):
        self.client.logout()
        response = self.client.post(self.create_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, "Usuário criado com sucesso.")

    def test_create_missing_fields(self):
        self.client.logout()
        data = {"username": "", "email": "", "cpf": "", "phone": "", "password": ""}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in data:
            self.assertIn("This field may not be blank.", response.json()[field])

    def test_create_invalid_cpf(self):
        self.client.logout()
        data = {**self.user_data, "cpf": "12345678900"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "CPF inválido: dígitos verificadores incorretos.",
            response.json().get("cpf", ""),
        )

    def test_create_invalid_email(self):
        self.client.logout()
        data = {**self.user_data, "email": "emailinvalido"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter a valid email address.", response.json().get("email", ""))

    def test_create_duplicate_username(self):
        self.client.logout()
        self.make_user_not_auth(**self.user_data)
        response = self.client.post(self.create_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "a user with that username already exists.",
            str(response.json().get("username")).lower(),
        )
        self.assertIn(
            "user with this email already exists.",
            str(response.json().get("email")).lower(),
        )
        self.assertIn(
            "user with this cpf already exists.",
            str(response.json().get("cpf")).lower(),
        )
        self.assertIn(
            "user with this phone already exists.",
            str(response.json().get("phone")).lower(),
        )

    def test_create_duplicate_email(self):
        self.client.logout()
        self.make_user_not_auth(**self.user_data)
        data = {**self.user_data, "username": "otheruser"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "user with this email already exists", str(response.json()).lower()
        )

    def test_create_duplicate_email_case_insensitive(self):
        self.client.logout()
        self.make_user_not_auth(**self.user_data)
        data = {
            **self.user_data,
            "email": self.user_data["email"].upper(),
            "username": "otheruser",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "user with this email already exists", str(response.json()).lower()
        )

    def test_create_with_extra_field(self):
        self.client.logout()
        data = cast("dict[str, object]", {**self.user_data, "is_staff": True})
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_staff", response.json())

    def test_password_too_short(self):
        data = {**self.user_data, "password": "S1a!"}  # muito curta
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())
        self.assertIn(
            "A senha deve ter no mínimo 8 caracteres.",
            response.json().get("password"),
        )

    def test_password_missing_number(self):
        data = {**self.user_data, "password": "SenhaForte!"}  # sem número
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())
        self.assertIn(
            "A senha deve conter ao menos um número.",
            response.json().get("password"),
        )

    def test_password_missing_uppercase(self):
        data = {**self.user_data, "password": "senha123!"}  # sem maiúscula
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())
        self.assertIn(
            "A senha deve conter ao menos uma letra maiúscula.",
            response.json().get("password"),
        )

    def test_password_missing_lowercase(self):
        data = {**self.user_data, "password": "SENHA123!"}  # sem minúscula
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())
        self.assertIn(
            "A senha deve conter ao menos uma letra minúscula.",
            response.json().get("password"),
        )

    def test_password_missing_special_character(self):
        data = {**self.user_data, "password": "Senha1234"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "A senha deve conter ao menos um caractere especial.",
            response.json().get("password"),
        )

    def test_password_is_hashed_on_create(self):
        self.client.logout()
        response = self.client.post(self.create_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username=self.user_data["username"])
        self.assertNotEqual(user.password, self.user_data["password"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    # -------------------------W------
    # LIST VIEW
    # -------------------------------

    def test_list_json_fields(self):
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        if response.json():
            expected_fields = [
                "id",
                "username",
                "first_name",
                "last_name",
                "email",
                "cpf",
                "phone",
            ]
            for field in expected_fields:
                self.assertIn(field, response.json()[0])

    def test_list_view_success(self):
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_list_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------
    # UPDATE VIEW
    # -------------------------------
    def test_update_view_success(self):
        data = {"email": "novoemail@email.com"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Usuário atualizado com sucesso.")

    def test_partial_update_multiple_fields(self):
        data = {"email": "novo@email.com", "phone": "(12)99999-9999"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data["email"])
        self.assertEqual(self.user.phone, data["phone"])

    def test_update_password_rehash(self):
        data = {"password": "NovaSenha321!"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data["password"]))

    def test_update_invalid_email(self):
        data = {"email": "emailinvalido"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter a valid email address", str(response.json()["email"]))

    def test_update_invalid_cpf(self):
        data = {"cpf": "12345678900"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CPF inválido", str(response.json()["cpf"]))

    def test_update_unauthenticated(self):
        self.client.logout()
        response = self.client.patch(self.update_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------
    # DELETE VIEW
    # -------------------------------
    def test_delete_view_success(self):
        response = self.client.delete(self.delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, "Usuário excluído com sucesso.")
        self.assertFalse(User.objects.filter(id=self.user.pk).exists())

    def test_delete_unauthenticated(self):
        self.client.logout()
        response = self.client.delete(self.delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
