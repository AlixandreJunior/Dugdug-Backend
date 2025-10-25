from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.affiliate.models import Affiliate, Payout
from apps.user.models import User
from utils.user_mixin import UserMixin


class AffiliateMixin(UserMixin):
    def make_affiliate(
        self,
        user: User | None = None,
        code: str = "AFF123",
        commission_balance: int = 0,
        total_earned: int = 0,
        pix_key: str = "123456789",
        pix_key_type: str = "cpf",
    ) -> Affiliate:
        if user is None:
            user = self.make_user_auth()

        return Affiliate.objects.create(
            user=user,
            code=code,
            commission_balance=commission_balance,
            total_earned=total_earned,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
        )


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

    def test_create_affiliate_already_exists(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "53184468097", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_affiliate_cpf_valid(self):
        data = {"pix_key": "53184468097", "pix_key_type": "cpf"}
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

    # ---------- VALORES INVÁLIDOS ----------

    def test_create_affiliate_cpf_invalid(self):
        data = {"pix_key": "123", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_cnpj_invalid(self):
        data = {"pix_key": "123456789", "pix_key_type": "cnpj"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_email_invalid(self):
        data = {"pix_key": "not-an-email", "pix_key_type": "email"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_phone_invalid(self):
        data = {"pix_key": "123456", "pix_key_type": "phone"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_random_invalid(self):
        data = {"pix_key": "abcd", "pix_key_type": "random"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

    def test_create_affiliate_empty_pix_key(self):
        self.client.force_authenticate(user=self.staff)
        data = {"pix_key": "", "pix_key_type": "cpf"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pix_key", response.json())

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

    def test_detail_affiliate_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.affiliate.pk)

    def test_update_affiliate_user(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "53184468097", "pix_key_type": "cpf"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.pix_key, "53184468097")

    def test_update_affiliate_invalid_field(self):
        self.client.force_authenticate(user=self.user)
        data = {"pix_key": "ERROR", "pix_key_type": "cpf"}
        response = self.client.patch(self.update_url, data)
        print(response.json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_affiliate_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Affiliate.objects.filter(id=self.affiliate.pk).exists())


# ========================
# TESTES DE PAYOUT
# ========================
class PayoutViewTests(APITestCase, AffiliateMixin):
    def setUp(self):
        self.client = APIClient()
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

        # Payout existente
        self.payout = Payout.objects.create(
            affiliate=self.affiliate, amount=100, pix_key=self.affiliate.pix_key
        )

        # URLs
        self.create_url = reverse("payout-create")
        self.list_url = reverse("payout-list")
        self.detail_url = reverse("payout-detail", args=[self.payout.pk])
        self.update_url = reverse("payout-update", args=[self.payout.pk])
        self.delete_url = reverse("payout-delete", args=[self.payout.pk])

    def test_create_payout_success(self):
        self.client.force_authenticate(user=self.user)
        data: dict[str, object] = {"amount": 50, "pix_key": "63787432078"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["affiliate"], self.affiliate.pk)

    def test_create_payout_not_affiliate(self):
        new_user = self.make_user_auth(
            username="other",
            email="other@email.com",
            phone="(11)77777-7777",
            cpf="63787432078",  # telefone único
        )
        self.client.force_authenticate(user=new_user)
        data: dict[str, object] = {"amount": 50, "pix_key": "63787432078"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_payout_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_payout_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_detail_payout_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.payout.pk)

    def test_update_payout_admin(self):
        self.client.force_authenticate(user=self.superuser)
        data = {"status": "paid"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, "paid")

    def test_update_payout_not_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"status": "paid"}
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_payout_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Payout.objects.filter(id=self.payout.pk).exists())
