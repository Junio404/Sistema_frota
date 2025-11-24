class Manutencao:
    def __init__(self, id: int, placa_fk: str, tipo: str, data, custo: float,
                 descricao: str, status: str):

        self.__id = id
        self.__placa_fk = placa_fk
        self.__tipo = tipo
        self.__data = data
        self.__custo = custo
        self.__descricao = descricao
        self.__status = status

    @property
    def id(self):
        return self.__id

    @property
    def placa_fk(self):
        return self.__placa_fk

    @property
    def tipo_manutencao(self):
        return self.__tipo
    
    @property
    def data_manutencao(self):
        return self.__data

    @property
    def custo_manutencao(self):
        return self.__custo
    
    @property
    def descricao_manutencao(self):
        return self.__descricao

    #STATUS
    @property
    def status_manutencao(self):
        return self.__status
        
    @status_manutencao.setter
    def status_manutencao(self, novo_status):
        if novo_status == self.__status:
            raise ValueError("O veículo já está nesse estado")
        
        if novo_status.upper() not in ("MANUTENÇÃO", "CONCLUÍDA"):
            raise ValueError("Estado de manutenção inválida!")
        self.__status = novo_status
        
            
        
