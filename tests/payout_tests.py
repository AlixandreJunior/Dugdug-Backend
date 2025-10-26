from decimal import Decimal

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

    # ------------------- CRIAÇÃO DE PAYOUT -------------------

    def test_create_payout_success(self):
        self.affiliate.commission_balance = Decimal(70)
        self.affiliate.save(update_fields=["commission_balance"])

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["affiliate"], self.affiliate.pk)
        self.assertEqual(response.json()["amount"], "70.00")

        # Verifica que o commission_balance foi zerado
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.commission_balance, 0)

    def test_create_payout_insufficient_balance(self):
        self.affiliate.commission_balance = Decimal(30)
        self.affiliate.save(update_fields=["commission_balance"])

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Saldo insuficiente", str(response.data))

        # commission_balance não deve mudar
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.commission_balance, 30)

    def test_create_payout_not_affiliate(self):
        new_user = self.make_user_auth(
            username="other",
            email="other@email.com",
            phone="(11)77777-7777",
            cpf="63787432078",
        )
        self.client.force_authenticate(user=new_user)
        response = self.client.post(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- LISTAGEM -------------------

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

    # ------------------- DETALHE -------------------

    def test_detail_payout_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.payout.pk)

    # ------------------- ATUALIZAÇÃO -------------------

    def test_update_payout_admin(self):
        self.client.force_authenticate(user=self.superuser)
        data = {"status": "paid"}
        response = self.client.patch(self.update_url, data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, "paid")

    def test_update_payout_not_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"status": "paid"}
        response = self.client.patch(self.update_url, data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- DELEÇÃO -------------------

    def test_delete_payout_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Payout.objects.filter(id=self.payout.pk).exists())

    def test_delete_payout_not_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ------------------- TESTE DE MULTIPLOS PAYOUTS -------------------

    def test_create_multiple_payouts_no_negative_balance(self):
        # Define um saldo inicial
        self.affiliate.commission_balance = Decimal(120)
        self.affiliate.save(update_fields=["commission_balance"])

        self.client.force_authenticate(user=self.user)

        response1 = self.client.post(self.create_url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.json()["amount"], "120.00")

        # Verifica que o saldo foi zerado
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.commission_balance, 0)

        # Tenta criar outro payout com saldo zerado
        response2 = self.client.post(self.create_url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Saldo insuficiente", str(response2.data))
