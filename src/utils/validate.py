import re

from django.core.exceptions import ValidationError

from apps.user import models


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


def validate_password(password: str) -> None:
    if len(password) < 8:
        msg = "A senha deve ter no mínimo 8 caracteres."
        raise ValidationError(msg)
    if not re.search(r"[A-Z]", password):
        msg = "A senha deve conter ao menos uma letra maiúscula."
        raise ValidationError(msg)
    if not re.search(r"[a-z]", password):
        msg = "A senha deve conter ao menos uma letra minúscula."
        raise ValidationError(msg)
    if not re.search(r"\d", password):
        msg = "A senha deve conter ao menos um número."
        raise ValidationError(msg)
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        msg = "A senha deve conter ao menos um caractere especial."
        raise ValidationError(msg)


def validate_email(email: str) -> str:
    if models.User.objects.filter(email__iexact=email).exists():
        msg = "User with this email already exists."
        raise ValidationError(msg)
    return email
