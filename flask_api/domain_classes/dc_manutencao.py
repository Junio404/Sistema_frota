from dataclasses import dataclass, field
from datetime import date
from flask_api.models.enums import Tipo_manutencao, Status_manutencao


@dataclass
class Manutencao:
    _id: int = field(init=False, repr=False)
    _placa_fk: str = field(init=False, repr=False)
    _tipo_manutencao: Tipo_manutencao = field(init=False, repr=False)
    _data_inicio: date = field(init=False, repr=False)
    _data_conclusao: date | None = field(init=False, repr=False)
    _custo: float = field(init=False, repr=False)
    _descricao: str = field(init=False, repr=False)
    _status_manutencao: Status_manutencao = field(init=False, repr=False)

    def __init__(
        self,
        id: int,
        placa_fk: str,
        tipo_manutencao: Tipo_manutencao,
        data_inicio: date,
        data_conclusao: date | None,
        custo: float,
        descricao: str,
        status_manutencao: Status_manutencao
    ):
        self.id = id
        self.placa_fk = placa_fk
        self.tipo_manutencao = tipo_manutencao
        self.data_inicio = data_inicio
        self.data_conclusao = data_conclusao
        self.custo = custo
        self.descricao = descricao
        self.status_manutencao = status_manutencao

    # ID
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("ID inválido.")
        self._id = value

    # PLACA
    @property
    def placa_fk(self):
        return self._placa_fk

    @placa_fk.setter
    def placa_fk(self, value):
        if not isinstance(value, str) or len(value) < 7:
            raise ValueError("Placa inválida.")
        self._placa_fk = value.upper()

    # TIPO MANUTENÇÃO
    @property
    def tipo_manutencao(self):
        return self._tipo_manutencao

    @tipo_manutencao.setter
    def tipo_manutencao(self, value):
        if not isinstance(value, Tipo_manutencao):
            raise ValueError("Tipo de manutenção inválido.")
        self._tipo_manutencao = value

    # ------------------ DATA INICO ------------------
    @property
    def data_inicio(self):
        return self._data_inicio

    @data_inicio.setter
    def data_inicio(self, value):
        if not isinstance(value, date):
            raise ValueError("A data de início deve ser uma data válida.")
        self._data_inicio = value

    # ------------------ DATA CONCLUSAO ------------------
    @property
    def data_conclusao(self):
        return self._data_conclusao

    @data_conclusao.setter
    def data_conclusao(self, value):
        if value is not None:
            if not isinstance(value, date):
                raise ValueError("A data de conclusão deve ser uma data.")
            if value < date.today():
                   raise ValueError("Insira a data de hoje ou de dias posteriores")
        self._data_conclusao = value
    # ------------------ CUSTO ------------------
    @property
    def custo(self):
        return self._custo

    @custo.setter
    def custo(self, value):
        if not isinstance(value, (float, int)) or value < 0:
            raise ValueError("Custo inválido.")
        self._custo = float(value)

    # ------------------ DESCRICAO ------------------
    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Descrição inválida.")
        self._descricao = value.strip()

    # ------------------ STATUS ------------------
    @property
    def status_manutencao(self):
        return self._status_manutencao

    @status_manutencao.setter
    def status_manutencao(self, value):
        if not isinstance(value, Status_manutencao):
            raise ValueError("Status de manutenção inválido.")
        self._status_manutencao = value