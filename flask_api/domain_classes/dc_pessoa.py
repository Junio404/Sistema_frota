from dataclasses import dataclass, field

@dataclass
class Pessoa:
    _id: int | None
    _nome: str = field(init=False, repr=False)
    _cpf: str = field(init=False, repr=False)

    def __init__(self, id: int | None, nome: str, cpf: str):
        self._id = id
        self.nome = nome
        self.cpf = cpf

    # ------------------- ID -------------------
    @property
    def id(self):
        return self._id

    # ------------------- NOME -------------------
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ValueError("Nome inválido.")

        caracteres_invalidos = set("@#$%¨&*()[];:<>{}º°?+-_=§'")
        if any(char in caracteres_invalidos for char in value):
            raise ValueError("Nome inválido de pessoa.")

        self._nome = value.strip()

    # ------------------- CPF -------------------
    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, value: str):
        if not value.isdigit() or len(value) != 11:
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")
        self._cpf = value
