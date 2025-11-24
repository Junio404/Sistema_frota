from datetime import date
from typing import Optional
from enums import Status_motorista
from interfaces.interface_pessoa import PessoaCreate, PessoaResponse, PessoaUpdate


# -------------------- MOTORISTA CREATE --------------------
class MotoristaCreate(PessoaCreate):
    cat_cnh: str
    exp_anos: int
    disponibilidade: Status_motorista
    cnh_valido_ate: date


# -------------------- MOTORISTA UPDATE --------------------
class MotoristaUpdate(PessoaUpdate):
    cat_cnh: Optional[str] = None
    exp_anos: Optional[int] = None
    disponibilidade: Optional[Status_motorista] = None
    cnh_valido_ate: Optional[date] = None


# -------------------- MOTORISTA RESPONSE --------------------
class MotoristaResponse(PessoaResponse):
    cat_cnh: str
    exp_anos: int
    disponibilidade: Status_motorista
    cnh_valido_ate: date

    class Config:
        from_attributes = True