from typing import ClassVar

from django.db import models
from django.utils import timezone

from apps.user.models import User


class Affiliate(models.Model):
    class Meta:
        verbose_name: str = "Affiliate"
        verbose_name_plural: str = "Affiliates"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=26, unique=True)
    commission_balance = models.DecimalField(max_digits=10, decimal_places=2)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2)
    pix_key = models.CharField(max_length=120)
    joined_at = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f"Afiliado {self.user.username}"


class Payout(models.Model):
    class Meta:
        verbose_name: str = "Payout"
        verbose_name_plural: str = "Payouts"
        ordering: ClassVar[list[str]] = ["-requested_at"]

    class StatusChoices(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"

    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pix_key = models.CharField(max_length=120, help_text="Pix key for payment")
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default="pending"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.affiliate.user.username} - R${self.amount} ({self.status})"
