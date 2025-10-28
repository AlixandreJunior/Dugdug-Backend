from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.plan.models import Plan, Subscription
from utils.tests_mixins import AffiliateMixin


class SubscriptionViewTests(APITestCase, AffiliateMixin):
    def setUp(self):
        self.client = self.client
        # Usuários
        self.user = self.make_user_auth(username="user1")
        self.superuser = self.make_superuser(username="admin")
        self.other_user = self.make_user_auth(
            username="user2",
            cpf="833.740.410-86",
            phone="(11)11111-2222",
            email="otheruser@gmail.com",
        )

        # Planos
        self.plan = Plan.objects.create(
            name="Plano Bronze", price=Decimal("100.00"), duration_days=30
        )
        self.plan2 = Plan.objects.create(
            name="Plano Prata", price=Decimal("200.00"), duration_days=60
        )

        # Afiliado
        self.affiliate = self.make_affiliate(user=self.user, code="AFF12345")

        # Subscription
        self.subscription = Subscription.objects.create(
            costumer=self.user,
            plan=self.plan,
            affiliate=self.affiliate,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
            payment_method="pix",
        )

        # URLs
        self.subscription_list_url = reverse("plan:subscription-list")
        self.subscription_create_url = reverse("plan:subscription-create")
        self.subscription_detail_url = reverse(
            "plan:subscription-detail", args=[self.subscription.pk]
        )
        self.subscription_cancel_url = reverse(
            "plan:subscription-cancel", args=[self.subscription.pk]
        )
        self.subscription_admin_list_url = reverse("plan:subscription-admin-list")

    # ----------------------------
    # Listar Subscriptions
    # ----------------------------
    def test_list_subscriptions_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_subscriptions_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_subscriptions_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.subscription_admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    # ----------------------------
    # Criar Subscription
    # ----------------------------
    def test_create_subscription_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "plan_id": self.plan2.pk,
            "affiliate_code": self.affiliate.code,
            "payment_method": "pix",
        }
        response = self.client.post(self.subscription_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.commission_balance, Decimal("20.00"))

    def test_create_subscription_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            "plan_id": self.plan2.pk,
            "affiliate_code": self.affiliate.code,
            "payment_method": "pix",
        }
        response = self.client.post(self.subscription_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_subscription_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "plan_id": 9999,
            "affiliate_code": "INVALID",
            "payment_method": "unknown",
        }
        response = self.client.post(self.subscription_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Detalhe da Subscription
    # ----------------------------
    def test_detail_subscription_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.subscription_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_subscription_other_user_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.subscription_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_subscription_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.subscription_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_subscription_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.subscription_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # Cancelar Subscription
    # ----------------------------
    def test_cancel_subscription_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.subscription_cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)

    def test_cancel_subscription_other_user_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.subscription_cancel_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_subscription_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(self.subscription_cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_subscription_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.subscription_cancel_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
