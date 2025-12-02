from datetime import date
from typing import Optional
from flask_api.models.enums import Status_motorista
from flask_api.interfaces.interface_pessoa import PessoaCreate, PessoaResponse, PessoaUpdate


# -------------------- MOTORISTA CREATE --------------------
class Motorista_create(PessoaCreate):
    cat_cnh: str
    exp_anos: int
    disponibilidade: Status_motorista
    cnh_valido_ate: date


# -------------------- MOTORISTA UPDATE --------------------
class Motorista_update(PessoaUpdate):
    cat_cnh: Optional[str] = None
    exp_anos: Optional[int] = None
    disponibilidade: Optional[Status_motorista] = None
    cnh_valido_ate: Optional[date] = None


# -------------------- MOTORISTA RESPONSE --------------------
class Motorista_response(PessoaResponse):
    cat_cnh: str
    exp_anos: int
    disponibilidade: Status_motorista
    cnh_valido_ate: date

    class Config:
        from_attributes = True