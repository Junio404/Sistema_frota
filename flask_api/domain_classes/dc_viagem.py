# domínio/viagem.py
from datetime import date
from flask_api.models.enums import Status_motorista, Status_viagem, Veiculo_status, Tipo_evento

class Viagem:
    def __init__(self, placa_fk, cpf_fk, origem, destino, distancia_km, data_chegada):
        self.placa_fk = placa_fk
        self.cpf_fk = cpf_fk
        self.origem = origem
        self.destino = destino
        self.distancia_km = distancia_km
        self.data_chegada = data_chegada


    # ------------- Validações de domínio -------------


    @staticmethod
    def validar_motorista_disponivel(status_motorista: str):
        if status_motorista == Status_motorista.INATIVO.value:
            raise ValueError("Motorista INATIVO não pode iniciar viagem.")
        if status_motorista == Status_motorista.EM_VIAGEM.value:
            raise ValueError("Motorista já está em viagem.")

    @staticmethod
    def validar_veiculo_disponivel(status_veiculo: str):
        if status_veiculo == Veiculo_status.INATIVO.value:
            raise ValueError("Veículo INATIVO não pode iniciar viagem.")
        if status_veiculo == Veiculo_status.MANUTENCAO.value:
            raise ValueError("Veículo em manutenção não pode iniciar viagem.")
        if status_veiculo == Veiculo_status.EM_VIAGEM.value:
            raise ValueError("Veículo já está em viagem.")

    @staticmethod
    def validar_categoria_cnh(cat_motorista: str, tipo_veiculo: str):
        ordem = ["A", "B", "C", "D", "E"]
        categoria_minima = {
            "MOTO": "A",
            "CARRO": "B",
            "CAMINHAO": "C"
        }.get(tipo_veiculo)

        if categoria_minima is None:
            raise ValueError(f"Tipo de veículo '{tipo_veiculo}' inválido.")

        if ordem.index(cat_motorista) < ordem.index(categoria_minima):
            raise ValueError(
                f"CNH incompatível. Para dirigir {tipo_veiculo}, "
                f"mínimo é {categoria_minima}, mas motorista possui {cat_motorista}."
            )

    @staticmethod
    def calcular_hodometro(quilometragem_atual: float, distancia_km: float) -> float:
        if distancia_km <= 0:
            raise ValueError("A distância deve ser maior que zero.")
        return quilometragem_atual + distancia_km

    @staticmethod
    def calcular_combustivel(distancia_km: float, consumo_medio: float, qtd_litros_atual: float):
        litros_gastos = distancia_km / consumo_medio
        
        if qtd_litros_atual - litros_gastos < 0:
            raise ValueError("Viagem Longa para a quantidade de litros de combustivel que o carro tem!")
        return qtd_litros_atual - litros_gastos
    

