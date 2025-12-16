import sqlite3
from config import Config
import re
from flask_api.models.enums import Veiculo_status

def buscar_dados_modelo(id_modelo: int):
    with sqlite3.connect(Config.DATABASE) as conn:
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
                "tipo_combustivel": row[3]
            }

        return None


def inserir_veiculo(veiculo):
    with sqlite3.connect(Config.DATABASE) as conn:
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
            veiculo.placa,
            veiculo.modelo_fk,
            veiculo.tipo_veiculo,
            veiculo.ano,
            veiculo.quilometragem,
            veiculo.qtd_litros,
            veiculo.consumo_medio_km_l,
            veiculo.tipo_combustivel,
            veiculo.status
        ))

        conn.commit()

        
def validar_placa_mercosul(placa: str) -> bool:
    if not placa:
        return False  # evita o AttributeError
    padrao = r'^[A-Z]{3}[0-9][A-Z][0-9]{3}$'
    return re.match(padrao, placa.upper()) is not None


def placa_existe(placa: str) -> bool:
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT 1 
            FROM VEICULO
            WHERE PLACA = ?
            """, (placa,)
        )
        
        return cur.fetchone() is not None
    
    
def atualizar_veiculo(placa: str, campos: dict):
    """
    Atualiza apenas os campos enviados no dicionário `campos`.
    Exemplo: {"CONSUMO_MEDIO_KM_L": 15.2}
    """
    if not campos:
        return False

    set_clause = ", ".join([f"{col} = ?" for col in campos.keys()])
    valores = list(campos.values())
    valores.append(placa)

    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE VEICULO
            SET {set_clause}
            WHERE PLACA = ?
            """,
            valores
        )
        conn.commit()

    return True



def atualizar_veiculo(placa: str, campos: dict):
    """
    Atualiza apenas os campos enviados no dicionário `campos`.
    Exemplo: {"CONSUMO_MEDIO_KM_L": 15.2}
    """
    if not campos:
        return False

    set_clause = ", ".join([f"{col} = ?" for col in campos.keys()])
    valores = list(campos.values())
    valores.append(placa)

    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE VEICULO
            SET {set_clause}
            WHERE PLACA = ?
            """,
            valores
        )
        conn.commit()

    return True


def deletar_veiculo(placa: str):
    with sqlite3.connect(Config.DATABASE) as conn:
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM VEICULO 
            WHERE PLACA = ?
        """, (placa,))
        
        conn.commit()

    return f"Veiculo com a Placa {placa} deletado permanentemente!"



def verificar_preventiva_urgente_veiculos():
    """
    Verifica a quilometragem dos veículos.
    Se QUILOMETRAGEM >= 10000 km e o status for ATIVO ou INATIVO,
    altera para PREVENTIVA_URGENTE.
    """

    conn = None
    try:
        conn = sqlite3.connect(Config.DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        
        # -------- Buscar veículos elegíveis para preventiva urgente ------------
        cur.execute("""
            SELECT PLACA, QUILOMETRAGEM, STATUS
            FROM VEICULO
            WHERE QUILOMETRAGEM >= ?
              AND STATUS IN (?, ?)
        """, (
            10000,
            Veiculo_status.ATIVO.value,
            Veiculo_status.INATIVO.value
        ))

        veiculos_para_preventiva = cur.fetchall()

        if not veiculos_para_preventiva:
            print("Nenhum veículo elegível para preventiva urgente.")
            return

        # --------- 2 — Atualizar status para PREVENTIVA_URGENTE -----------------
        for placa, km, status in veiculos_para_preventiva:
            cur.execute("""
                UPDATE VEICULO
                SET STATUS = ?
                WHERE PLACA = ?
            """, (Veiculo_status.PREVENTIVA_URGENTE.value, placa))

            print(f"⚠️ Veículo {placa} com {km} km marcado como PREVENTIVA_URGENTE.")

        conn.commit()
        print("✅ Verificação de preventiva urgente concluída com sucesso.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Erro ao verificar preventiva urgente: {e}")
        raise

    finally:
        if conn:
            conn.close()