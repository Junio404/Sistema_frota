import sqlite3
from config import Config
from flask_api.domain_classes.dc_motorista import Motorista
from flask_api.domain_classes.dc_pessoa import Pessoa


# ---------------------------------------------------------
# FUNÇÃO AUXILIAR — cria objeto Motorista a partir de linha do BD
# ---------------------------------------------------------
def row_to_motorista(row):
    if row is None:
        return None
    
    (
        id,
        nome,
        cpf,
        cat_cnh,
        exp_anos,
        disponibilidade,
        cnh_valido_ate
    ) = row

    return Motorista(
        id=id,
        nome=nome,
        cpf=cpf,
        cat_cnh=cat_cnh,
        exp_anos=exp_anos,
        disponibilidade=disponibilidade,
        cnh_valido_ate=cnh_valido_ate
    )


# ---------------------------------------------------------
# VERIFICAR SE CPF EXISTE
# ---------------------------------------------------------
def cpf_existe(cpf: str) -> bool:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM PESSOA WHERE CPF = ?", 
            (cpf,)
        )
        return cur.fetchone() is not None


# ---------------------------------------------------------
# INSERIR MOTORISTA
# ---------------------------------------------------------
def inserir_motorista(motorista: Motorista):
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # 1 — INSERE NA TABELA PESSOA
        cur.execute(
            """
            INSERT INTO PESSOA (NOME, CPF)
            VALUES (?, ?)
            """,
            (motorista.nome, motorista.cpf)
        )
        pessoa_id = cur.lastrowid  # chave primária gerada

        # 2 — INSERE NA TABELA MOTORISTA
        cur.execute(
            """
            INSERT INTO MOTORISTA (ID, CPF, CAT_CNH, EXP_ANOS, DISPONIBILIDADE, CNH_VALIDO_ATE)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                pessoa_id,
                motorista.cpf,
                motorista.cat_cnh,
                motorista.exp_anos,
                motorista.disponibilidade,
                motorista.cnh_valido_ate
            )
        )

        conn.commit()


# ---------------------------------------------------------
# BUSCAR MOTORISTA POR ID
# ---------------------------------------------------------
def buscar_motorista_por_id(id_motorista: int) -> Motorista | None:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                P.ID,
                P.NOME,
                P.CPF,
                M.CAT_CNH,
                M.EXP_ANOS,
                M.DISPONIBILIDADE,
                M.CNH_VALIDO_ATE
            FROM MOTORISTA M
            INNER JOIN PESSOA P ON P.ID = M.ID
            WHERE M.ID = ?
            """,
            (id_motorista,)
        )

        row = cur.fetchone()
        return row_to_motorista(row)


# ---------------------------------------------------------
# LISTAR TODOS OS MOTORISTAS
# ---------------------------------------------------------
def listar_motoristas() -> list[Motorista]:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                P.ID,
                P.NOME,
                P.CPF,
                M.CAT_CNH,
                M.EXP_ANOS,
                M.DISPONIBILIDADE,
                M.CNH_VALIDO_ATE
            FROM MOTORISTA M
            INNER JOIN PESSOA P ON P.ID = M.ID
            ORDER BY P.NOME
            """
        )

        rows = cur.fetchall()
        return [row_to_motorista(r) for r in rows]


# ---------------------------------------------------------
# ATUALIZAR MOTORISTA
# ---------------------------------------------------------
def atualizar_motorista(id: int, dados: dict):
    """
    dados = {
        "CAT_CNH": "C",
        "EXP_ANOS": 10,
        ...
    }
    Apenas os campos presentes no dict serão atualizados.
    """

    if not dados:
        return  # nada pra atualizar

    keys = ", ".join([f"{campo} = ?" for campo in dados.keys()])
    values = list(dados.values())

    query = f"UPDATE MOTORISTA SET {keys} WHERE ID = ?"

    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.execute(query, (*values, id))
        conn.commit()
        

def buscar_cat_cnh(cpf: str):
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            """
        SELECT CAT_CNH 
        FROM MOTORISTA
        WHERE CPF = ?
            """, (cpf,)
        )
        row = cur.fetchone()
        return row_to_motorista(row)
    
    

def deletar_motorista(cpf: str):
    
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_key = ON")
        cur = conn.cursor()
        
        cur.execute("""
        DELETE FROM PESSOA WHERE CPF = ?         
                    """, (cpf,))

        
        cur.execute("""
        DELETE FROM MOTORISTA WHERE CPF = ?            
                    """, (cpf,))