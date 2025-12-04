import sqlite3
from config import Config
from flask_api.domain_classes.dc_motorista import Motorista
from flask_api.domain_classes.dc_pessoa import Pessoa


# ---------------------------------------------------------
# FUNÇÃO AUXILIAR — cria objeto Motorista a partir de linha do BD
# ---------------------------------------------------------
def _row_to_motorista(row):
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
        return _row_to_motorista(row)


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
        return [_row_to_motorista(r) for r in rows]


# ---------------------------------------------------------
# ATUALIZAR MOTORISTA
# ---------------------------------------------------------
def atualizar_motorista(motorista: Motorista):
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # UPDATE PESSOA
        cur.execute(
            """UPDATE PESSOA
               SET NOME = ?, CPF = ?
               WHERE ID = ?
            """,
            (motorista.nome, motorista.cpf, motorista.id)
        )

        # UPDATE MOTORISTA
        cur.execute(
            """UPDATE MOTORISTA
               SET CAT_CNH = ?, EXP_ANOS = ?, DISPONIBILIDADE = ?, CNH_VALIDO_ATE = ?
               WHERE ID = ?
            """,
            (
                motorista.cat_cnh,
                motorista.exp_anos,
                motorista.disponibilidade,
                motorista.cnh_valido_ate,
                motorista.id,
            )
        )

        conn.commit()
