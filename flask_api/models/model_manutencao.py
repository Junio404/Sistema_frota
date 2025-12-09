from pydantic import BaseModel, Field
from typing import Optional
from flask_api.models.enums import Tipo_manutencao, Status_manutencao # usarei o status viagem pois ele tem o estado "em_andamento" e "concluida" que funciona perfeitamente para este caso.
from datetime import date

# -------------------- MANUTENCAO CREATE --------------------

class Manutencao_create(BaseModel):
    placa_fk: str
    tipo_manutencao: Tipo_manutencao


    data_inicio: date = Field(default_factory=date.today)


    data_conclusao: Optional[date] = None
    custo: Optional[float] = None
    descricao: Optional[str] = None
    status_manutencao: Status_manutencao = Field(default=Status_manutencao.EM_ANDAMENTO)
# -------------------- MANUTENCAO UPDATE --------------------

class Manutencao_update(BaseModel):
    placa_fk: Optional[str] = None
    tipo_manutencao: Optional[Tipo_manutencao] = None
    data: Optional[date] = None
    custo: Optional[float] = None
    descricao: Optional[str] = None
    status_manutencao: Optional[Status_manutencao] = None


# -------------------- MANUTENCAO RESPONSE --------------------

class Manutencao_response(BaseModel):
    id: int
    placa_fk: str
    tipo_manutencao: Tipo_manutencao
    data: date
    custo: float
    descricao: Optional[str]
    status_manutencao: Status_manutencao