from domain_classes.dc_pessoa import Pessoa

class Motorista(Pessoa):
    def __init__(self, id: int, nome: str, cpf: str,
                 cat_cnh: str, exp_anos: int, disponibilidade: str, cnh_valido_ate):
        
        super().__init__(id, nome, cpf)

        self.__cat_cnh = cat_cnh
        self.__exp_anos = exp_anos
        self.__disponibilidade = disponibilidade
        self.__cnh_valido_ate = cnh_valido_ate

    # CAT CNH
    @property
    def cat_cnh(self):
        return self.__cat_cnh

    @cat_cnh.setter
    def cat_cnh(self, value):
        if value not in ("A", "B", "C", "D", "E"):
            raise ValueError("Categoria de CNH inválida.")
        self._cat_cnh = value

    # EXP ANOS
    @property
    def exp_anos(self):
        return self.__exp_anos

    @exp_anos.setter
    def exp_anos(self, value):
        if value < 0:
            raise ValueError("Experiência inválida.")
        self.__exp_anos = value

    # DISPONIBILIDADE
    @property
    def disponibilidade(self):
        return self.__disponibilidade

    @disponibilidade.setter
    def disponibilidade(self, value):
        if value == self.__disponibilidade:
            raise ValueError("O motorista já está neste estado")
        if value not in ("ATIVO", "INATIVO"):
            raise ValueError("Status de motorista inválido.")
        self.__disponibilidade = value

    # CNH VALIDADE
    @property
    def cnh_valido_ate(self):
        return self.__cnh_valido_ate

    @cnh_valido_ate.setter
    def cnh_valido_ate(self, value):
        from datetime import date
        if value < date.today():
            raise ValueError("CNH vencida.")
        self.__cnh_valido_ate = value
        