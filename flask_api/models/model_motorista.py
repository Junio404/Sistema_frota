from interfaces.interface_pessoa import Pessoa

class Motorista(Pessoa):
    def __init__(self, nome: str, cpf: str, cat_cnh: str, exp_anos: int, disponibilidade: str):
        super().__init__(nome, cpf)
        self.cat_cnh = cat_cnh
        self.exp_anos = exp_anos
        self.disponibilidade = disponibilidade
        
    
    def validar_cnh(nome, cpf):
        '''
        Valida a cnh do motorista e informa qual tipo de veículo ele pode dirigir de acordo com sua categoria.
        '''
        
