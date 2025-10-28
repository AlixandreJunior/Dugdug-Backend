from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.plan.models import Plan
from utils.tests_mixins import UserMixin


class PlanViewTests(APITestCase, UserMixin):
    def setUp(self):
        self.user = self.make_user_auth(username="user1")
        self.staff = self.make_staff_user(username="staff")
        self.superuser = self.make_superuser(username="admin")

        # Planos
        self.plan = Plan.objects.create(
            name="Plano Bronze", price=Decimal("100.00"), duration_days=30
        )

        # URLs
        self.plan_list_url = reverse("plan:list")
        self.plan_create_url = reverse("plan:create")
        self.plan_detail_url = reverse("plan:detail", args=[self.plan.name])
        self.plan_update_url = reverse("plan:update", args=[self.plan.name])
        self.plan_delete_url = reverse("plan:delete", args=[self.plan.name])

    # ----------------------------
    # Listagem de planos
    # ----------------------------
    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.plan_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.plan_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------
    # Detalhe do plano
    # ----------------------------
    def test_detail_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.plan_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.plan_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.plan.pk)

    # ----------------------------
    # Criação de planos
    # ----------------------------
    def test_create_unauthenticated(self):
        data: dict[str, object] = {
            "name": "Plano Ouro",
            "price": "200.00",
            "duration_days": 60,
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(self.plan_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_forbidden(self):
        data: dict[str, object] = {
            "name": "Plano Ouro",
            "price": "200.00",
            "duration_days": 60,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.plan_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_staff_allowed(self):
        data: dict[str, object] = {
            "name": "Plano Ouro",
            "price": "200.00",
            "duration_days": 60,
        }
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.plan_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "Plano Ouro")

    def test_create_superuser_allowed(self):
        data: dict[str, object] = {
            "name": "Plano Prata",
            "price": "300.00",
            "duration_days": 90,
        }
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(self.plan_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "Plano Prata")

    def test_create_invalid_data(self):
        data: dict[str, object] = {"name": "", "price": "abc", "duration_days": -5}
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(self.plan_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())
        self.assertIn("price", response.json())
        self.assertIn("duration_days", response.json())

    # ----------------------------
    # Atualização de planos
    # ----------------------------
    def test_update_unauthenticated(self):
        data = {"name": "Plano Bronze Atualizado"}
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.plan_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_forbidden(self):
        data = {"name": "Plano Bronze Atualizado"}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.plan_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_staff_allowed(self):
        data = {"name": "Plano Bronze Atualizado"}
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(self.plan_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.name, "Plano Bronze Atualizado")

    def test_update_superuser_allowed(self):
        data = {"name": "Plano Bronze Super"}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(self.plan_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.name, "Plano Bronze Super")

    def test_update_invalid_data(self):
        data = {"price": "invalid"}
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(self.plan_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.json())

    # ----------------------------
    # Exclusão de planos
    # ----------------------------
    def test_delete_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.plan_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.plan_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_staff_allowed(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.plan_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Plan.objects.filter(id=self.plan.pk).exists())

    def test_delete_superuser_allowed(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self.plan_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Plan.objects.filter(id=self.plan.pk).exists())
