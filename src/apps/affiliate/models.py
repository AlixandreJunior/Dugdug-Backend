from django.db import models

from apps.user.models import User


class Affiliate(models.Model):
    class Meta:
        verbose_name: str = "Affiliate"
        verbose_name_plural: str = "Affiliates"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=26)
    commission_balance = models.DecimalField()
    total_earned = models.DecimalField()

    def __str__(self) -> str:
        return f"Afiliado {self.user.username}"


class Sale(models.Model):
    class Meta:
        verbose_name: str = "Affiliate"
        verbose_name_plural: str = "Affiliates"

    affiliate = models.ForeignKey(Affiliate, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f"Venda Nº{self.pk}"
