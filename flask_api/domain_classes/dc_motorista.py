from datetime import date
from flask_api.domain_classes.dc_pessoa import Pessoa
from flask_api.models.enums import Status_motorista


class Motorista(Pessoa):

    def __init__(self, id, nome, cpf, cat_cnh, exp_anos, disponibilidade, cnh_valido_ate):
        super().__init__(id=id, nome=nome, cpf=cpf)

        # setters (cada um faz sua validação)
        self.cat_cnh = cat_cnh
        self.exp_anos = exp_anos
        self.disponibilidade = disponibilidade
        self.cnh_valido_ate = cnh_valido_ate

    # -----------------------
    # CAT CNH
    # -----------------------
    @property
    def cat_cnh(self):
        return self._cat_cnh

    @cat_cnh.setter
    def cat_cnh(self, value):
        if value not in ("A", "B", "C", "D", "E"):
            raise ValueError("Categoria de CNH inválida.")
        self._cat_cnh = value

    # -----------------------
    # EXP ANOS
    # -----------------------
    @property
    def exp_anos(self):
        return self._exp_anos

    @exp_anos.setter
    def exp_anos(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Experiência inválida.")
        self._exp_anos = value

    # -----------------------
    # DISPONIBILIDADE
    # -----------------------
    @property
    def disponibilidade(self):
        return self._disponibilidade

    @disponibilidade.setter
    def disponibilidade(self, value):
        if hasattr(self, "_disponibilidade") and value == self._disponibilidade:
            raise ValueError("O motorista já está neste estado.")
        if value not in ("ATIVO", "INATIVO"):
            raise ValueError("Status de motorista inválido.")
        self._disponibilidade = value

    # -----------------------
    # CNH VALIDO ATÉ
    # -----------------------
    @property
    def cnh_valido_ate(self):
        return self._cnh_valido_ate

    @cnh_valido_ate.setter
    def cnh_valido_ate(self, value):
        if not isinstance(value, date):
            raise ValueError("A validade da CNH deve ser uma data.")
        if value < date.today():
            raise ValueError("CNH vencida.")
        self._cnh_valido_ate = value
