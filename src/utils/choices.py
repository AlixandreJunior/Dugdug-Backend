from django.db import models


class PixKeyTypeChoices(models.TextChoices):
    CPF = "cpf", "CPF"
    CNPJ = "cnpj", "CNPJ"
    EMAIL = "email", "E-mail"
    PHONE = "phone", "Telefone"
    RANDOM = "random", "Chave Aleatória"


class StatusChoices(models.TextChoices):
    PAID = "paid", "Paid"
    PENDING = "pending", "Pending"
    FAILED = "failed", "Failed"


class PaymentMethodChoices(models.TextChoices):
    PIX = "pix", "PIX"
    CREDIT_CARD = "credit", "Credit"
    BOLETO = "boleto", "Boleto"
