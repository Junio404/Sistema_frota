import sqlite3
from config import Config
import re

def buscar_dados_modelo(id_modelo: int):
    """Retorna TIPO_VEICULO, QTD_LITROS, CONSUMO_MEDIO_KM_L e TIPO_COMBUSTIVEL de uma vez."""
    
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            SELECT TIPO_VEICULO, QTD_LITROS, CONSUMO_MEDIO_KM_L, TIPO_COMBUSTIVEL
            FROM MODELO
            WHERE ID = ?
        """, (id_modelo,))

        row = cur.fetchone()
        
        if row:
            return {
                "tipo_veiculo": row[0],
                "qtd_litros": row[1],
                "consumo_medio_km_l": row[2],
                "tipo_combustivel": row[3],
            }
        return None


def inserir_veiculo(data):
    """Insere o veículo no banco"""
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO VEICULO (
                PLACA,
                MODELO_FK,
                TIPO_VEICULO,
                ANO,
                QUILOMETRAGEM,
                QTD_LITROS,
                CONSUMO_MEDIO_KM_L,
                TIPO_COMBUSTIVEL,
                STATUS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.placa.upper(),
            data.modelo_fk,
            data.tipo_veiculo,
            data.ano,
            data.quilometragem,
            data.qtd_litros,
            data.consumo_medio_km_l,
            data.tipo_combustivel,
            # CORREÇÃO: Passa o valor string do status (o Pydantic já validou)
            # Use 'data.status' se for string ou 'data.status.value' se for Enum.
            # Assumindo que Pydantic retornou um objeto string ou Enum.value:
            data.status 
        ))

        conn.commit()
        
def validar_placa_mercosul(placa: str) -> bool:
    if not placa:
        return False  # evita o AttributeError
    padrao = r'^[A-Z]{3}[0-9][A-Z][0-9]{3}$'
    return re.match(padrao, placa.upper()) is not None
