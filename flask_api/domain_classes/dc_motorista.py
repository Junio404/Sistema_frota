from dataclasses import dataclass, field
from datetime import date, datetime
from flask_api.domain_classes.dc_pessoa import Pessoa

@dataclass
class Motorista(Pessoa):
    _cat_cnh: str = field(init=False, repr=False)
    _exp_anos: int = field(init=False, repr=False)
    _disponibilidade: str = field(init=False, repr=False)
    _cnh_valido_ate: date = field(init=False, repr=False)

    def __init__(
        self,
        id,
        nome,
        cpf,
        cat_cnh,
        exp_anos,
        disponibilidade,
        cnh_valido_ate
    ):
        super().__init__(id=id, nome=nome, cpf=cpf)

        self.cat_cnh = cat_cnh
        self.exp_anos = exp_anos
        self.disponibilidade = disponibilidade
        self.cnh_valido_ate = cnh_valido_ate

    # ---------------- CAT CNH -------------------
    @property
    def cat_cnh(self):
        return self._cat_cnh

    @cat_cnh.setter
    def cat_cnh(self, value):
        if value not in ("A", "B", "C", "D", "E"):
            raise ValueError("Categoria de CNH inválida.")
        self._cat_cnh = value

    # ------------------- EXP ANOS -------------------
    @property
    def exp_anos(self):
        return self._exp_anos

    @exp_anos.setter
    def exp_anos(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Experiência inválida.")
        self._exp_anos = value

    # ------------------- DISPONIBILIDADE -------------------
    @property
    def disponibilidade(self):
        return self._disponibilidade

    @disponibilidade.setter
    def disponibilidade(self, value):
        if hasattr(self, "_disponibilidade") and value == self._disponibilidade:
            raise ValueError("O motorista já está neste estado.")

        if value not in ("ATIVO", "INATIVO", "EM_VIAGEM"):
            raise ValueError("Status de motorista inválido.")

        self._disponibilidade = value

    # ------------------- CNH VALIDO ATÉ -------------------

    @property
    def cnh_valido_ate(self):
        # É importante usar hasattr() para checar se o atributo existe antes de retornar
        if not hasattr(self, '_cnh_valido_ate'):
            # Isso pode acontecer se o construtor falhar, mas é uma segurança.
            # No seu caso, o problema é a atribuição no setter.
            raise AttributeError("O atributo _cnh_valido_ate não foi inicializado.")
        return self._cnh_valido_ate

    @cnh_valido_ate.setter
    def cnh_valido_ate(self, value):
        data_final = value

        if isinstance(data_final, str):
            try:
                # 1. TENTA CONVERTER A STRING
                data_final = datetime.strptime(data_final, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Formato de data de validade da CNH inválido. Use YYYY-MM-DD.")
        
        # 2. VALIDA O TIPO E A DATA
        if not isinstance(data_final, date):
            # Lança erro se não for string (que já foi tratada) nem objeto date
            raise ValueError("A validade da CNH deve ser uma data.")
        
        if data_final < date.today():
            raise ValueError("CNH vencida.")
            
        # 3. ATRIBUIÇÃO FINAL (CORRIGINDO O ERRO CRÍTICO DE ATRIBUTO)
        self._cnh_valido_ate = data_final