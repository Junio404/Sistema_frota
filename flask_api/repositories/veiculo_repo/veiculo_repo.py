import re
import sqlite3
from config import Config


def buscar_tipo_modelo(id_modelo: int):
    """Retorna o tipo do modelo (MOTO, CARRO, CAMINHAO)"""
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            SELECT TIPO_VEICULO
            FROM MODELO
            WHERE ID = ?
        """, (id_modelo,))

        row = cur.fetchone()
        return row[0] if row else None
    
def buscar_qtd_litros(id_modelo: int):
    """Retorna a quantidade de litros a partirr do id"""
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            SELECT QTD_LITROS
            FROM MODELO
            WHERE ID = ?
        """, (id_modelo,))

        row = cur.fetchone()
        return row[0] if row else None

def buscar_consumo_medio(id_modelo: int):
    """Retorna o consumo médio pelo id do modelo"""
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            SELECT CONSUMO_MEDIO_KM_L
            FROM MODELO
            WHERE ID = ?
        """, (id_modelo,))

        row = cur.fetchone()
        return row[0] if row else None



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
                STATUS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.placa.upper(),
            data.modelo_fk,
            data.tipo_veiculo,
            data.ano,
            data.quilometragem,
            data.qtd_litros,
            data.consumo_medio_km_l,
            data.status.value
        ))

        conn.commit()
        
def validar_placa_mercosul(placa: str) -> bool:
    if not placa:
        return False  # evita o AttributeError
    padrao = r'^[A-Z]{3}[0-9][A-Z][0-9]{3}$'
    return re.match(padrao, placa.upper()) is not None
