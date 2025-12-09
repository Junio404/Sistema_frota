from pydantic import BaseModel
from typing import Optional
from flask_api.models.enums import Veiculo_status, Tipo_combustivel

# -------------------- VEICULO CREATE --------------------

class Veiculo_create(BaseModel):
    placa: str
    modelo_fk: int
    tipo_veiculo: str
    ano: int
    quilometragem: float
    consumo_medio_km_l: float
    qtd_litros: int
    status: Veiculo_status = Veiculo_status.ATIVO
    tipo_combustivel: Tipo_combustivel

# -------------------- VEICULO UPDATE --------------------

class Veiculo_update(BaseModel):
    consumo_medio_km_l: Optional[float] = None
    status: Optional[Veiculo_status] = None
# -------------------- VEICULO RESPONSE --------------------

class Veiculo_response(BaseModel):
    placa: str
    modelo_fk: int
    tipo_veiculo: str
    ano: int
    quilometragem: float
    consumo_medio_km_l: float
    status: Veiculo_status
    tipo_combustivel: Tipo_combustivel