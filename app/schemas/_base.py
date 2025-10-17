import re
from typing import Annotated, TypeVar
from pydantic import AfterValidator, BaseModel, ConfigDict

class OrmBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")


PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$^&*-]).{8,32}$')
CPF_REGEX = re.compile(r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$')

def is_valid_cpf(cpf: str):
    cpf_clean = re.sub(r'[.-]', '', cpf)

    if len(cpf_clean) != 11:
        raise ValueError('Seu CPF é inválido.')
    else:
        cpf_clean = ''.join(filter(str.isdigit, cpf_clean)).zfill(11)
        if len(cpf_clean) != 11:
            raise ValueError("CPF deve conter 11 dígitos")

        if cpf_clean == cpf_clean[0] * 11:
            raise ValueError('Seu CPF é inválido.')

        total = 0
        for i in range(9):
            total += int(cpf_clean[i]) * (10 - i)
        remainder = total % 11
        if remainder < 2:
            if int(cpf_clean[9]) != 0:
                raise ValueError('Seu CPF é inválido.')
        else:
            if int(cpf_clean[9]) != 11 - remainder:
                raise ValueError('Seu CPF é inválido.')

        total = 0
        for i in range(10):
            total += int(cpf_clean[i]) * (11 - i)
        remainder = total % 11
        if remainder < 2:
            if int(cpf_clean[10]) != 0:
                raise ValueError('Seu CPF é inválido.')
        else:
            if int(cpf_clean[10]) != 11 - remainder:
                raise ValueError('Seu CPF é inválido.')

    return cpf

cpf_format = Annotated[str, AfterValidator(lambda cpf: f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}")]
clean_cpf_format = Annotated[str, AfterValidator(lambda cpf:re.sub(r'[.-]', '', cpf))]
CPF_VALIDATOR = Annotated[str, AfterValidator(is_valid_cpf)]
VALID_CLEAN_CPF = Annotated[str, AfterValidator(is_valid_cpf), AfterValidator(lambda cpf: re.sub(r'[.-]', '', cpf))]


EnumT = TypeVar("EnumT")

ENUM_VALUE = Annotated[EnumT, AfterValidator(lambda v: v.value)]