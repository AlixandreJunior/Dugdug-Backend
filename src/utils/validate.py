import re

from django.core.exceptions import ValidationError


def validate_cpf(value: str) -> None:
    cpf = re.sub(r"\D", "", value)

    if len(cpf) != 11:
        message = "CPF deve conter 11 dígitos."
        raise ValidationError(message)

    if cpf == cpf[0] * 11:
        message = "CPF inválido: todos os dígitos são iguais."
        raise ValidationError(message)

    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = ((sum1 * 10) % 11) % 10

    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = ((sum2 * 10) % 11) % 10

    if int(cpf[9]) != digit1 or int(cpf[10]) != digit2:
        message = "CPF inválido: dígitos verificadores incorretos."
        raise ValidationError(message)


def validate_phone(value: str) -> None:
    phone = re.sub(r"\s+", "", value)
    phone_pattern = re.compile(r"^(?:\(\d{2}\))?\d{4,5}-?\d{4}$")

    if not phone_pattern.match(phone):
        message = "Telefone inválido. Use o formato (XX)XXXXX-XXXX ou apenas números."

        raise ValidationError(message)

    digits_only = re.sub(r"\D", "", phone)

    if len(digits_only) not in (10, 11):
        message = "Telefone deve conter 10 ou 11 dígitos."
        raise ValidationError(message)

    if digits_only == digits_only[0] * len(digits_only):
        message = "Telefone inválido: todos os dígitos são iguais."
        raise ValidationError(message)
