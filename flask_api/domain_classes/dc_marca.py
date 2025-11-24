class Marca:
    def __init__(self, id: int, nome: str):
        self.__id = id
        self.__nome = nome

    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, value):
        if not value:
            raise ValueError("Nome da marca inválido.")
        if value in ("@","#","!","$","%", "¨", "&","*","(",")","[","]",",",".",";",":","<",">","{","}","º","°","?", "+", "-", "_","§", "=", "'"):
            raise ValueError("Nome inválido de marca")
        self.__nome = value
