from pydantic import BaseModel
from typing import Optional


# -------------------- MARCA CREATE --------------------

class Marca_create(BaseModel):
    nome:str
# -------------------- MARCA UPDATE --------------------

class Marca_update(BaseModel):
    nome: Optional[str] = None


# -------------------- MANUTENCAO RESPONSE --------------------

class Manutencao_response(BaseModel):
    id: int
    nome: str