import sqlite3
from datetime import datetime
from typing import Optional, Dict
from config import Config

DB_PATH = Config.DATABASE 



#--------------------- CONEXÃO COM O BANCO -----------------------------

def conectar(db_path: str = DB_PATH):
    """Cria e retorna uma nova conexão com o banco de dados."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def placa_existe(placa: str) -> bool:
    """
    Verifica no banco de dados se a placa existe
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        
        cur.execute("""
        SELECT PLACA
        FROM VEICULO
        where placa = ?         
                    """, (placa,))
        
        row = cur.fetchone()
        return row[0] if row else None
    

def buscar_tipo_combustivel(placa:str):
    """
    Busca o tipo de combustivel do veiculo através da placa
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        
        cur.execute("""
        SELECT tipo_COMBUSTIVEL
        FROM VEICULO
        where placa = ?         
                    """, (placa,))
        
        row = cur.fetchone()
        return row[0] if row else None
    

def valor_a_pagar(tipo_combustivel: str, litros:int) -> float:
    
    tipo_preço = {
    "GASOLINA": 5.89,
    "ETANOL": 4.29,
    "DIESEL": 6.79
    }
    
    if litros <= 0:
        raise ValueError("Valor para litros inválido")
    
    valor = tipo_preço[tipo_combustivel] * litros
    
    
    return valor



def inserir_abastecimento(data):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute()
        
        cur.execute("""
        INSERT INTO ABASTECIMENTO (
            PLACA_FK,
            TIPO_COMBUSTIVEL,
            DATA,
            LITROS,
            VALOR_PAGO,
            HODOMETRO
        )  VALUES (?, ?, ?, ?, ?, ?)             
                    """, 
        (
            data.placa_fk,
            data.tipo_combustivel,
            data.data,
            data.litros,
            data.valor,
            data.hodometro                    
        ))
        
        conn.commit()
    
    








