from datetime import datetime

class Abastecimento:
    def __init__(self, tipo_combustivel: str, litros: float, valor_pago: float):
        self.tipo_combustivel = tipo_combustivel
        self.litros = litros
        self.valor_pago = valor_pago
        self.data_abastecimento = datetime.now()
        
        
    def calcular_consumo():
        '''
        Calcula-se o consumo médio do veículo que abasteceu
        '''
    def verificar_padrao_consumo():
        '''
        Verifica se o consumo do veículo está no padrão descrito no projeto
        '''
    def exibir_veiculos_fora_do_padrao():
        '''
        Gera uma lista dos veículos que estão irregulares na questão do consumo médio
        '''
    def registra_abastecimento():
        '''
        Atualiza o histórico de abastecimento
        '''