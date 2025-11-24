from pydantic import BaseModel
from typing import Optional


class PessoaBase(BaseModel):
    nome: str
    cpf: str


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    nome: Optional[str] = None


class PessoaResponse(PessoaBase):
    id: int

    class Config:
        from_attributes = True