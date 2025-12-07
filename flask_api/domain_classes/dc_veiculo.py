from dataclasses import dataclass, field
from flask_api.repositories.veiculo_repo.veiculo_repo import validar_placa_mercosul
from flask_api.models.enums import Tipo_combustivel, Veiculo_status


@dataclass
class Veiculo:
    __placa: str = field(init=False, repr=False)
    __modelo_fk: int = field(init=False, repr=False)
    __tipo_veiculo: str = field(init=False, repr=False)
    __ano: int = field(init=False, repr=False)
    __quilometragem: float = field(init=False, repr=False)
    __consumo_medio_km_l: float = field(init=False, repr=False)
    __qtd_litros: int = field(init=False, repr=False)
    __tipo_combustivel: str = field(init=False, repr=False)
    __status: str = field(init=False, repr=False)

    def __init__(
        self,
        placa: str,
        modelo_fk: int,
        tipo_veiculo: str,
        ano: int,
        quilometragem: float,
        consumo_medio_km_l: float,
        qtd_litros: int,
        tipo_combustivel: str,
        status: str = Veiculo_status.ATIVO
    ):
        self.placa = placa
        self.modelo_fk = modelo_fk
        self.tipo_veiculo = tipo_veiculo
        self.ano = ano
        self.quilometragem = quilometragem
        self.consumo_medio_km_l = consumo_medio_km_l
        self.qtd_litros = qtd_litros
        self.tipo_combustivel = tipo_combustivel
        self.status = status


    # -- PLACA --
    @property
    def placa(self):
        return self.__placa

    @placa.setter
    def placa(self, value):
        if not validar_placa_mercosul(value):
            raise ValueError("Placa inválida no padrão Mercosul.")
        self.__placa = value.upper()


    # -- MODELO FK --
    @property
    def modelo_fk(self):
        return self.__modelo_fk

    @modelo_fk.setter
    def modelo_fk(self, value):
        if value <= 0:
            raise ValueError("Modelo inválido.")
        self.__modelo_fk = value


    # -- TIPO VEÍCULO --
    @property
    def tipo_veiculo(self):
        return self.__tipo_veiculo

    @tipo_veiculo.setter
    def tipo_veiculo(self, value):
        if not value:
            raise ValueError("Tipo de veículo inválido.")
        self.__tipo_veiculo = value


    # -- ANO --
    @property
    def ano(self):
        return self.__ano
    
    @ano.setter
    def ano(self, value):
        if int(value) < 1980:
            raise ValueError("Ano inválido.")
        self.__ano = int(value)


    # -- QUILOMETRAGEM --
    @property
    def quilometragem(self):
        return self.__quilometragem

    @quilometragem.setter
    def quilometragem(self, value):
        if float(value) < 0:
            raise ValueError("Quilometragem inválida.")
        self.__quilometragem = float(value)


    # -- CONSUMO MÉDIO --
    @property
    def consumo_medio_km_l(self):
        return self.__consumo_medio_km_l

    @consumo_medio_km_l.setter
    def consumo_medio_km_l(self, value):
        if float(value) <= 0:
            raise ValueError("Consumo médio inválido.")
        self.__consumo_medio_km_l = float(value)


    # -- QTD LITROS --
    @property
    def qtd_litros(self):
        return self.__qtd_litros

    @qtd_litros.setter
    def qtd_litros(self, value):
        if int(value) <= 0:
            raise ValueError("Quantidade de litros inválida.")
        self.__qtd_litros = int(value)


    # -- TIPO COMBUSTÍVEL --
    @property
    def tipo_combustivel(self):
        return self.__tipo_combustivel
    
    @tipo_combustivel.setter
    def tipo_combustivel(self, value):
        try:
            Tipo_combustivel(value)
        except:
            raise ValueError("Tipo de combustível inválido.")
        self.__tipo_combustivel = value


    # -- STATUS --
    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        try:
            Veiculo_status(value)
        except:
            raise ValueError("Status inválido.")
        self.__status = value
