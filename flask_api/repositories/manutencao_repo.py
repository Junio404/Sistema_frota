import sqlite3
from datetime import date
from config import Config

from flask_api.domain_classes.dc_manutencao import Manutencao
from flask_api.models.enums import Tipo_manutencao, Status_manutencao, Veiculo_status, Tipo_evento


# ---------- Custos fixos para manutenções preventivas ----------
CUSTOS_PREVENTIVA = {
    "MOTO": 150.00,
    "CARRO": 350.00,
    "CAMINHAO": 900.00
}


def buscar_tipo_veiculo_placa(placa: str):
    # ---------- Busca o tipo de veículo através da placa ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        
        cur.execute("""
        SELECT TIPO_VEICULO 
        FROM VEICULO
        WHERE PLACA = ?
        """, (placa,))
        
        row = cur.fetchone()
        return row[0] if row else None        


# ---------- Converte uma linha do BD para objeto Manutencao ----------
def _row_to_manutencao(row):
    if row is None:
        return None

    (
        id,
        placa_fk,
        tipo,
        data_inicio,
        data_conclusao,
        custo,
        descricao,
        status
    ) = row

    return Manutencao(
        id=id,
        placa_fk=placa_fk,
        tipo_manutencao=Tipo_manutencao(tipo),
        data_inicio=data_inicio,
        data_conclusao=data_conclusao,
        custo=custo,
        descricao=descricao,
        status_manutencao=Status_manutencao(status)
    )


def atualizar_status_veiculo_manutencao(placa: str):
    # ---------- Muda status do veículo para MANUTENCAO ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.execute("""
            UPDATE VEICULO SET STATUS = ?
            WHERE PLACA = ?
        """, (Veiculo_status.MANUTENCAO.value, placa))


def inserir_manutencao(dados) -> Manutencao:
    placa = dados.placa_fk
    tipo = dados.tipo_manutencao
    tipo_veiculo = buscar_tipo_veiculo_placa(placa)

    data_inicio = date.today()

    # ---------- Define valores com base no tipo de manutenção ----------
    custo = None
    descricao = None
    data_conclusao = None
    status = Status_manutencao.EM_ANDAMENTO

    if tipo == Tipo_manutencao.PREVENTIVA:
        custo = CUSTOS_PREVENTIVA.get(tipo_veiculo)
        descricao = "Revisão preventiva"
        data_conclusao = dados.data_conclusao
    else:
        custo = dados.custo
        descricao = dados.descricao
        data_conclusao = dados.data_conclusao

    # ---------- Cria objeto Manutencao ----------
    manutencao = Manutencao(
        id=None,
        placa_fk=placa,
        tipo_manutencao=tipo,
        data_inicio=data_inicio,
        data_conclusao=data_conclusao,
        custo=custo,
        descricao=descricao,
        status_manutencao=status
    )
    
    # ---------- Converte datas para formato ISO ----------
    data_inicio_sql = manutencao.data_inicio.isoformat()
    data_conclusao_sql = manutencao.data_conclusao.isoformat() if manutencao.data_conclusao else None

    conn = None
    try:
        # ---------- Abre conexão ----------
        conn = sqlite3.connect(Config.DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # ---------- Insere manutenção na tabela ----------
        cur.execute(
            """
            INSERT INTO MANUTENCAO 
            (
                PLACA_FK,
                TIPO_MANUTENCAO,
                DATA_INICIO,
                DATA_CONCLUSAO,
                CUSTO,
                DESCRICAO,
                STATUS_MANUTENCAO
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                manutencao.placa_fk,
                manutencao.tipo_manutencao.value,
                data_inicio_sql,
                data_conclusao_sql,
                manutencao.custo,
                manutencao.descricao,
                manutencao.status_manutencao.value
            )
        )
        
        manutencao._id = cur.lastrowid

        conn.commit()
        return manutencao

    except Exception as e:
        # ---------- Desfaz alterações em caso de erro ----------
        if conn:
            conn.rollback()
        raise e

    finally:
        # ---------- Fecha conexão ----------
        if conn:
            conn.close()


