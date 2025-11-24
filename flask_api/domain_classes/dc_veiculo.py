class Veiculo:
    def __init__(self, placa: str, modelo_fk: int, tipo_veiculo: str, ano: int,
                 quilometragem: float, consumo_medio: float, status: str):

        self.__placa = placa
        self.__modelo_fk = modelo_fk
        self.__tipo_veiculo = tipo_veiculo
        self.__ano = ano
        self.__quilometragem = quilometragem
        self.__consumo_medio = consumo_medio
        self.__status = status

    @property
    def placa(self):
        return self.__placa

    @property
    def modelo_fk(self):
        return self.__modelo_fk

    @property
    def tipo_veiculo(self):
        return self.__tipo_veiculo

    @property
    def ano(self):
        return self.__ano

    @ano.setter
    def ano(self, value):
        if value < 1980:
            raise ValueError("Ano inválido.")
        self.__ano = value

    @property
    def quilometragem(self):
        return self.__quilometragem
    
    @quilometragem.setter
    def quilometragem(self, value: int):
        if not value:
            raise ValueError("Valor inválido.")
        try:
            float(value)
            self.value = value
        except ValueError:
            raise ValueError("Valor de quilometragem inválido.")

    @quilometragem.setter
    def quilometragem(self, value):
        if value < 0:
            raise ValueError("Quilometragem inválida.")
        self.__quilometragem = value

    @property
    def consumo_medio(self):
        return self.__consumo_medio

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if value not in ("ATIVO", "INATIVO", "MANUTENCAO"):
            raise ValueError("Status inválido.")
        self.__status = value
