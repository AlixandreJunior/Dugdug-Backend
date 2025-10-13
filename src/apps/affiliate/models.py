from django.db import models

class Affiliate(models.Model):
    class Meta:
        verbose_name: str = "Affiliate"
        verbose_name_plural: str = "Affiliates"

    ...

    def __str__(self) -> str:
        return f"Afiliado {...}"