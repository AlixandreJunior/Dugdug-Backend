from django.db import models

from apps.user.models import User


class Customer(models.Model):
    class Meta:
        verbose_name: str = "Customer"
        verbose_name_plural: str = "Customers"

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Cliente {...}"


class Subscription(models.Model):
    class Meta:
        verbose_name: str = "Subscription"
        verbose_name_plural: str = "Subscriptions"

    costumer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Assinatura {...}"
