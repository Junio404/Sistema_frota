import sqlite3
from datetime import date, datetime
from config import Config
from flask_api.domain_classes.dc_abastecimento import Abastecimento
from flask_api.models.enums import Tipo_evento



# ------------- FUNÇÃO AUXILIAR — cria objeto Abastecimento a partir da linha do BD -------------

def _row_to_abastecimento(row):
    if row is None:
        return None

    (
        id,
        placa_fk,
        tipo_combustivel,
        data,
        litros,
        valor_pago,
        hodometro
    ) = row

    return Abastecimento(
        id=id,
        placa_fk=placa_fk,
        tipo_combustivel=tipo_combustivel,
        data=datetime.strptime(data, "%Y-%m-%d").date(),
        litros=litros,
        valor=valor_pago,
        hodometro=hodometro
    )



# ------------- BUSCAR TIPO DE COMBUSTÍVEL PELO VEÍCULO -------------

def buscar_tipo_combustivel(placa: str) -> str | None:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT TIPO_COMBUSTIVEL
            FROM VEICULO
            WHERE PLACA = ?
            """,
            (placa,)
        )

        row = cur.fetchone()
        return row[0] if row else None



# ------------- PEGAR QUANTIDADE DE LITROS CADASTRADA DO VEÍCULO -------------

def get_qtd_litros_abastecimento(placa: str) -> float | None:
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            """
            SELECT QTD_LITROS
            FROM VEICULO
            WHERE PLACA = ?
            """,
            (placa,)
        )

        row = cur.fetchone()
        return float(row["QTD_LITROS"]) if row else None



# ------------- FUNÇÃO DE NEGÓCIO: cálculo do valor a pagar -------------

def valor_a_pagar(tipo_combustivel: str, litros: int) -> float:

    precos = {
        "GASOLINA": 5.89,
        "ETANOL": 4.29,
        "DIESEL": 6.79
    }

    if litros <= 0:
        raise ValueError("Valor para litros inválido.")

    if tipo_combustivel not in precos:
        raise ValueError("Tipo de combustível inválido.")

    return precos[tipo_combustivel] * litros


def validar_litros_qtd_combustivel(litros: float, qtd_combustivel: float):
    """
    Valida se a quantidade de litros abastecidos não ultrapassa
    a capacidade máxima do tanque do veículo.
    """

    if litros <= 0:
        raise ValueError("A quantidade de litros deve ser maior que zero.")

    if qtd_combustivel is None:
        raise ValueError("Não foi possível determinar a capacidade do tanque do veículo.")

    if litros > qtd_combustivel:
        raise ValueError(
            f"Quantidade de litros excede a capacidade do tanque. "
            f"Máximo permitido: {qtd_combustivel}L."
        )

    return True


def get_quilometragem_atual_abastecimento(placa: str) -> float: 
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?",
            (placa,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Veículo não encontrado.")
        return float(row["QUILOMETRAGEM"])
    
def atualizar_litros_combustivel_abastecimento(litros: float, qtd_atual: float, placa: str) -> float:    
    with sqlite3.connect(Config.DATABASE) as conn:
        novo_nivel_combustivel = litros + qtd_atual
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE VEICULO SET QTD_LITROS = ? WHERE PLACA = ?
        """, (novo_nivel_combustivel, placa))

        

    
    



# ------------- INSERIR ABASTECIMENTO -------------

def inserir_abastecimento(abastecimento: Abastecimento):
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO ABASTECIMENTO (
                PLACA_FK,
                TIPO_COMBUSTIVEL,
                DATA,
                LITROS,
                VALOR_PAGO,
                HODOMETRO
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                abastecimento.placa_fk,
                abastecimento.tipo_combustivel,
                abastecimento.data.strftime("%Y-%m-%d"),
                abastecimento.litros,
                abastecimento.valor_pago,
                abastecimento.hodometro
            )
        )

        conn.commit()



# BUSCAR ABASTECIMENTO POR ID

def buscar_abastecimento_por_id(id_abastecimento: int) -> Abastecimento | None:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                ID,
                PLACA_FK,
                TIPO_COMBUSTIVEL,
                DATA,
                LITROS,
                VALOR_PAGO,
                HODOMETRO
            FROM ABASTECIMENTO
            WHERE ID = ?
            """,
            (id_abastecimento,)
        )

        row = cur.fetchone()
        return _row_to_abastecimento(row)



# ------------- LISTAR TODOS OS ABASTECIMENTOS -------------

def listar_abastecimentos() -> list[Abastecimento]:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                ID,
                PLACA_FK,
                TIPO_COMBUSTIVEL,
                DATA,
                LITROS,
                VALOR_PAGO,
                HODOMETRO
            FROM ABASTECIMENTO
            ORDER BY DATA DESC
            """
        )

        rows = cur.fetchall()
        return [_row_to_abastecimento(r) for r in rows]



def insert_evento_abastecimento(abastecimento):
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        resumo = (
            f"Abastecimento de {abastecimento.litros}L "
            f"({abastecimento.tipo_combustivel})"
        )

        observacao = (
            f"Valor pago: R$ {abastecimento.valor_pago:.2f} | "
            f"Hodômetro: {abastecimento.hodometro}"
        )

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO HISTORICO_EVENTO_VEICULO
            (PLACA_FK, TIPO_EVENTO, DATA_EVENTO, RESUMO, VALOR_ASSOCIADO, OBSERVACAO)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            abastecimento.placa_fk,
            Tipo_evento.ABASTECIMENTO.value,
            date.today().isoformat(),
            resumo,
            abastecimento.valor_pago,
            observacao
        ))