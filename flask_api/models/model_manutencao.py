from datetime import datetime

class Manutencao:
    def __init__(self, tipo: str, id_veiculo: int, custo: float, descricao: str):
        self.tipo = tipo
        self.id_veiculo = id_veiculo
        self.data_manutencao = datetime.now()
        self.custo = custo
        self.descricao = descricao
        
        
    def marcar_veiculo_manutencao():
        '''
        Marca o veículo como "em manutenção"
        '''
    def liberar_veiculo():
        '''
        Libera o veículo para viagens
        '''
    def atualizar_historico_manutencao():
        '''
        Atualiza a tabela do histórico de manutenção com todas as informações de manutenção
        '''
    def registra_manutencao():
        '''
        Atualiza o histórico de manutencao
        '''