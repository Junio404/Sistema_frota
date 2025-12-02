from pydantic import BaseModel
from typing import Optional


# -------------------- TIPO VEICULO RESPONSE --------------------

class Tipo_veiculo_cnh_response(BaseModel):
    tipo_veiculo: str
    cat_min_cnh: str


# -------------------- MARCA CREATE --------------------
class Marca_create(BaseModel):
    nome_modelo: str
    marca_fk: str
    tipo_veiculo: str
# -------------------- MARCA UPDATE --------------------

class Marca_update(BaseModel):
    nome_modelo: Optional[str] = None
    marca_fk: Optional[str] = None
    tipo_veiculo: Optional[str] = None

# -------------------- MANUTENCAO RESPONSE --------------------

class Manutencao_response(BaseModel):
    id: int
    nome_modelo: str
    marca_fk: str
    tipo_veiculo: str