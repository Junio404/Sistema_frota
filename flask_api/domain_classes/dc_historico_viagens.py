class Historico_veiculo:
    def __init__(self, id: int, viagem_id_fk: int, registrado_em,
                 status: str, observacao: str):

        self.__id = id
        self.__viagem_id_fk = viagem_id_fk
        self.__registrado_em = registrado_em
        self.__status = status
        self.__observacao = observacao


    @property
    def id(self):
        return self.__id

    @property
    def viagem_id_fk(self):
        return self.__viagem_id_fk

    @property
    def registrado_em(self):
        return self.__registrado_em

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        if value == self.__status:
            raise ValueError("A viagem já está nesse estado")
        if value not in ("EM ANDAMENTO", "CONCLUÍDA"):
            raise ValueError("Valor de status de viagem inválido")
        self.__status = value

    @property
    def observacao(self):
        return self.__observacao