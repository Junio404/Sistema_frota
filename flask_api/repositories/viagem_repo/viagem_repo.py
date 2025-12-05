# repository/repo_viagem.py
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


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================================================
# BUSCAS SIMPLES
# ==============================================================

def repo_get_motorista(cpf: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM MOTORISTA WHERE CPF = ?
        """, (cpf,))
        row = cur.fetchone()
        return dict(row) if row else None


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


def repo_get_quilometragem(placa: str):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?", (placa,))
        row = cur.fetchone()
        return float(row["QUILOMETRAGEM"]) if row else None


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


def get_quilometragem_atual(conn: sqlite3.Connection, placa: str) -> float: 
    """Obtém a quilometragem atual do veículo.""" 
    cur = conn.cursor() 
    cur.execute("SELECT QUILOMETRAGEM FROM VEICULO WHERE PLACA = ?", (placa,)) 
    row = cur.fetchone() 
    if not row: raise ValueError("Veículo não encontrado.") 
    return float(row["QUILOMETRAGEM"])

# ==============================================================
# UPDATES
# ==============================================================

def repo_update_combustivel(conn, placa: str, novo_nivel: float):
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO SET QTD_LITROS = ? WHERE PLACA = ?
    """, (novo_nivel, placa))


def repo_update_veiculo_viagem(conn, placa: str, novo_hodometro: float):
    cur = conn.cursor()
    cur.execute("""
        UPDATE VEICULO SET STATUS = ?, QUILOMETRAGEM = ?
        WHERE PLACA = ?
    """, (Veiculo_status.EM_VIAGEM.value, novo_hodometro, placa))


def repo_update_motorista_viagem(conn, cpf: str):
    cur = conn.cursor()
    cur.execute("""
        UPDATE MOTORISTA SET DISPONIBILIDADE = ?
        WHERE CPF = ?
    """, (Status_motorista.EM_VIAGEM.value, cpf))


# ==============================================================
# INSERTS
# ==============================================================

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


def repo_insert_historico(conn, viagem):
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
