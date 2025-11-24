from pydantic import BaseModel
from typing import Optional
from enums import Tipo_manutencao
from datetime import date

# -------------------- MANUTENCAO CREATE --------------------

class Manutencao_create(BaseModel):
    placa_fk: str
    tipo_manutenção: Tipo_manutencao
    data: date
    custo: float
    descricao: str
    status_manutencao: str
# -------------------- MANUTENCAO UPDATE --------------------

class Manutencao_update(BaseModel):
    placa_fk: Optional[str] = None
    tipo_manutencao: Optional[Tipo_manutencao] = None
    data: Optional[date] = None
    custo: Optional[float] = None
    descricao: Optional[str] = None
    status_manutencao: Optional[str] = None


# -------------------- MANUTENCAO RESPONSE --------------------

class Manutencao_response(BaseModel):
    id: int
    placa_fk: str
    tipo_manutencao: Tipo_manutencao
    data: date
    custo: float
    descricao: Optional[str]
    status_manutencao: str