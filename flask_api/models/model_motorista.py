from datetime import date, datetime
from typing import Optional
from pydantic import validator
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

    @validator('cnh_valido_ate', pre=True)
    def converter_data_cnh(cls, value):
        """Converte a string 'YYYY-MM-DD' para objeto date."""
        if value is None or isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                # Trata strings vazias ou None vindos do request.form.get()
                if not value.strip(): 
                    return None
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Formato de data de validade da CNH inválido. Use YYYY-MM-DD.")
        
        return value


# -------------------- MOTORISTA RESPONSE --------------------
class Motorista_response(PessoaResponse):
    cat_cnh: str
    exp_anos: int
    disponibilidade: Status_motorista
    cnh_valido_ate: date

    class Config:
        from_attributes = True