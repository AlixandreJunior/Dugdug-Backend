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
        self.user = self.make_user_auth(username="user1")
        self.superuser = self.make_superuser(username="admin")

        self.plan = Plan.objects.create(
            name="Plano Bronze", price=Decimal("100.00"), duration_days=30
        )
        self.plan2 = Plan.objects.create(
            name="Plano Prata", price=Decimal("200.00"), duration_days=60
        )

        self.affiliate = self.make_affiliate(user=self.user, code="AFF12345")

        self.subscription = Subscription.objects.create(
            costumer=self.user,
            plan=self.plan,
            affiliate=self.affiliate,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
            payment_method="pix",
        )

        self.subscription_list_url = reverse("subscription-list")
        self.subscription_create_url = reverse("subscription-create")
        self.subscription_detail_url = reverse(
            "subscription-detail", args=[self.subscription.pk]
        )
        self.subscription_cancel_url = reverse(
            "subscription-cancel", args=[self.subscription.pk]
        )
        self.subscription_admin_list_url = reverse("subscription-admin-list")

    def test_subscription_list_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_subscription_create_with_affiliate(self):
        self.client.force_authenticate(user=self.user)
        data: dict[str, object] = {
            "plan_id": self.plan2.pk,
            "affiliate_code": self.affiliate.code,
            "payment_method": "pix",
        }
        response = self.client.post(self.subscription_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.commission_balance, Decimal("20.00"))

    def test_subscription_cancel(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.subscription_cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)
