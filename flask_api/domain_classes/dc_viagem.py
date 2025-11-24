class Viagem:
    def __init__(self, id: int, placa_fk: str, cpf_fk: str, origem: str, destino: str,
                 distancia_km: float, data_saida, data_chegada,
                 hodometro_saida: float, hodometro_chegada: float):

        self.__id = id
        self.__placa_fk = placa_fk
        self.__cpf_fk = cpf_fk
        self.__origem = origem
        self.__destino = destino
        self.__distancia_km = distancia_km
        self.__data_saida = data_saida
        self.__data_chegada = data_chegada
        self.__hodometro_saida = hodometro_saida
        self.__hodometro_chegada = hodometro_chegada


    @property
    def id(self):
        return self.__id

    @property
    def placa_fk(self):
        return self.__placa_fk

    @property
    def cpf_fk(self):
        return self.__cpf_fk

    @property
    def origem(self):
        return self.__origem

    @property
    def destino(self):
        return self.__destino

    @property
    def distancia_km(self):
        return self.__distancia_km

    @property
    def data_saida(self):
        return self.__data_saida

    @property
    def data_chegada(self):
        return self.__data_chegada

    @property
    def hodometro_saida(self):
        return self.__hodometro_saida

    @property
    def hodometro_chegada(self):
        return self.__hodometro_chegada