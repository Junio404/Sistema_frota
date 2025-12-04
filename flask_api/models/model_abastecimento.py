from pydantic import BaseModel
from typing import Optional
from flask_api.models.enums import Tipo_combustivel
from datetime import date

# -------------------- ABASTECIMENTO CREATE --------------------

class Abastecimento_create(BaseModel):
    placa_fk: str
    tipo_combustivel: Tipo_combustivel
    data: date
    litros: float
    valor_pago: float
    hodometro: float
    
# -------------------- ABASTECIMENTO UPDATE --------------------

class Abastecimento_update(BaseModel):
    placa_fk: Optional[str] = None
    tipo_combustivel: Optional[Tipo_combustivel] = None
    data: Optional[date] = None
    litros: Optional[float] = None
    valor_pago: Optional[float] = None
    hodometro: Optional[float] = None


# -------------------- ABASTECIMENTO RESPONSE --------------------

class Abastecimento_response(BaseModel):
    id: int
    placa_fk: str
    tipo_combustivel: Tipo_combustivel
    data: date
    litros: float
    valor_pago: float
    hodometro: float