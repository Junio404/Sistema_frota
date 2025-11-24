from pydantic import BaseModel
from typing import Optional
from enums import Veiculo_status

# -------------------- VEICULO CREATE --------------------

class VeiculoCreate(BaseModel):
    marca_id: int
    modelo_id: int
    placa: str
    ano: int
    status: Veiculo_status = Veiculo_status.ativo

# -------------------- VEICULO UPDATE --------------------

class VeiculoUpdate(BaseModel):
    marca_id: Optional[int] = None
    modelo_id: Optional[int] = None
    placa: Optional[str] = None
    ano: Optional[int] = None
    status: Optional[Veiculo_status] = None

# -------------------- VEICULO RESPONSE --------------------

class VeiculoResponse(BaseModel):
    id: int
    marca_id: int
    modelo_id: int
    placa: str
    ano: int
    status: Veiculo_status