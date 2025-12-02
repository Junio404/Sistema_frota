class Pessoa:
    def __init__(self, id: int, nome: str, cpf: str):
        self._id = id
        self._nome = nome
        self._cpf = cpf

    # ID
    @property
    def id(self):
        return self._id

    # NOME
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value: str):
        if not value or len(value) < 2:
            raise ValueError("Nome inválido.")
        if value in ("@","#","!","$","%", "¨", "&","*","(",")","[","]",",",".",";",":","<",">","{","}","º","°","?", "+", "-", "_","§", "=", "'"):
            raise ValueError("Nome inválido de pessoa.")
        self._nome = value

    # CPF
    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, value: str):
        if len(value) != 11:
            raise ValueError("CPF inválido")
        self._cpf = value