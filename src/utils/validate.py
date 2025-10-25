import re
import uuid
from typing import cast

from django.core.exceptions import ValidationError

from apps.user import models
from utils.choices import PixKeyTypeChoices


def validate_cnpj(cnpj: str) -> None:
    cnpj = re.sub(r"\D", "", cnpj or "")

    if len(cnpj) != 14:
        msg = "CNPJ deve ter 14 dígitos."
        raise ValidationError(msg)

    if cnpj == cnpj[0] * 14:
        msg = "CNPJ inválido."
        raise ValidationError(msg)

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, *pesos_1]

    soma1 = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
    dig1 = soma1 % 11
    dig1 = 0 if dig1 < 2 else 11 - dig1

    soma2 = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
    dig2 = soma2 % 11
    dig2 = 0 if dig2 < 2 else 11 - dig2

    if int(cnpj[12]) != dig1 or int(cnpj[13]) != dig2:
        msg = "CNPJ inválido."
        raise ValidationError(msg)


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


def validate_random_pix_key(key: str) -> str:
    if not key or not key.strip():
        msg = "Chave aleatória (EVP) vazia ou inválida."
        raise ValidationError(msg)

    key_str = key.strip()

    pattern_formatted = (
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )
    pattern_alnum32 = r"^[0-9a-fA-F]{32}$"

    if re.fullmatch(pattern_formatted, key_str):
        try:
            u = uuid.UUID(key_str)
        except (ValueError, AttributeError):
            msg = "UUID formatado inválido para chave aleatória (EVP)."
            raise ValidationError(msg) from None
    elif re.fullmatch(pattern_alnum32, key_str):
        try:
            u = uuid.UUID(key_str)
        except (ValueError, AttributeError):
            msg = "Chave aleatória inválida (32 hex)."
            raise ValidationError(msg) from None
    else:
        msg = (
            "Formato inválido. Informe um UUID canônico com hífens (8-4-4-4-12) "
            "ou 32 caracteres hex (apenas letras e números hexadecimais)."
        )
        raise ValidationError(msg)

    return str(u)


def validate_pix_key(key: str, type_key: str) -> None:
    if type_key == cast("str", PixKeyTypeChoices.EMAIL):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", key or ""):
            raise ValidationError({"pix_key": "E-mail inválido para chave PIX."})

    elif type_key == cast("str", PixKeyTypeChoices.CPF):
        cpf = re.sub(r"\D", "", key or "")
        validate_cpf(cpf)

    elif type_key == cast("str", PixKeyTypeChoices.CNPJ):
        cnpj = re.sub(r"\D", "", key or "")
        validate_cnpj(cnpj)

    elif type_key == cast("str", PixKeyTypeChoices.PHONE):
        validate_phone(key)

    elif type_key == cast("str", PixKeyTypeChoices.RANDOM):
        validate_random_pix_key(key)

    else:
        raise ValidationError({"pix_key_type": "Tipo de chave PIX inválido."})
