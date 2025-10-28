from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.affiliate.models import Affiliate
from utils.tests_mixins import AffiliateMixin


# ========================
# TESTES DE AFFILIATE
# ========================
class AffiliateViewTests(APITestCase, AffiliateMixin):
    def setUp(self):
        self.client = APIClient()
        # Usuários
        self.user = self.make_user_auth(username="user1", email="user1@email.com")
        self.staff = self.make_staff_user(
            username="staff",
            email="staff@email.com",
            phone="(11)99999-9999",
            cpf="53184468097",
        )
        self.superuser = self.make_superuser(
            username="admin",
            email="admin@email.com",
            phone="(11)88888-8888",
            cpf="09339479092",
        )

        # Affiliate existente
        self.affiliate = self.make_affiliate(user=self.user)

        # URLs
        self.create_url = reverse("affiliate-create")
        self.list_url = reverse("affiliate-list")
        self.detail_url = reverse("affiliate-detail", args=[self.affiliate.pk])
        self.update_url = reverse("affiliate-update", args=[self.affiliate.pk])
        self.delete_url = reverse("affiliate-delete", args=[self.affiliate.pk])

    # ---------- CRIAÇÃO ----------

    def test_create_affiliate_already_exists(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "53184468097", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_affiliate_cpf_valid(self):
        data = {"pix_key": "05075710298", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_affiliate_cnpj_valid(self):
        data = {"pix_key": "12.345.678/0001-95", "pix_key_type": "cnpj"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_affiliate_email_valid(self):
        data = {"pix_key": "test@example.com", "pix_key_type": "email"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_affiliate_phone_valid(self):
        data = {"pix_key": "(11)99999-9999", "pix_key_type": "phone"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_affiliate_random_valid(self):
        data = {
            "pix_key": "6d68a68e-1434-43d3-b4cf-952c93b4d8f7",
            "pix_key_type": "random",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_affiliate_auto_code(self):
        """Se o código não for enviado, deve ser gerado automaticamente."""
        data = {"pix_key": "98765432100", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response.json()["code"], r"^AFF[A-F0-9]{8}$")

    def test_create_affiliate_custom_code(self):
        """Se o código for enviado, o sistema deve aceitá-lo."""
        data = {
            "pix_key": "98765432100",
            "pix_key_type": "cpf",
            "code": "MEUCOD123",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["code"], "MEUCOD123")

    def test_create_affiliate_duplicate_code(self):
        """Não deve permitir duplicar o código."""
        self.client.post(
            self.create_url,
            {
                "pix_key": "98765432100",
                "pix_key_type": "cpf",
                "code": "CODDUPLICADO",
            },
        )
        response = self.client.post(
            self.create_url,
            {
                "pix_key": "11122233344",
                "pix_key_type": "cpf",
                "code": "CODDUPLICADO",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.json())

    # ---------- VALORES INVÁLIDOS ----------

    def test_create_affiliate_invalid_pix_key_types(self):
        """pix_key_type inválido deve gerar erro."""
        data = {"pix_key": "12345678900", "pix_key_type": "unknown"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key_type", response.json())

    def test_create_affiliate_cpf_invalid(self):
        data = {"pix_key": "123", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_cnpj_invalid(self):
        data = {"pix_key": "123456789", "pix_key_type": "cnpj"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_affiliate_email_invalid(self):
        data = {"pix_key": "not-an-email", "pix_key_type": "email"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_affiliate_phone_invalid(self):
        data = {"pix_key": "123456", "pix_key_type": "phone"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_affiliate_random_invalid(self):
        data = {"pix_key": "abcd", "pix_key_type": "random"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_affiliate_empty_pix_key(self):
        data = {"pix_key": "", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- LISTAGEM E DETALHE ----------

    def test_list_affiliate_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_affiliate_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_list_affiliate_requires_auth(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_affiliate_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.affiliate.pk)

    # ---------- ATUALIZAÇÃO ----------

    def test_update_affiliate_user(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "53184468097", "pix_key_type": "cpf"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_affiliate_invalid_field(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "ERROR", "pix_key_type": "cpf"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_affiliate_not_owner(self):
        other_user = self.make_user_auth(
            username="other",
            email="other@email.com",
            phone="(11)33333-9999",
            cpf="407.913.650-60",
        )
        self.client.force_authenticate(user=other_user)
        data = {"pix_key": "05075710298"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- EXCLUSÃO ----------

    def test_delete_affiliate_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Affiliate.objects.filter(id=self.affiliate.pk).exists())

    def test_delete_affiliate_not_owner(self):
        other_user = self.make_user_auth(
            username="other",
            email="other@email.com",
            phone="(11)33333-9999",
            cpf="407.913.650-60",
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
