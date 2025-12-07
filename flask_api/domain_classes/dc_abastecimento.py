from dataclasses import dataclass, field
from datetime import date
from flask_api.domain_classes.dc_veiculo import validar_placa_mercosul
from flask_api.models.enums import Qtd_combustivel_litro


@dataclass
class Abastecimento:
    _placa_fk: str = field(init=False, repr=False)
    _tipo_combustivel: str = field(init=False, repr=False)
    _data: date = field(init=False, repr=False)
    _litros: float = field(init=False, repr=False)
    _valor_pago: float = field(init=False, repr=False)
    _hodometro: float = field(init=False, repr=False)

    id: int | None = None

    def __init__(
        self,
        id: int | None,
        placa_fk: str,
        tipo_combustivel: str,
        data: date,
        litros: float,
        valor_pago: float,
        hodometro: float
    ):
        self.id = id
        self.placa_fk = placa_fk
        self.tipo_combustivel = tipo_combustivel
        self.data = data
        self.litros = litros
        self.valor_pago = valor_pago
        self.hodometro = hodometro

    # ------------------ PLACA FK ------------------
    @property
    def placa_fk(self):
        return self._placa_fk

    @placa_fk.setter
    def placa_fk(self, value):
        if not validar_placa_mercosul(value):
            raise ValueError("Placa inválida no padrão Mercosul.")
        self._placa_fk = value.upper()

    # ------------------ TIPO COMBUSTÍVEL ------------------
    @property
    def tipo_combustivel(self):
        return self._tipo_combustivel

    @tipo_combustivel.setter
    def tipo_combustivel(self, value):
        if value not in ("GASOLINA", "ETANOL", "DIESEL"):
            raise ValueError("Tipo de combustível inválido.")
        self._tipo_combustivel = value

    # ------------------ DATA ------------------
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, date):
            raise ValueError("A data deve ser um objeto date.")
        self._data = value

    # ------------------ LITROS ------------------
    @property
    def litros(self):
        return self._litros

    @litros.setter
    def litros(self, value):
        if value <= 0:
            raise ValueError("Quantidade de litros inválida.")
        self._litros = float(value)

    # ------------------ VALOR PAGO ------------------
    @property
    def valor_pago(self):
        return self._valor_pago

    @valor_pago.setter
    def valor_pago(self, value):
        if value < 0:
            raise ValueError("Valor pago inválido.")
        self._valor_pago = float(value)

    # ------------------ HODÔMETRO ------------------
    @property
    def hodometro(self):
        return self._hodometro

    @hodometro.setter
    def hodometro(self, value):
        if value < 0:
            raise ValueError("Hodômetro inválido.")
        self._hodometro = float(value)