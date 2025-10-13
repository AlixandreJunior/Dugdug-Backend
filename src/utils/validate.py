import re

from django.core.exceptions import ValidationError


def validate_cpf(value: str) -> None:
    cpf_pattern = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
    if not cpf_pattern.match(value):
        message = "CPF inválido. Use o formato XXX.XXX.XXX-XX ou apenas números."
        raise ValidationError(message)


def validate_phone(value: str) -> None:
    phone_pattern = re.compile(r"^(\(\d{2}\)\s?)?\d{4,5}-?\d{4}$")
    if not phone_pattern.match(value):
        message = "Telefone inválido."
        raise ValidationError(message)
