class Abastecimento:
    def __init__(self, id: int, placa_fk: str, tipo_combustivel: str, data,
                 litros: float, valor_pago: float, hodometro: float):

        self.__id = id
        self.__placa_fk = placa_fk
        self.__tipo_combustivel = tipo_combustivel
        self.__data = data
        self.__litros = litros
        self.__valor_pago = valor_pago
        self.__hodometro = hodometro
        

    #ID
    @property
    def id(self):
        return self.__id

    #PLACA
    @property
    def placa_fk(self):
        return self.__placa_fk



    @property
    def tipo_combustivel(self):
        return self.__tipo_combustivel

    @property
    def data(self):
        return self.__data

    @property
    def litros(self):
        return self.__litros

    @property
    def valor_pago(self):
        return self.__valor_pago

    @property
    def hodometro(self):
        return self.__hodometro