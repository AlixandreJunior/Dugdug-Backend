from django.db import models
from django.utils import timezone

from apps.affiliate.models import Affiliate
from apps.user.models import User


class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)

    def __str__(self) -> str:
        return f"{self.name} - R${self.price}"


class Subscription(models.Model):
    class Meta:
        verbose_name: str = "Subscription"
        verbose_name_plural: str = "Subscriptions"

    class PaymentMethodChoices(models.TextChoices):
        PIX = "pix", "PIX"
        CREDIT_CARD = "credit", "Credit"
        BOLETO = "boleto", "Boleto"

    costumer = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True)
    is_active = models.BooleanField(default=True)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethodChoices.choices, default="pix"
    )

    def __str__(self) -> str:
        return f"{self.costumer.username} - {self.plan.name}"
