import sqlite3
from datetime import date
from config import Config
from flask_api.models.enums import (
    Status_motorista,
    Status_viagem,
    Veiculo_status,
    Tipo_evento
)


DB_PATH = Config.DATABASE


# ------------ cria conexão com o banco -------------
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------- BUSCAS SIMPLES ------------------
# ------------ busca motorista pelo CPF -------------
def repo_get_motorista(cpf: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM MOTORISTA WHERE CPF = ?
        """, (cpf,))
        row = cur.fetchone()
        return dict(row) if row else None


# ------------ busca veículo e tipo do modelo -------------
def repo_get_veiculo(placa: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT V.*, M.TIPO_VEICULO
            FROM VEICULO V
            JOIN MODELO M ON M.ID = V.MODELO_FK
            WHERE PLACA = ?
        """, (placa,))
        row = cur.fetchone()
        return dict(row) if row else None


# ------------ retorna quilometragem do veículo -------------
def repo_get_quilometragem(placa: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?", (placa,))
        row = cur.fetchone()
        return float(row["QUILOMETRAGEM"]) if row else None


# ------------ retorna consumo médio e litros atuais -------------
def repo_get_consumo(placa: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT CONSUMO_MEDIO_KM_L, QTD_LITROS
            FROM VEICULO
            WHERE PLACA = ?
        """, (placa,))
        row = cur.fetchone()
        return (float(row["CONSUMO_MEDIO_KM_L"]), float(row["QTD_LITROS"])) if row else None


# ------------ obtém quilometragem usando conexão existente -------------
def get_quilometragem_atual(conn: sqlite3.Connection, placa: str) -> float: 
    cur = conn.cursor() 
    cur.execute("SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?", (placa,)) 
    row = cur.fetchone() 
    if not row:
        raise ValueError("Veículo não encontrado.") 
    return float(row["QUILOMETRAGEM"])


# ----------------------- UPDATES ---------------------------

# ------------ atualiza nível de combustível -------------
def repo_update_combustivel(conn, placa: str, novo_nivel: float):
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO SET QTD_LITROS = ? WHERE PLACA = ?
    """, (novo_nivel, placa))


# ------------ atualiza status do veículo e hodômetro -------------
def repo_update_veiculo_viagem(conn, placa: str, novo_hodometro: float):
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO SET STATUS = ?, QUILOMETRAGEM = ?
        WHERE PLACA = ?
    """, (Veiculo_status.EM_VIAGEM.value, novo_hodometro, placa))


# ------------ atualiza motorista para status em viagem -------------
def repo_update_motorista_viagem(conn, cpf: str):
    cur = conn.cursor()
    cur.execute("""
        UPDATE MOTORISTA SET DISPONIBILIDADE = ?
        WHERE CPF = ?
    """, (Status_motorista.EM_VIAGEM.value, cpf))


# ------------------------- INSERTS ---------------------------------
# ------------ registra nova viagem -------------
def repo_insert_viagem(conn, viagem, hodometro_atual, hodometro_final):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO VIAGEM 
        (PLACA_FK, CPF_FK, ORIGEM, DESTINO, DISTANCIA_KM,
         DATA_SAIDA, DATA_CHEGADA, HODOMETRO_SAIDA, HODOMETRO_CHEGADA, STATUS)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        viagem.placa_fk,
        viagem.cpf_fk,
        viagem.origem,
        viagem.destino,
        viagem.distancia_km,
        date.today().isoformat(),
        viagem.data_chegada.isoformat(),
        hodometro_atual,
        hodometro_final,
        Status_viagem.EM_ANDAMENTO.value
    ))


# ------------ registra evento da viagem no histórico do veículo -------------
def repo_insert_evento_viagem(conn, viagem):
    resumo = f"Viagem de {viagem.origem} para {viagem.destino}"

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO HISTORICO_EVENTO_VEICULO
        (PLACA_FK, TIPO_EVENTO, DATA_EVENTO, RESUMO, VALOR_ASSOCIADO, OBSERVACAO)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        viagem.placa_fk,
        Tipo_evento.VIAGEM.value,
        date.today().isoformat(),
        resumo,
        viagem.distancia_km,
        f"Motorista: {viagem.cpf_fk}"
    ))



def verificar_conclusao_viagem():
    """
    Verifica viagens cujo término já chegou,
    marcando como concluídas e reativando veículo e motorista.
    """

    data_hoje_iso = date.today().isoformat()

    conn = None
    try:
        conn = sqlite3.connect(Config.DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        
        # ----------------- 1 — Buscar viagens que deveriam ser concluídas --------------
        
        cur.execute("""
            SELECT ID, PLACA_FK, CPF_FK
            FROM VIAGEM
            WHERE STATUS = ?
              AND DATA_CHEGADA <= ?
        """, (Status_viagem.EM_ANDAMENTO.value, data_hoje_iso))

        viagens_a_concluir = cur.fetchall()
        

        if not viagens_a_concluir:
            print("Nenhuma viagem pendente de conclusão encontrada.")
            return

        
        # ------- 2 — Atualizar cada viagem, motorista e veículo -----------
        
        for id_viagem, placa, cpf in viagens_a_concluir:

            # VIAGEM -> CONCLUÍDA
            cur.execute("""
                UPDATE VIAGEM
                SET STATUS = ?
                WHERE ID = ?
            """, (Status_viagem.CONCLUIDA.value, id_viagem))

            # VEÍCULO -> ATIVO
            cur.execute("""
                UPDATE VEICULO
                SET STATUS = ?
                WHERE PLACA = ?
            """, (Veiculo_status.ATIVO.value, placa))

            # MOTORISTA -> ATIVO
            cur.execute("""
                UPDATE MOTORISTA
                SET DISPONIBILIDADE = ?
                WHERE CPF = ?
            """, (Status_motorista.ATIVO.value, cpf))

            print(f"✅ Viagem {id_viagem} concluída. Veículo {placa} e motorista {cpf} ativados.")

        conn.commit()
        print("✅ Todas as viagens concluídas com sucesso.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Erro ao verificar conclusão de viagem: {e}")
        raise

    finally:
        if conn:
            conn.close()
