class Historico_evento_veiculo:
    def __init__(self, id: int, placa_fk: str, tipo_evento: str, data_evento,
                 resumo: str, valor_associado: float, observacao: str):

        self.__id = id
        self.__placa_fk = placa_fk
        self.__tipo_evento = tipo_evento
        self.__data_evento = data_evento
        self.__resumo = resumo
        self.__valor_associado = valor_associado
        self.__observacao = observacao


    @property
    def id(self):
        return self.__id

    @property
    def placa_fk(self):
        return self.__placa_fk

    @property
    def tipo_evento(self):
        return self.__tipo_evento

    @property
    def data_evento(self):
        return self.__data_evento

    @property
    def resumo(self):
        return self.__resumo

    @property
    def valor_associado(self):
        return self.__valor_associado

    @property
    def observacao(self):
        return self.__observacao