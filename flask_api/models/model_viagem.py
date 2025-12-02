from pydantic import BaseModel
from typing import Optional
from flask_api.models.enums import Status_viagem
from datetime import date

# -------------------- VIAGEM CREATE --------------------

class ViagemCreate(BaseModel):
    placa_fk: str
    cpf_fk: str
    origem: str
    destino: str
    distancia_km: float
    data_chegada: date

# -------------------- VIAGEM UPDATE --------------------
class ViagemUpdate(BaseModel):
    destino: Optional[str] = None
    data_chegada: Optional[date] = None
    hodometro_chegada: Optional[float] = None
    status: Optional[Status_viagem] = None
# -------------------- VIAGEM RESPONSE --------------------

class ViagemResponse(BaseModel):
    id: int
    placa_fk: str
    cpf_fk: str
    origem: str
    destino: str
    distancia_km: float
    data_saida: date
    data_chegada: Optional[date]
    hodometro_saida: float
    hodometro_chegada: Optional[float]
    status: Status_viagem