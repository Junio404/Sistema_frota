
class Veiculo():
    def __init__(self, placa: str, modelo: str, ano: str, quilometragem: float, custo_kml: float, status: str):
        self.__placa = placa
        self.__modelo = modelo
        self.__ano = ano
        self.quilometragem = quilometragem
        self.custo_kml = custo_kml
        self.status = status