# ---------- Buscar manutenção pelo ID ----------
def buscar_manutencao_por_id(id_manutencao: int) -> Manutencao | None:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                ID,
                PLACA_FK,
                TIPO_MANUTENCAO,
                DATA_INICIO,
                DATA_CONCLUSAO,
                CUSTO,
                DESCRICAO,
                STATUS_MANUTENCAO
            FROM MANUTENCAO
            WHERE ID = ?
            """,
            (id_manutencao,)
        )

        row = cur.fetchone()
        return _row_to_manutencao(row)


# ---------- Listar todas as manutenções ----------
def listar_manutencoes() -> list[Manutencao]:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                ID,
                PLACA_FK,
                TIPO_MANUTENCAO,
                DATA_INICIO,
                DATA_CONCLUSAO,
                CUSTO,
                DESCRICAO,
                STATUS_MANUTENCAO
            FROM MANUTENCAO
            ORDER BY DATA_INICIO DESC
            """
        )

        rows = cur.fetchall()
        return [_row_to_manutencao(r) for r in rows]


def repo_insert_evento_manutencao(manutencao):
    # ---------- Cria registro de evento no histórico de veículo ----------
    with sqlite3.connect(Config.DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        
        if manutencao.tipo_manutencao.value == "PREVENTIVA":
            resumo = "Início de Manutenção Preventiva"
        else:
            resumo = "Início de Manutenção Corretiva"

        observacao = f"Custo estimado/definido: R$ {manutencao.custo:.2f}. Descrição: {manutencao.descricao}"

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO HISTORICO_EVENTO_VEICULO
            (PLACA_FK, TIPO_EVENTO, DATA_EVENTO, RESUMO, VALOR_ASSOCIADO, OBSERVACAO)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            manutencao.placa_fk,
            Tipo_evento.MANUTENCAO.value,
            manutencao.data_inicio.isoformat(),
            resumo,
            manutencao.custo,
            observacao
        ))


# ---------- Verifica e conclui manutenções cuja data já chegou ----------
def verificar_conclusao_manutencao():
    """
    Atualiza manutenções que atingiram a data de conclusão,
    marcando-as como CONCLUIDA e ativando o veículo novamente.
    """
    
    data_hoje_iso = date.today().isoformat()

    conn = None
    try:
        conn = sqlite3.connect(Config.DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # ---------- Busca manutenções que já deveriam ter sido concluídas ----------
        cur.execute("""
            SELECT ID, PLACA_FK, CUSTO
            FROM MANUTENCAO
            WHERE STATUS_MANUTENCAO = ? 
            AND DATA_CONCLUSAO <= ?
        """, (Status_manutencao.EM_ANDAMENTO.value, data_hoje_iso))
        
        manutencoes_a_concluir = cur.fetchall()

        if not manutencoes_a_concluir:
            print("Nenhuma manutenção pendente de conclusão encontrada.")
            return

        for id_manutencao, placa, custo in manutencoes_a_concluir:

            # ---------- Atualiza status da manutenção ----------
            cur.execute("""
                UPDATE MANUTENCAO
                SET STATUS_MANUTENCAO = ?
                WHERE ID = ?
            """, (Status_manutencao.CONCLUIDA.value, id_manutencao))

            # ---------- Ativa o veículo ----------
            cur.execute("""
                UPDATE VEICULO
                SET STATUS = ?
                WHERE PLACA = ?
            """, (Veiculo_status.ATIVO.value, placa))

            print(f"✅ Status atualizados para Manutenção ID {id_manutencao} e veículo {placa}.")

        conn.commit()

        print("✅ Todos os eventos de conclusão registrados com sucesso.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Erro ao verificar conclusão de manutenção: {e}")
        raise

    finally:
        if conn:
            conn.close()
