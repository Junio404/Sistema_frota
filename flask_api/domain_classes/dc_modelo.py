class Modelo:
    def __init__(self, id: int, nome_modelo: str, marca_fk: int):
        self.__id = id
        self.__nome_modelo = nome_modelo
        self.__marca_fk = marca_fk

    @property
    def id(self):
        return self.__id

    @property
    def nome_modelo(self):
        return self.__nome_modelo

    @nome_modelo.setter
    def nome_modelo(self, value):
        if not value:
            raise ValueError("Nome do modelo inválido.")
        self.__nome_modelo = value

    @property
    def marca_fk(self):
        return self.__marca_fk
