from django.db import models

class Customer(models.Model):
    class Meta:
        verbose_name: str = "Customer"
        verbose_name_plural: str = "Customers"

    ...

    def __str__(self) -> str:
        return f"Cliente {...}"
