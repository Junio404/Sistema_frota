from pydantic import BaseModel
from typing import Optional
from enums import Status_viagem

# -------------------- VIAGEM CREATE --------------------

class ViagemCreate(BaseModel):
    veiculo_id: int
    motorista_id: int
    origem: str
    destino: str
    hodometro_saida: int

# -------------------- VIAGEM UPDATE --------------------

class ViagemUpdate(BaseModel):
    destino: Optional[str] = None
    hodometro_chegada: Optional[int] = None
    status: Optional[Status_viagem] = None

# -------------------- VIAGEM RESPONSE --------------------

class ViagemResponse(BaseModel):
    id: int
    veiculo_id: int
    motorista_id: int
    origem: str
    destino: str
    hodometro_saida: int
    hodometro_chegada: Optional[int]
    status: Status_viagem