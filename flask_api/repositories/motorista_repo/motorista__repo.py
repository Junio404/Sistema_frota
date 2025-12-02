import sqlite3
from config import Config

def inserir_motorista(data):
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # Inserindo na tabela PESSOA
        cur.execute("""
            INSERT INTO PESSOA (CPF, NOME)
            VALUES (?, ?)
        """, (
            data.cpf,
            data.nome
        ))
        # Inserindo na tabela MOTORISTA
        cur.execute("""
            INSERT INTO MOTORISTA (CPF, CAT_CNH, EXP_ANOS, DISPONIBILIDADE, CNH_VALIDO_ATE)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.cpf,
            data.cat_cnh,
            data.exp_anos,
            data.disponibilidade,
            data.cnh_valido_ate
        ))


        conn.commit()


def cpf_existe(cpf: str) -> bool:
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM PESSOA WHERE CPF = ?", (cpf,))
        return cur.fetchone() is not None
    
def validar_cpf(cpf: int) -> bool:
    if len(cpf) == 11:
        return True
    else:
        return False